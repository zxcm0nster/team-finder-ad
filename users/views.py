from django.contrib.auth import (
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView

from .forms import (
    CustomPasswordChangeForm,
    CustomUserCreationForm,
    EmailLoginForm,
    ProfileEditForm,
)

PAGINATE_BY_COUNT = 6

User = get_user_model()


class RegisterView(CreateView):
    model = User
    template_name = "users/register.html"
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("projects:list")


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True


def custom_logout(request):
    logout(request)
    return redirect("projects:list")


class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"

    def get_object(self):
        user_id = self.kwargs.get("id")
        return get_object_or_404(User, id=user_id)


class ParticipantListView(ListView):
    model = User
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = PAGINATE_BY_COUNT

    def get_queryset(self):
        return User.objects.order_by("id").select_related("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query_prefix"] = ""
        return context


@login_required
def edit_profile(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)

    if request.user != user_instance:
        return HttpResponseForbidden("Вы не можете редактировать чужой профиль.")

    profile = user_instance.profile

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            user_instance.first_name = profile.name
            user_instance.last_name = profile.surname
            user_instance.save(update_fields=["first_name", "last_name"])
            return redirect("users:user_detail", id=user_instance.id)
    else:
        form = ProfileEditForm(instance=profile)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form, "user": user_instance},
    )


@login_required
def change_password(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)

    if request.user != user_instance:
        return HttpResponseForbidden("Вы не можете изменять пароль другого пользователя.")

    if request.method == "POST":
        form = CustomPasswordChangeForm(user=user_instance, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user_instance)
            return redirect("users:user_detail", id=user_instance.id)
    else:
        form = CustomPasswordChangeForm(user=user_instance)

    return render(request, "users/change_password.html", {"form": form})
