from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    # Явно указываем поля, которые хотим видеть в форме помимо стандартных
    first_name = forms.CharField(max_length=150, required=True, label="Имя")
    last_name = forms.CharField(max_length=150, required=True, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        # Порядок полей в кортеже определяет порядок их вывода в HTML
        fields = ('first_name', 'last_name', 'username', 'email')
