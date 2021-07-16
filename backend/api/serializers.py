from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings

from .models import Recipes, Tags, Ingredients, RecipeIngredients

User = get_user_model()


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = tuple(User.REQUIRED_FIELDS) + (
#             settings.USER_ID_FIELD,
#             settings.LOGIN_FIELD,
#         )
#         read_only_fields = (settings.LOGIN_FIELD,)
#
#     def update(self, instance, validated_data):
#         email_field = get_user_email_field_name(User)
#         if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
#             instance_email = get_user_email(instance)
#             if instance_email != validated_data[email_field]:
#                 instance.is_active = False
#                 instance.save(update_fields=["is_active"])
#         return super().update(instance, validated_data)


class RecipesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.get(author=obj).exists()


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(method_name='get_recipes_count')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.get(author=obj).exists()

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
        if recipes_limit >= recipes_number:
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


class CreateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all(), source='ingredient')

    class Meta:
        model = RecipeIngredients
        fields = ('amount', 'ingredient', 'id')


class RecipesCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientsSerializer(many=True, source='recipe_ingredient')

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
    is_favorited = serializers.SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return self.context.get('request').user.user_favorites.get(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return self.context.get('request').user.shop_list.get(recipe=obj).exists()
