from django.urls import path
from . import views

app_name = "testing"

urlpatterns = [
    path("", views.TestListView.as_view(), name="list"),
    path("create/", views.TestCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TestDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.TestUpdateView.as_view(), name="edit"),

    path("<int:test_pk>/questions/add/", views.QuestionCreateView.as_view(), name="question_add"),
    path("questions/<int:pk>/edit/", views.QuestionUpdateView.as_view(), name="question_edit"),
]