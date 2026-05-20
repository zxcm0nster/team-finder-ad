from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.contrib.auth import get_user_model

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
    # Указываем модель, из которой будем брать данные
    model = User
    # Указываем путь к твоему шаблону
    template_name = 'users/user-details.html'
    # Указываем, под каким именем объект будет доступен в HTML (ты используешь {{ user.name }})
    context_object_name = 'user'
    
    # DetailView по умолчанию ищет объект по pk (primary key).
    def get_object(self):
        # Получаем id из URL
        user_id = self.kwargs.get('id')
        # Ищем пользователя или выдаём 404, если такого нет
        return get_object_or_404(User, id=user_id)

class ParticipantListView(ListView):
    model = User
    template_name = 'users/participants.html'
    # Называем список 'participants', как просит ТЗ
    context_object_name = 'participants'
    # Сортировка по порядку добавления в базу (по id)
    ordering = ['id']
    # Включаем пагинацию (например, по 6 человек на страницу), 
    # чтобы заработал page_obj в твоём HTML
    paginate_by = 6 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Пустая строка для query_prefix, чтобы пагинация в HTML не выдавала ошибку
        context['query_prefix'] = "" 
        return context