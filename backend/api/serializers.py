from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MaxLengthValidator
from django.core.files.uploadedfile import SimpleUploadedFile

import base64
import uuid
import tempfile
import os

from .models import Recipe, Tag, Ingredient, RecipeIngredient
from backend.settings import MEDIA_ROOT

User = get_user_model()


class CustomImageField(serializers.ImageField):

    def to_internal_value(self, data):
        data = data.strip('data:image/')
        index = data.find(';')
        content_type = data[:index]
        data = data[index + 8:]
        image_data = base64.b64decode(data)
        filename = uuid.uuid4().hex
        with tempfile.TemporaryFile() as image:
            image.write(image_data)
            image.seek(0)
            file = SimpleUploadedFile(
                name=f'{filename}.{content_type}',
                content=image.read(),
                content_type=f'image/{content_type}'
            )
        return super().to_internal_value(file)


class RecipesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return self.context.get('request').user.follower.filter(author=obj).exists()


def unique_username_validator(value):
    if User.objects.filter(username=value).exists():
        raise serializers.ValidationError('A user with that username already exists.')


def unique_email_validator(value):
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError('A user with that email already exists.')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            MaxLengthValidator(254),
            unique_email_validator
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(150),
            unique_username_validator,
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
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.filter(author=obj).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit', None)
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()

        serializer = RecipesReadSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit', None)
        recipes_number = self.context.get('request').user.recipes.all().count()
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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), required=True)
    amount = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RecipesCreateSerializer(serializers.Serializer):
    ingredients = CreateRecipeIngredientsSerializer(many=True, required=True)
    image = CustomImageField(required=True)
    text = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=True)
    cooking_time = serializers.IntegerField(required=True)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request').user, **validated_data)
        recipe.tags.set(tags)
        recipe.save()
        for elem in ingredients:
            ingredient = elem.pop('id')
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, **elem)
        return recipe

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        if 'tags' in validated_data:
            instance.tags.set(validated_data['tags'])

        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.name = validated_data.get('name', instance.name)
        if 'image' in validated_data:
            os.remove(MEDIA_ROOT + '/' + str(instance.image))
            instance.image = validated_data['image']
        instance.save()

        if 'ingredients' in validated_data:
            print('in ingredients:')
            print('ingredients' in validated_data)
            instance.recipe_ingredient.all().delete()
            ingredients = validated_data.get('ingredients')
            for elem in ingredients:
                ingredient = elem.pop('id')
                RecipeIngredient.objects.create(recipe=instance, ingredient=ingredient, **elem)
        return instance


class ListRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(method_name='get_measurement_unit')
    amount = serializers.SerializerMethodField(method_name='get_amount')

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
    ingredients = ListRecipeIngredientsSerializer(many=True, read_only=True, source='recipe_ingredient')
    tags = TagsSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True, context='get_context')
    image = serializers.SerializerMethodField(method_name='get_image')
    is_favorited = serializers.SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(method_name='get_is_in_shopping_cart', )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_context(self):
        return {'request': self.context}

    def get_image(self, obj):
        if self.context.get('request').is_secure():
            return 'https://' + str(self.context.get('request').get_host()) + str(obj.image.url)
        return 'http://' + str(self.context.get('request').get_host()) + str(obj.image.url)

    def get_is_favorited(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return self.context.get('request').user.user_favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return self.context.get('request').user.shop_list.filter(recipe=obj).exists()
