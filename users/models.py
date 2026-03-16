from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

from lms.models import Course, Lesson


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="email")

    phone = models.CharField(max_length=15, verbose_name="телефон", blank=True, null=True,
                             help_text="введите номер телефона")
    city = models.CharField(max_length=35, verbose_name="город", blank=True, null=True, help_text="введите город")
    avatar = models.ImageField(upload_to="avatars/", verbose_name="аватар", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


class Payments(models.Model):
    METHOD_CHOICES = [('cash', 'наличные'), ('transfer', 'перевод на счет'),]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", verbose_name="пользователь")
    payment_date = models.DateTimeField(verbose_name="дата оплаты", auto_now_add=True)
    paid_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payments_course", verbose_name="оплаченный курс", blank=True, null=True)
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="payments_lesson", verbose_name="оплаченный урок", blank=True, null=True)
    payment_amount = models.DecimalField(verbose_name="сумма оплаты", max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='transfer')

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'

    def __str__(self):
        return f'{self.user} - {self.payment_amount}'

    def clean(self):
        """Проверка, что указан либо курс, либо урок, но не оба и не ни одного"""
        if self.paid_course and self.paid_lesson:
            raise ValidationError("Платеж может быть только за курс ИЛИ только за урок")
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError("Укажите оплаченный курс или оплаченный урок")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)