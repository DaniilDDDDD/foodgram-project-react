from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings

from .models import Recipes, Tags, Ingredients

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


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipesListSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    author = UserReadSerializer()

    class Meta:
        model = Recipes
        exclude = ('pub_date',)


class RecipesCreateSerializer(serializers.ModelSerializer):
    # tags = ???
    author = UserReadSerializer()
    is_favourite = serializers.BooleanField(required=False)
    is_in_shopping_cart = serializers.BooleanField(required=False)

    class Meta:
        model = Recipes
        exclude = ('pub_date', )


class RecipesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
