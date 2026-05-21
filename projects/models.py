from django.contrib.auth.models import User
from django.db import models

MAX_LEN_SKILL = 124
MAX_LEN_PROJECT_NAME = 200
MAX_LEN_STATUS = 6

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"


class Skill(models.Model):
    name = models.CharField(
        max_length=MAX_LEN_SKILL, unique=True, verbose_name="Название навыка"
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]
    
    name = models.CharField(max_length=MAX_LEN_PROJECT_NAME, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_projects', verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub")
    status = models.CharField(
        max_length=MAX_LEN_STATUS, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    participants = models.ManyToManyField(
        User, blank=True, related_name='participated_projects', verbose_name="Участники"
    )
    skills = models.ManyToManyField(
        Skill, related_name='projects', blank=True, verbose_name="Навыки"
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
