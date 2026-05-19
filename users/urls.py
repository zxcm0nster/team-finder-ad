from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    # Используем встроенный LoginView, но подсовываем ему твой шаблон
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    # При выходе перекидываем обратно на страницу логина или главную
    path('logout/', views.custom_logout, name='logout'),
]
