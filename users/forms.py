import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Имя")
    last_name = forms.CharField(max_length=150, required=True, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ProfileEditForm(forms.ModelForm):
    # Объявляем поля явно, чтобы Django не выбрасывал FieldError при запуске сервера
    phone = forms.CharField(
        required=False,
        label='Номер телефона',
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': '+7XXXXXXXXXX или 8XXXXXXXXXX'})
    )
    github_url = forms.URLField(
        required=False,
        label='Ссылка на GitHub',
        widget=forms.URLInput(attrs={'class': 'input-field', 'placeholder': 'https://github.com/username'})
    )

    class Meta:
        model = User
        fields = [] # Оставляем пустым, так как наши кастомные поля объявлены выше

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Автоматически заполняем поля текущими данными пользователя при GET-запросе
        if self.instance and self.instance.pk:
            self.fields['phone'].initial = getattr(self.instance, 'phone', '')
            self.fields['github_url'].initial = getattr(self.instance, 'github_url', '')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        
        if not phone:
            return phone

        # 1. Проверяем формат (8 или +7 и затем 10 цифр)
        if not re.match(r'^(\+7|8)\d{10}$', phone):
            raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")

        # 2. Приводим к единому стандарту: '8' -> '+7'
        if phone.startswith('8'):
            phone = '+7' + phone[1:]

        # 3. Проверка уникальности номера телефона
        model_class = self._meta.model
        try:
            if model_class.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Этот номер телефона уже используется другим пользователем.")
        except Exception:
            # Защита на случай, если поле еще не добавлено в саму БД через миграции
            pass

        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '').strip()

        if github_url:
            # 1. Базовая проверка структуры URL
            parsed_url = urlparse(github_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValidationError("Введите корректный URL-адрес.")

            # 2. Проверяем домен github.com
            if 'github.com' not in parsed_url.netloc.lower():
                raise ValidationError("Ссылка должна вести именно на сайт github.com.")

        return github_url

    def save(self, commit=True):
        user = super().save(commit=False)
        # Записываем очищенные данные в объект пользователя перед сохранением
        user.phone = self.cleaned_data.get('phone')
        user.github_url = self.cleaned_data.get('github_url')
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-field'})
