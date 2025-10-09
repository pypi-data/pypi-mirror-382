from django.contrib.auth.models import BaseUserManager
from django.db import models

from pfx.pfxcore.models import AbstractPFXBaseUser


class User(AbstractPFXBaseUser):
    """Default user for tests."""

    USERNAME_FIELD = 'username'

    username = models.CharField("Username", max_length=150, unique=True)

    objects = BaseUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
