from django.urls import path
from .views import calculator_view, export_excel_view

app_name = "calculator"

urlpatterns = [
    path("", calculator_view, name="index"),
    path("export-excel/", export_excel_view, name="export_excel"),
]