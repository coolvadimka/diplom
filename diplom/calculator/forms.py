from django import forms


class CalculatorForm(forms.Form):
    k = forms.IntegerField(
        label="k",
        min_value=2,
        max_value=10,
        initial=3,
        widget=forms.NumberInput(attrs={
            "class": "form-control"
        })
    )

    n = forms.IntegerField(
        label="n",
        min_value=1,
        max_value=5,
        initial=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control"
        })
    )

    expression = forms.CharField(
        label="Формула",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите формулу"
        })
    )