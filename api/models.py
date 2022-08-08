from django.db import models
from profiles.models import Profile
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def _create_user(self, username, email, first_name=None, last_name=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have an username')
        if not first_name:
            raise ValueError('Users must have a first_name')
        if not last_name:
            raise ValueError('Users must have a last_name')
        if not email:
            raise ValueError('Users must have an email address')

        user: Profile = Profile(username=username, email=email, first_name=first_name, last_name=last_name,
                                **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email, first_name, last_name, password):
        return self._create_user(username, email, first_name, last_name, password)

    def create_superuser(self, username, email, first_name=None, last_name=None, password=None):
        return self._create_user(username, email, first_name, last_name, password, is_staff=True, is_superuser=True)
