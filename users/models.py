from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

from lms.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="email")

    phone = models.CharField(max_length=15, verbose_name="телефон", blank=True, null=True,
                             help_text="введите номер телефона")
    city = models.CharField(max_length=35, verbose_name="город", blank=True, null=True, help_text="введите город")
    avatar = models.ImageField(upload_to="avatars/", verbose_name="аватар", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


class Payments(models.Model):
    METHOD_CHOICES = [
        ('cash', 'наличные'),
        ('transfer', 'перевод на счет'),
        ('stripe', 'Stripe'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('succeeded', 'Успешно оплачен'),
        ('canceled', 'Отменен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возвращен'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="пользователь"
    )
    payment_date = models.DateTimeField(
        verbose_name="дата оплаты",
        auto_now_add=True
    )
    paid_course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name="payments_course",
        verbose_name="оплаченный курс",
        blank=True,
        null=True
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="payments_lesson",
        verbose_name="оплаченный урок",
        blank=True,
        null=True
    )
    payment_amount = models.DecimalField(
        verbose_name="сумма оплаты",
        max_digits=10,
        decimal_places=2
    )
    payment_method = models.CharField(
        max_length=50,
        choices=METHOD_CHOICES,
        default='transfer'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="статус платежа"
    )

    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID продукта в Stripe"
    )

    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID цены в Stripe"
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии в Stripe"
    )

    stripe_checkout_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="ссылка на оплату Stripe"
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID PaymentIntent в Stripe"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="дополнительные данные"
    )

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'

    def __str__(self):
        item = self.paid_course or self.paid_lesson
        return f'{self.user.email} - {item} - {self.payment_amount} '

    def clean(self):
        """Проверка, что указан либо курс, либо урок, но не оба и не ни одного"""
        if self.paid_course and self.paid_lesson:
            raise ValidationError("Платеж может быть только за курс ИЛИ только за урок")
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError("Укажите оплаченный курс или оплаченный урок")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def product_name(self):
        """ Название товара для Stripe """
        item = self.paid_course or self.paid_lesson
        return item.name

    @property
    def product_description(self):
        """ Описание товара для Stripe """
        item = self.paid_course or self.paid_lesson
        return item.description

    @property
    def is_paid(self):
        """ Проверка, оплачен ли платеж """
        return self.status == 'succeeded'