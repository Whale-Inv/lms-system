from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import Payments
from lms.models import Subscription
from users.models import User
from django.db import models


@shared_task
def activate_subscription(payment_id):

    payment = Payments.objects.get(id=payment_id)

    # Если оплачен курс
    if payment.paid_course and payment.status == "succeeded":
        # Создаем подписку
        Subscription.objects.get_or_create(
            user=payment.user, course=payment.paid_course
        )


@shared_task
def user_last_login():
    """
    Метод проверяет пользователей по дате последнего входа.
    Если пользователь не заходил более месяца, то блокирует его.
    """
    month_ago = timezone.now() - timedelta(days=30)

    count = (
        User.objects.filter(
            is_active=True,
            is_superuser=False,
        )
        .filter(models.Q(last_login__isnull=True) | models.Q(last_login__lte=month_ago))
        .update(is_active=False)
    )

    return f"Заблокировано пользователей: {count}"
