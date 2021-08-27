import os

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinValueValidator

from .models import Recipe, Tag, Ingredient, RecipeIngredient
from backend.settings import MEDIA_ROOT
from .fields import CustomImageField
from .validators import unique_username_validator, unique_email_validator

User = get_user_model()


class RecipesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return self.context.get('request').user.follower.filter(
            author=obj
        ).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            MaxLengthValidator(
                254,
                message='Ensure email has at most 254 characters.'
            ),
            unique_email_validator
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                150,
                message='Ensure username value has at most 150 characters.'
            ),
            unique_username_validator
        ]
    )
    first_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                150,
                message='Ensure first_name has at most 150 characters.'
            )
        ]
    )
    last_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                150,
                message='Ensure last_name has at most 150 characters.'
            )
        ]
    )
    password = serializers.CharField(
        required=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'password'
        )


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.filter(
            author=obj
        ).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').GET.get(
            'recipes_limit',
            None
        )
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()

        serializer = RecipesReadSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        recipes_limit = self.context.get('request').GET.get(
            'recipes_limit',
            None
        )
        recipes_number = self.context.get(
            'request'
        ).user.recipes.all().count()
        if recipes_limit is None or int(recipes_limit) >= recipes_number:
            return recipes_number
        return recipes_limit


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class CreateRecipeIngredientsSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(
        required=True
    )


class RecipesCreateSerializer(serializers.Serializer):
    ingredients = CreateRecipeIngredientsSerializer(
        many=True,
        required=True
    )
    image = CustomImageField(required=True)
    text = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    cooking_time = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(
                1,
                message='Ensure cooking_time is greater than or equal to 1.'
            )
        ]
    )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Ingredients field may not be blank.'
            )

        validation_errors = []

        result = {}
        for item in value:
            if item['amount'] < 1:
                validation_errors.append(
                    f'Ensure amount of {item["id"].name} '
                    f'is greater than or equal to 1.'
                )

            if item['id'] in result:
                result[item['id']] += item['amount']
            else:
                result[item['id']] = item['amount']

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        validated_data = []
        for key in result:
            validated_data.append(
                {
                    'id': key,
                    'amount': result[key]
                }
            )

        return validated_data

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Tags field may not be blank.')
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get(
            'request'
        ).user, **validated_data)
        recipe.tags.set(tags)
        recipe.save()
        for elem in ingredients:
            ingredient = elem.pop('id')
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                **elem
            )
        return recipe

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        if 'tags' in validated_data:
            instance.tags.set(validated_data['tags'])

        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.name = validated_data.get('name', instance.name)
        if 'image' in validated_data:
            try:
                os.remove(MEDIA_ROOT + '/' + str(instance.image))
            except PermissionError:
                pass
            instance.image = validated_data['image']
        instance.save()

        if 'ingredients' in validated_data:
            instance.recipe_ingredients.all().delete()
            ingredients = validated_data.get('ingredients')
            for elem in ingredients:
                ingredient = elem.pop('id')
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    **elem
                )
        return instance


class ListRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(
        method_name='get_id'
    )
    name = serializers.SerializerMethodField(
        method_name='get_name'
    )
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )
    amount = serializers.SerializerMethodField(
        method_name='get_amount'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    def get_amount(self, obj):
        return obj.amount


class RecipesListSerializer(serializers.ModelSerializer):
    ingredients = ListRecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    tags = TagsSerializer(
        many=True,
        read_only=True
    )
    author = UserReadSerializer(
        read_only=True,
        context='get_context'
    )
    image = serializers.SerializerMethodField(
        method_name='get_image'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text',
            'cooking_time'
        )

    def get_context(self):
        return {'request': self.context}

    def get_image(self, obj):
        if self.context.get('request').is_secure():
            return 'https://' + str(self.context.get(
                'request').get_host()) + str(obj.image.url)
        return 'http://' + str(self.context.get(
            'request').get_host()) + str(obj.image.url)

    def get_is_favorited(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return self.context.get('request').user.user_favorites.filter(
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return self.context.get('request').user.shop_list.filter(
            recipe=obj
        ).exists()
