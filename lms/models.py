from django.db import models

from config import settings


class Course(models.Model):
    name = models.CharField(max_length=150, verbose_name="название", help_text="введите название курса")
    preview = models.ImageField(upload_to="courses_preview/", verbose_name="превью")
    description = models.TextField(verbose_name="описание", help_text="введите описание курса")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="автор", default=4)

    def __str__(self):
        return f"курс: {self.name}"

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"


class Lesson(models.Model):
    name = models.CharField(max_length=150, verbose_name="название", help_text="введите название урока")
    description = models.TextField()
    preview = models.ImageField(upload_to="lessons_preview", verbose_name="превью")
    link = models.CharField(max_length=100, verbose_name="ссылка", help_text="добавьте ссылку на видео")
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE, verbose_name="курс")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="автор", default=4)

    def __str__(self):
        return f"урок {self.name}"

    class Meta:
        verbose_name = "урок"
        verbose_name_plural = "уроки"