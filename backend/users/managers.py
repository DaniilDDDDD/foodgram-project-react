from django.utils.crypto import get_random_string
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(
            self,
            username=None,
            email=None,
            password=None,
            **extra_fields
    ):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        if username is None:
            username = get_random_string(10, 'abcdefghjkmnpqrstuvwxyz'
                                             'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                             '23456789')
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        confirmation_code = uuid.uuid4()
        user.confirmation_code = confirmation_code
        if 'role' not in extra_fields:
            user.role = 'user'
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            username,
            email=None,
            password=None,
            **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username=username, email=email,
                                password=password, **extra_fields)