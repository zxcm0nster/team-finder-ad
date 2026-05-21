from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError

from .models import Profile
from .utils import validate_and_normalize_phone, validate_github_url

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = forms.HiddenInput()
        self.fields["username"].required = False
        if "first_name" in self.fields:
            self.fields["first_name"].label = "Имя"
        if "last_name" in self.fields:
            self.fields["last_name"].label = "Фамилия"

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").strip().lower()
        if email:
            cleaned["username"] = email
            self.cleaned_data["username"] = email
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailLoginForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Неверный email или пароль",
    }

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "input-field"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget.attrs.setdefault("class", "input-field")

    def clean(self):
        email = (self.cleaned_data.get("username") or "").strip().lower()
        if email:
            try:
                found = User.objects.get(email__iexact=email)
                self.cleaned_data["username"] = found.username
            except User.DoesNotExist:
                self.cleaned_data["username"] = email
        return super().clean()


class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(
        required=True,
        label="Номер телефона",
        widget=forms.TextInput(
            attrs={
                "class": "input-field",
                "placeholder": "+7XXXXXXXXXX или 8XXXXXXXXXX",
            }
        ),
    )
    github_url = forms.URLField(
        required=False,
        label="Ссылка на GitHub",
        widget=forms.URLInput(
            attrs={
                "class": "input-field",
                "placeholder": "https://github.com/username",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {
            "name": forms.TextInput(attrs={"class": "input-field"}),
            "surname": forms.TextInput(attrs={"class": "input-field"}),
            "avatar": forms.FileInput(attrs={"class": "input-field", "id": "id_avatar"}),
            "about": forms.Textarea(
                attrs={"class": "input-field", "rows": 4, "placeholder": "О себе"}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        # ИСПРАВЛЕНО (Перенесено в utils.py): базовая валидация формата и нормализация
        phone = validate_and_normalize_phone(phone)

        # Проверку на уникальность в базе данных оставляем в форме (ей нужен доступ к self.instance)
        if (
            Profile.objects.filter(phone=phone)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError("Этот номер телефона уже используется другим пользователем.")

        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        # ИСПРАВЛЕНО (Перенесено в utils.py): вся валидация ушла во внешний хелпер
        return validate_github_url(github_url)


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "input-field"})
