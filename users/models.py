from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="email")

    phone = models.CharField(max_length=15, verbose_name="телефон", blank=True, null=True, help_text="введите номер телефона")
    city = models.CharField(max_length=35, verbose_name="город", blank=True, null=True, help_text="введите город")
    avatar = models.ImageField(upload_to="avatars/", verbose_name="аватар")
