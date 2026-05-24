import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Message(models.Model):
    """Модель Сообщение"""

    subject: models.CharField = models.CharField(
        max_length=150, null=False, blank=False, verbose_name="Тема письма"
    )
    body: models.TextField = models.TextField(
        null=False, blank=False, verbose_name="Тело письма"
    )
    owner: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
    )

    def __str__(self) -> str:
        return f"{self.subject}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["subject"]


class Mailing(models.Model):
    """Модель Рассылка"""

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата и время начала отправки"
    )
    end_time: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата и время окончания отправки"
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created",
        verbose_name="Статус рассылки",
    )
    message: models.ForeignKey = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients: models.ManyToManyField = models.ManyToManyField(
        "clients.Client",
        related_name="mailings",
        verbose_name="Получатели",
    )
    owner: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
    )

    def __str__(self) -> str:
        return f"Рассылка #{self.pk} (Тема: {self.message.subject})"

        def update_status(self) -> None:
            """Динамически проверяет текущее время и обновляет статус напрямую в БД."""
            now = timezone.now()

            if now < self.start_time:
                calculated_status = "created"
            elif self.start_time <= now <= self.end_time:
                calculated_status = "started"
            else:
                calculated_status = "completed"

            if self.status != calculated_status:
                # Обновляем поле в базе данных напрямую в один быстрый SQL-запрос
                Mailing.objects.filter(pk=self.pk).update(status=calculated_status)
                self.status = (
                    calculated_status  # Обновляем статус в текущем объекте в памяти
                )

    def clean(self) -> None:
        super().clean()
        now = timezone.now()

        if self.start_time and self.start_time < now - datetime.timedelta(minutes=1):
            raise ValidationError(
                {"start_time": "Дата и время начала рассылки не могут быть в прошлом."}
            )

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {
                    "end_time": "Дата окончания рассылки должна быть строго позже даты начала."
                }
            )

        def save(self, *args, **kwargs) -> None:
            # Рассчитываем статус только при первом создании или обычном сохранении формы
            now = timezone.now()
            if now < self.start_time:
                self.status = "created"
            elif self.start_time <= now <= self.end_time:
                self.status = "started"
            else:
                self.status = "completed"

            # full_clean вызываем только если мы НЕ обновляем конкретные поля программно
            if not kwargs.get("update_fields"):
                self.full_clean()

            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-start_time"]


class MailingAttempt(models.Model):
    """Модель попытки отправки рассылки"""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    attempt_time: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response: models.TextField = models.TextField(
        blank=True, null=True, verbose_name="Ответ сервера / Текст ошибки"
    )
    mailing: models.ForeignKey = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    def __str__(self) -> str:
        return f"Попытка #{self.pk} для Рассылки #{self.mailing_id} ({self.status})"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ["-attempt_time"]
