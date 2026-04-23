from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Material
from .forms import MaterialForm


class TeacherOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, "is_teacher", False)

class MaterialListView(ListView):
    model = Material
    template_name = "materials/material_list.html"
    context_object_name = "materials"
    paginate_by = 10

    def get_queryset(self):
        qs = Material.objects.all()
        user = self.request.user
        if not (user.is_authenticated and getattr(user, "is_teacher", False)):
            qs = qs.filter(is_published=True)
        return qs

class MaterialDetailView(DetailView):
    model = Material
    template_name = "materials/material_detail.html"
    context_object_name = "material"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        qs = Material.objects.all()
        user = self.request.user
        if not (user.is_authenticated and getattr(user, "is_teacher", False)):
            qs = qs.filter(is_published=True)
        return qs

class MaterialCreateView(LoginRequiredMixin, TeacherOnlyMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class MaterialUpdateView(LoginRequiredMixin, TeacherOnlyMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

class MaterialDeleteView(LoginRequiredMixin, TeacherOnlyMixin, DeleteView):
    model = Material
    template_name = "materials/material_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("materials:list")

