import smtplib

from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt


def send_mailing(mailing: Mailing) -> tuple[bool, str]:
    """Выполняет отправку конкретной рассылки всем связанным получателям."""
    now = timezone.now()

    # Шаг 1. Инициация и проверка времени
    # Обновляем статус рассылки на актуальный перед проверкой
    mailing.update_status()

    if not (mailing.start_time <= now <= mailing.end_time):
        return False, "Ошибка: текущее время не входит в разрешенный интервал рассылки."

    if mailing.status != "started":
        return (
            False,
            f"Ошибка: рассылка не может быть запущена в статусе '{mailing.get_status_display()}'.",
        )

    recipients = mailing.recipients.all()
    if not recipients:
        return False, "Предупреждение: у рассылки нет ни одного получателя."

    recipient_emails = [client.email for client in recipients]

    # Шаг 3. Отправка писем через send_mail() с логированием
    try:
        # Django send_mail отправляет письмо списку адресатов
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=None,
            recipient_list=recipient_emails,
            fail_silently=False,
        )

        # Если всё прошло успешно, создаем лог 'success'
        MailingAttempt.objects.create(
            status="success",
            server_response="Письма успешно отправлены всем получателям.",
            mailing=mailing,
        )
        return True, "Рассылка успешно выполнена."

    except smtplib.SMTPException as e:
        # Перехватываем специфичные ошибки почтового сервера (неверный пароль приложения, блокировка)
        error_message = f"Ошибка SMTP сервера: {str(e)}"
        MailingAttempt.objects.create(
            status="failed", server_response=error_message, mailing=mailing
        )
        return False, error_message

    except Exception as e:
        # Перехватываем любые другие неожиданные ошибки (например, упал интернет)
        error_message = f"Непредвиденная ошибка при отправке: {str(e)}"
        MailingAttempt.objects.create(
            status="failed", server_response=error_message, mailing=mailing
        )
        return False, error_message
