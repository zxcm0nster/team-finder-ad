from django import forms

from users.utils import validate_github_url
from .models import Project

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"

STATUS_CHOICES = [
    (STATUS_OPEN, "Открыт"),
    (STATUS_CLOSED, "Закрыт"),
]


class ProjectForm(forms.ModelForm): 
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
        github_url = self.cleaned_data.get("github_url", "") 
        # Красиво переиспользуем валидатор, чтобы не писать логику заново
        return validate_github_url(github_url)
