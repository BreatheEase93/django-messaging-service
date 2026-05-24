from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUser(AbstractUser):
    """Стандартный класс пользователя"""

    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    verification_token: models.CharField = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Токен верификации"
    )
    country: models.CharField = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Страна"
    )
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
