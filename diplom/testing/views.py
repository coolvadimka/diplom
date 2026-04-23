from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import Test, Question
from .forms import TestForm, QuestionForm


class TeacherOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, "is_teacher", False)


class TestListView(ListView):
    model = Test
    template_name = "testing/test_list.html"
    context_object_name = "tests"
    paginate_by = 10

    def get_queryset(self):
        qs = Test.objects.all().select_related("author")
        user = self.request.user

        if not (user.is_authenticated and getattr(user, "is_teacher", False)):
            qs = qs.filter(is_published=True)

        return qs


class TestDetailView(DetailView):
    model = Test
    template_name = "testing/test_detail.html"
    context_object_name = "test_obj"

    def get_queryset(self):
        qs = Test.objects.all().select_related("author")
        user = self.request.user

        if not (user.is_authenticated and getattr(user, "is_teacher", False)):
            qs = qs.filter(is_published=True)

        return qs


class TestCreateView(LoginRequiredMixin, TeacherOnlyMixin, CreateView):
    model = Test
    form_class = TestForm
    template_name = "testing/test_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TestUpdateView(LoginRequiredMixin, TeacherOnlyMixin, UpdateView):
    model = Test
    form_class = TestForm
    template_name = "testing/test_form.html"

class QuestionCreateView(LoginRequiredMixin, TeacherOnlyMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "testing/question_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.test_obj = get_object_or_404(Test, pk=self.kwargs["test_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.test = self.test_obj
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["test_obj"] = self.test_obj
        return context

    def get_success_url(self):
        return reverse("testing:detail", kwargs={"pk": self.test_obj.pk})


class QuestionUpdateView(LoginRequiredMixin, TeacherOnlyMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = "testing/question_form.html"
    context_object_name = "question_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["test_obj"] = self.object.test
        return context

    def get_success_url(self):
        return reverse("testing:detail", kwargs={"pk": self.object.test.pk})