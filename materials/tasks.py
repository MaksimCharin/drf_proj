from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from materials.models import Course, Subscription

@shared_task
def send_course_update_notification(course_id):
    """Отправляет уведомление об обновлении курса всем подписанным пользователям"""
    try:
        course = Course.objects.get(id=course_id)
        subscribed_users_emails = Subscription.objects.filter(course=course).values_list('user__email', flat=True)

        if not subscribed_users_emails:
            print(f"Нет подписчиков для курса '{course.name}'. Письмо не отправлено.")
            return

        subject = f"Обновление курса: '{course.name}'"
        message = (
            f"Привет!\n\n"
            f"Курс '{course.name}' был обновлен.\n"
            f"Описание: {course.description or 'Нет описания.'}\n\n"
            f"Заходите на платформу, чтобы узнать подробности!\n\n"
            f"С уважением,\n"
            f"Команда образовательной платформы"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = list(subscribed_users_emails)

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"Уведомление об обновлении курса '{course.name}' отправлено {len(recipient_list)} подписчикам.")

    except Course.DoesNotExist:
        print(f"Курс с ID {course_id} не найден.")
    except Exception as e:
        print(f"Ошибка при отправке уведомления об обновлении курса: {e}")