from django import forms
from .models import Material


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["title", "short_description", "content", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "maxlength": 120,
                "placeholder": "Введите название материала"
            }),
            "short_description": forms.TextInput(attrs={
                "class": "form-input",
                "maxlength": 300,
                "placeholder": "Краткое описание (до 300 символов)"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 10,
                "placeholder": "Основной текст материала"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_published"].help_text = (
            "Если не отмечено — материал виден только преподавателям."
        )

    # Валидация title
    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()

        if len(title) < 3:
            raise forms.ValidationError(
                "Название должно содержать минимум 3 символа."
            )

        if len(title) > 120:
            raise forms.ValidationError(
                "Название не должно превышать 120 символов."
            )

        return title

    # Валидация short_description
    def clean_short_description(self):
        short_description = (self.cleaned_data.get("short_description") or "").strip()

        if len(short_description) < 10:
            raise forms.ValidationError(
                "Краткое описание должно содержать минимум 10 символов."
            )

        if len(short_description) > 300:
            raise forms.ValidationError(
                "Краткое описание не должно превышать 300 символов."
            )

        return short_description