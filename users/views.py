from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, ProfileEditForm, CustomPasswordChangeForm

User = get_user_model()

class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    # После успешной регистрации перенаправляем на страницу входа
    success_url = reverse_lazy('users:login')

def custom_logout(request):
    logout(request)
    return redirect('users:login')

class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'
    
    def get_object(self):
        # Получаем id из URL
        user_id = self.kwargs.get('id')
        # Ищем пользователя или выдаём 404, если такого нет
        return get_object_or_404(User, id=user_id)

class ParticipantListView(ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    ordering = ['id']
    paginate_by = 6 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query_prefix'] = "" 
        return context

@login_required
def edit_profile(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    
    # Защита безопасности: пользователь может редактировать только свой профиль
    if request.user != user_instance:
        return HttpResponseForbidden("Вы не можете редактировать чужой профиль.")

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user_instance)
        if form.is_valid():
            form.save()
            # Перенаправляем на страницу профиля через именованный маршрут
            return redirect('users:user_detail', id=user_instance.id)
    else:
        form = ProfileEditForm(instance=user_instance)

    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def change_password(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    
    # Защита: менять пароль можно только самому себе
    if request.user != user_instance:
        return HttpResponseForbidden("Вы не можете изменять пароль другого пользователя.")

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user_instance, data=request.POST)
        if form.is_valid():
            form.save()
            # Обновляем сессию, чтобы пользователя не выкинуло из системы
            update_session_auth_hash(request, user_instance)
            # Перенаправляем на страницу профиля через именованный маршрут
            return redirect('users:user_detail', id=user_instance.id)
    else:
        form = CustomPasswordChangeForm(user=user_instance)

    return render(request, 'users/change_password.html', {'form': form})
