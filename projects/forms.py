from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    # Жестко задаем варианты выбора для статуса
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='Статус',
        widget=forms.Select(attrs={'class': 'input-field'})
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'github_url': 'Ссылка на GitHub',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Название проекта'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'placeholder': 'Расскажите о проекте...', 'rows': 5}),
            'github_url': forms.URLInput(attrs={'class': 'input-field', 'placeholder': 'https://github.com/...'}),
        }
