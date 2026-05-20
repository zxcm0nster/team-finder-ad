from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import Project


class ProjectForm(forms.ModelForm):
    STATUS_CHOICES = [
        ("open", "Открыт"),
        ("closed", "Закрыт"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Статус",
        widget=forms.Select(attrs={"class": "input-field"}),
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "input-field", "placeholder": "Название проекта"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "input-field",
                    "placeholder": "Расскажите о проекте...",
                    "rows": 5,
                }
            ),
            "github_url": forms.URLInput(
                attrs={"class": "input-field", "placeholder": "https://github.com/..."}
            ),
        }

    def clean_github_url(self):
        github_url = (self.cleaned_data.get("github_url") or "").strip()
        if not github_url:
            return github_url
        parsed_url = urlparse(github_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValidationError("Введите корректный URL-адрес.")
        if "github.com" not in parsed_url.netloc.lower():
            raise ValidationError("Ссылка должна вести именно на сайт github.com.")
        return github_url
