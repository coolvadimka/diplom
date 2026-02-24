from django.db import models
import json


class CalculationHistory(models.Model):
    """Модель для сохранения истории вычислений в SQLite"""

    expression = models.CharField(
        max_length=255,
        verbose_name="Логическое выражение",
        db_index=True  # Добавляем индекс для быстрого поиска
    )

    k_value = models.IntegerField(
        default=2,
        verbose_name="Значность логики (k)",
        db_index=True
    )

    # Для SQLite используем TextField и будем хранить JSON как строку
    result_data = models.TextField(
        verbose_name="Результаты вычислений",
        default='{}',
        help_text="Хранится в формате JSON"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        db_index=True
    )

    # Дополнительные поля для удобства
    input_type = models.CharField(
        max_length=20,
        choices=[
            ('expression', 'Выражение'),
            ('vector', 'Вектор функции'),
        ],
        default='expression',
        verbose_name="Тип ввода"
    )

    variables = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Переменные"
    )

    class Meta:
        verbose_name = "История вычислений"
        verbose_name_plural = "История вычислений"
        ordering = ['-created_at']

        # Добавляем составной индекс для частых запросов
        indexes = [
            models.Index(fields=['-created_at', 'k_value']),
        ]

    def __str__(self):
        return f"{self.expression} (k={self.k_value}) - {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    def set_result_data(self, data):
        """Сериализация данных перед сохранением"""
        self.result_data = json.dumps(data, ensure_ascii=False)

    def get_result_data(self):
        """Десериализация данных при чтении"""
        try:
            return json.loads(self.result_data) if self.result_data else {}
        except json.JSONDecodeError:
            return {}

    def get_short_preview(self):
        """Получить краткий предпросмотр результата"""
        data = self.get_result_data()
        preview = []

        if 'sdnf' in data:
            preview.append('СДНФ')
        if 'sknf' in data:
            preview.append('СКНФ')
        if 'truth_table' in data:
            preview.append('Таблица')

        return ', '.join(preview) if preview else 'Нет данных'