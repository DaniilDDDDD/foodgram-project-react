from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MaxLengthValidator

import base64
import uuid

from .models import Recipes, Tags, Ingredients, RecipeIngredients

User = get_user_model()


class CustomImageField(serializers.Field):
    def to_internal_value(self, data):
        data = data.strip('data:image/png;base64,')
        image_data = base64.b64decode(data)
        filename = uuid.uuid4().hex
        image = open(f'{filename}.png', 'wb')
        image.write(image_data)
        image.close()
        return image


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.filter(author=obj).exists()


def unique_user_validator(value):
    if User.objects.filter(username=value).exists():
        raise serializers.ValidationError('A user with that username already exists')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            MaxLengthValidator(254)
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(150),
            unique_user_validator,
            # RegexValidator(regex='^[\w.@+-]+\z')  #TODO: fix regex
        ]
    )
    first_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(150)
        ]
    )
    last_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(150)
        ]
    )
    password = serializers.CharField(
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(method_name='get_recipes_count')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.filter(author=obj).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit', None)
        if recipes_limit is not None:
            recipes = self.context.get('request').user.recipes.all()[:recipes_limit]
        else:
            recipes = self.context.get('request').user.recipes.all()
        serializer = RecipesReadSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit', None)
        recipes_number = self.context.get('request').user.recipes.all().count()
        if recipes_limit is None or recipes_limit >= recipes_number:
            return recipes_number
        return recipes_limit


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredients
        fields = ('amount', 'ingredient', 'id')


class RecipesCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientsSerializer(many=True, source='recipe_ingredient')
    image = CustomImageField()

    class Meta:
        model = Recipes
        fields = ('ingredients', 'recipe_ingredient', 'tags', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipes.objects.create(author=self.context.get('request').user, **validated_data)
        for elem in ingredients:
            ingredient = elem.pop('ingredient')
            RecipeIngredients.objects.create(recipe=recipe, ingredient=ingredient, **elem)
        return recipe

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)

        instance.recipe_ingredient.all().delete()
        ingredients = validated_data.get('recipe_ingredient')
        for elem in ingredients:
            ingredient = elem.pop('ingredient')
            RecipeIngredients.objects.create(recipe=instance, ingredient=ingredient, **elem)
        return instance


class ListRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(method_name='get_measurement_unit')
    amount = serializers.SerializerMethodField(method_name='get_amount')

    class Meta:
        model = RecipeIngredients
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
    ingredients = ListRecipeIngredientsSerializer(many=True, read_only=True, source='recipe_ingredient')
    tags = TagsSerializer(many=True, read_only=True)
    author = UserReadSerializer(many=False, read_only=True)
    image = serializers.SerializerMethodField(method_name='get_image')
    is_favorited = serializers.SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url

    def get_is_favorited(self, obj):
        return self.context.get('request').user.user_favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return self.context.get('request').user.shop_list.filter(recipe=obj).exists()
