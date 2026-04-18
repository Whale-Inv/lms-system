from django.db import models

from config import settings


class Course(models.Model):
    name = models.CharField(
        max_length=150, verbose_name="название", help_text="введите название курса"
    )
    preview = models.ImageField(
        upload_to="courses_preview/", verbose_name="превью", null=True, blank=True
    )
    description = models.TextField(
        verbose_name="описание", help_text="введите описание курса"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="автор",
        default=4,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="цена"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="дата обновления")
    last_notification_sent = models.DateTimeField(
        verbose_name="дата отправки последнего уведомления", null=True, blank=True
    )

    def __str__(self):
        return f"курс: {self.name}"

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"


class Lesson(models.Model):
    name = models.CharField(
        max_length=150, verbose_name="название", help_text="введите название урока"
    )
    description = models.TextField()
    preview = models.ImageField(
        upload_to="lessons_preview", verbose_name="превью", null=True, blank=True
    )
    link = models.CharField(
        max_length=100, verbose_name="ссылка", help_text="добавьте ссылку на видео"
    )
    course = models.ForeignKey(
        Course, related_name="lessons", on_delete=models.CASCADE, verbose_name="курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="автор",
        default=4,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="цена"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="дата обновления")

    def __str__(self):
        return f"урок {self.name}"

    class Meta:
        verbose_name = "урок"
        verbose_name_plural = "уроки"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="пользователь",
        related_name="subscriptions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="курс",
        related_name="subscribers",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата подписки")

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} -> {self.course.title}"
