from django.urls import path
from . import views

app_name = "materials"

urlpatterns = [
    path("", views.MaterialListView.as_view(), name="list"),
    path("add/", views.MaterialCreateView.as_view(), name="add"),
    path("<slug:slug>/", views.MaterialDetailView.as_view(), name="detail"),
    path("<slug:slug>/edit/", views.MaterialUpdateView.as_view(), name="edit"),
    path("<slug:slug>/delete/", views.MaterialDeleteView.as_view(), name="delete"),
]