from django.conf import settings
from django.db import models


class Client(models.Model):
    """Модель получателя рассылки"""

    email = models.EmailField(
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        verbose_name="Электронная почта",
    )
    name = models.CharField(
        max_length=150, null=False, blank=False, verbose_name="Ф. И. О."
    )
    commit = models.TextField(null=True, blank=True, verbose_name="Комментарий")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        ordering = ["name"]
