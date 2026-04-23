from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Test(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название тестирования")
    description = models.TextField(blank=True, verbose_name="Описание")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tests",
        verbose_name="Преподаватель",
    )

    is_required = models.BooleanField(default=False, verbose_name="Обязательное")
    allow_back_navigation = models.BooleanField(
        default=True,
        verbose_name="Разрешить возврат к предыдущим вопросам",
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")

    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True,
                                                     verbose_name="Ограничение по времени (в минутах)", )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Тестирование"
        verbose_name_plural = "Тестирования"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("testing:detail", kwargs={"pk": self.pk})


class Question(models.Model):
    TYPE_SINGLE_CHOICE = "single_choice"
    TYPE_NUMBER = "number"

    QUESTION_TYPE_CHOICES = [
        (TYPE_SINGLE_CHOICE, "Один вариант ответа"),
        (TYPE_NUMBER, "Числовой ответ"),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Тестирование",
    )
    text = models.TextField(verbose_name="Текст вопроса")
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        verbose_name="Тип вопроса",
    )
    order = models.PositiveIntegerField(verbose_name="Порядок вопроса")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["order"]
        unique_together = ("test", "order")

    def __str__(self):
        return f"{self.test.title} — вопрос {self.order}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Вопрос",
    )
    text = models.CharField(max_length=300, verbose_name="Текст варианта")
    order = models.PositiveIntegerField(default=1, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        ordering = ["order"]

    def __str__(self):
        return self.text


class TestAttempt(models.Model):
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, "В процессе"),
        (STATUS_COMPLETED, "Завершено"),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Тестирование",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_attempts",
        verbose_name="Студент",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_IN_PROGRESS,
        verbose_name="Статус",
    )

    current_question_order = models.PositiveIntegerField(
        default=1,
        verbose_name="Текущий номер вопроса",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Начато")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершено",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время окончания попытки",
    )

    class Meta:
        verbose_name = "Попытка прохождения"
        verbose_name_plural = "Попытки прохождения"
        ordering = ["-started_at"]
        unique_together = ("test", "student")

    def __str__(self):
        return f"{self.student} / {self.test}"

    def mark_completed(self):
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Попытка",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="student_answers",
        verbose_name="Вопрос",
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Выбранный вариант",
    )
    numeric_answer = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Числовой ответ",
    )
    answered_at = models.DateTimeField(auto_now=True, verbose_name="Дата ответа")

    class Meta:
        verbose_name = "Ответ студента"
        verbose_name_plural = "Ответы студентов"
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"Ответ: {self.attempt} / {self.question}"