import smtplib

from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt


def send_mailing(mailing: Mailing) -> tuple[bool, str]:
    """
    Выполняет отправку рассылки получателям с batch-сохранением логов попыток.
    """
    now = timezone.now()

    # Валидация входных данных по времени (Критерий ТЗ)
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

    # Список, в который мы соберем объекты логов для batch-сохранения
    attempts_to_create = []

    try:
        # Отправка писем
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=None,
            recipient_list=recipient_emails,
            fail_silently=False,
        )

        # Для каждого получателя формируем лог успеха в памяти (Критерий ТЗ)
        for client in recipients:
            attempts_to_create.append(
                MailingAttempt(
                    status="success",
                    server_response=f"Письмо успешно отправлено на адрес {client.email}.",
                    mailing=mailing,
                )
            )

        # ЗАПИСЬ ЧЕРЕЗ BATCH (bulk_create) — отправляем все логи одним SQL-запросом
        MailingAttempt.objects.bulk_create(attempts_to_create)
        return True, "Рассылка успешно выполнена."

    except smtplib.SMTPException as e:
        error_message = f"Ошибка SMTP сервера: {str(e)}"

        # В случае ошибки также формируем batch логов для каждого получателя
        for client in recipients:
            attempts_to_create.append(
                MailingAttempt(
                    status="failed",
                    server_response=f"Сбой доставки на {client.email}. {error_message}",
                    mailing=mailing,
                )
            )

        MailingAttempt.objects.bulk_create(attempts_to_create)
        return False, error_message

    except Exception as e:
        error_message = f"Непредвиденная ошибка: {str(e)}"
        for client in recipients:
            attempts_to_create.append(
                MailingAttempt(
                    status="failed", server_response=error_message, mailing=mailing
                )
            )
        MailingAttempt.objects.bulk_create(attempts_to_create)
        return False, error_message
