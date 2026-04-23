import re

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Material(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, max_length=50)

    short_description = models.CharField(max_length=300, verbose_name="Краткое описание")
    content = models.TextField(verbose_name="Текст материала")


    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materials",
        verbose_name="Автор",
    )

    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Учебный материал"
        verbose_name_plural = "Учебные материалы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # дата публикации
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        else:
            self.published_at = None
        if not self.slug:
            last = (
                Material.objects
                .filter(slug__regex=r"^material-\d+$")
                .order_by("-id")
                .first()
            )

            next_num = 1
            if last and last.slug:
                m = re.match(r"^material-(\d+)$", last.slug)
                if m:
                    next_num = int(m.group(1)) + 1

            self.slug = f"material-{next_num}"
            while Material.objects.filter(slug=self.slug).exists():
                next_num += 1
                self.slug = f"material-{next_num}"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("materials:detail", kwargs={"slug": self.slug})