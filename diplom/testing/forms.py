from django import forms
from .models import Test, Question


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = [
            "title",
            "description",
            "is_required",
            "allow_back_navigation",
            "time_limit_minutes",
            "is_published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "maxlength": 200,
                "placeholder": "Введите название тестирования"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 6,
                "placeholder": "Введите описание тестирования"
            }),
            "time_limit_minutes": forms.NumberInput(attrs={
                "class": "form-input",
                "min": 1,
                "placeholder": "Например: 30"
            }),
        }

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()

        if len(title) < 3:
            raise forms.ValidationError("Название должно содержать минимум 3 символа.")

        if len(title) > 200:
            raise forms.ValidationError("Название не должно превышать 200 символов.")

        return title

    def clean_time_limit_minutes(self):
        value = self.cleaned_data.get("time_limit_minutes")

        if value is not None and value < 1:
            raise forms.ValidationError("Лимит времени должен быть больше 0 минут.")

        return value


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "question_type", "order"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 4,
                "placeholder": "Введите текст вопроса"
            }),
            "question_type": forms.Select(attrs={
                "class": "form-input"
            }),
            "order": forms.NumberInput(attrs={
                "class": "form-input",
                "min": 1,
                "placeholder": "Например: 1"
            }),
        }

    def clean_text(self):
        text = (self.cleaned_data.get("text") or "").strip()

        if len(text) < 3:
            raise forms.ValidationError("Текст вопроса должен содержать минимум 3 символа.")

        return text

    def clean_order(self):
        order = self.cleaned_data.get("order")

        if order is None or order < 1:
            raise forms.ValidationError("Порядок вопроса должен быть не меньше 1.")

        return order