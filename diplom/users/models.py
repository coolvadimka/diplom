from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    photo = models.ImageField(upload_to="users/%Y/%m/%d/", null=True, blank=True, verbose_name="Фотография")
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")
    group = models.CharField(max_length=50, verbose_name="Учебная группа")
