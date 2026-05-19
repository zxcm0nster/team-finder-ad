from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    # После успешной регистрации перенаправляем на страницу входа
    success_url = reverse_lazy('users:login')

def custom_logout(request):
    logout(request)
    return redirect('users:login')
