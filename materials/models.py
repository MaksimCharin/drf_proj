from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name="название курса")
    preview = models.ImageField(
        upload_to="materials/course_previews/",
        verbose_name="превью",
        blank=True,
        null=True,
    )
    description = models.TextField(verbose_name="описание курса", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='владелец', null=True, blank=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="курс"
    )
    name = models.CharField(max_length=255, verbose_name="название урока")
    description = models.TextField(verbose_name="описание урока", blank=True, null=True)
    preview = models.ImageField(
        upload_to="materials/lesson_previews/",
        verbose_name="превью",
        blank=True,
        null=True,
    )
    video_link = models.URLField(verbose_name="ссылка на видео", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='владелец', null=True, blank=True)


    def __str__(self):
        return f"{self.name} ({self.course.name})"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
