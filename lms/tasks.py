from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from lms.models import Course, Subscription
from django.core.mail import send_mail
from django.conf import settings


def should_send_notification(course):
    """Проверяет, нужно ли отправлять уведомление"""
    now = timezone.now()
    four_hours_ago = now - timedelta(hours=4)

    # Проверяем, что курс обновлялся, и последнее уведомление было >4 часов назад
    if course.updated_at < four_hours_ago:
        if not course.last_notification_sent:
            return True
        return course.last_notification_sent < four_hours_ago
    return False


@shared_task
def send_update_email(user_email, course_name, course_id):
    """Отправка письма пользователю"""
    subject = f"Обновление курса: {course_name}"
    message = f"""Здравствуйте!

Курс "{course_name}" был обновлен.

Перейти к курсу: {settings.SITE_URL}/courses/{course_id}/

С уважением,
Команда LMS"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task
def send_course_update_notifications():
    """Асинхронная рассылка уведомлений об обновлении курсов"""

    now = timezone.now()
    four_hours_ago = now - timedelta(hours=4)

    # Находим курсы, которые обновлялись больше 4 часов назад и в них есть подписчики
    courses = Course.objects.filter(
        updated_at__lte=four_hours_ago, subscribers__isnull=False
    ).distinct()

    for course in courses:
        # 👇 Используем функцию проверки
        if should_send_notification(course):
            subscribers = Subscription.objects.filter(course=course)

            for subscription in subscribers:
                send_update_email.delay(
                    user_email=subscription.user.email,
                    course_name=course.name,
                    course_id=course.id,
                )

            # После отправки обновляем время
            course.last_notification_sent = now
            course.save()
