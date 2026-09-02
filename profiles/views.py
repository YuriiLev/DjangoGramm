from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ProfileForm
from .models import Profile


def get_acting_profile(request):
    profiles = request.user.profiles.all()
    acting_id = request.GET.get("as")
    if acting_id:
        chosen = profiles.filter(id=acting_id).first()
        if chosen:
            return chosen
    return profiles.first()


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "profiles/profile_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        return self.request.user.profiles.all()


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profiles/profile_detail.html"
    context_object_name = "profile"

    def get_queryset(self):
        return Profile.objects.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_profiles"] = self.request.user.profiles.all()
        context["acting"] = get_acting_profile(self.request)
        return context


class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_form.html"
    success_url = reverse_lazy("profile-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Profile"
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_form.html"

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("profile-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Profile"
        return context


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = "profiles/profile_confirm_delete.html"
    success_url = reverse_lazy("profile-list")

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
