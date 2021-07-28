from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


def unique_username_validator(value):
    if User.objects.filter(username=value).exists():
        raise serializers.ValidationError(
            'A user with that username already exists.'
        )


def unique_email_validator(value):
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError(
            'A user with that email already exists.'
        )
