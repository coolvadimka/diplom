from django.contrib import admin
from .models import Test, Question, Choice, TestAttempt, StudentAnswer


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "is_required", "allow_back_navigation", "is_published", "time_limit_minutes", "created_at")
    list_filter = ("is_required", "allow_back_navigation", "is_published", "created_at")
    search_fields = ("title", "description", "author__username")



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "test", "order", "question_type")
    list_filter = ("question_type", "test")
    search_fields = ("text", "test__title")
    ordering = ("test", "order")


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "order", "text")
    list_filter = ("question__test",)
    search_fields = ("text", "question__text")


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "test", "student", "status", "current_question_order", "started_at",  "expires_at", "completed_at")
    list_filter = ("status", "test")
    search_fields = ("student__username", "test__title")


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt", "question", "selected_choice", "numeric_answer", "answered_at")
    list_filter = ("question__test",)
    search_fields = ("attempt__student__username", "question__text")