from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Преподаватель"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT,
        verbose_name="Роль"
    )
    photo = models.ImageField(upload_to="users/%Y/%m/%d/", null=True, blank=True, verbose_name="Фотография")
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")
    group = models.CharField(max_length=50, verbose_name="Учебная группа")

    @property
    def is_teacher(self) -> bool:
        return self.role == self.Roles.TEACHER

