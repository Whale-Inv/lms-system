from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from lms.models import Course, Lesson
from users.models import User, Payments


class Command(BaseCommand):
    help = "Добавление тестовых платежей в БД"

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(
            email="test1@mail.ru", phone="+79876541232", city="Москва"
        )
        user.set_password("test123")
        user.save()

        payment_data = timezone.now() - timedelta(days=1)
        course = Course.objects.get(id=4)
        lesson = Lesson.objects.get(id=2)

        payments = [
            {
                "user": user,
                "payment_date": payment_data,
                "paid_course": course,
                "paid_lesson": None,
                "payment_amount": 10000,
                "payment_method": "transfer",
            },
            {
                "user": user,
                "payment_date": timezone.now() - timedelta(days=2),
                "paid_course": None,
                "paid_lesson": lesson,
                "payment_amount": 5000,
                "payment_method": "cash",
            },
        ]
        for payment_data in payments:
            payment, created = Payments.objects.get_or_create(**payment_data)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"successfully added payment: {payment.payment_amount}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"payment already exists: {payment.payment_amount}"
                    )
                )
