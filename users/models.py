import random

from django.contrib.auth.models import User
from django.db import models

from .utils import generate_avatar

# Константы длин полей модели (PEP 8)
MAX_LEN_NAME = 124
MAX_LEN_PHONE = 12
MAX_LEN_ABOUT = 256
RANDOM_FILENAME_MAX = 10000


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=MAX_LEN_NAME, verbose_name="Имя")
    surname = models.CharField(max_length=MAX_LEN_NAME, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Аватар",
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=MAX_LEN_PHONE, verbose_name="Телефон", blank=True, default='')
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub")
    about = models.TextField(max_length=MAX_LEN_ABOUT, blank=True, null=True, verbose_name="О себе")
    favorite_projects = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='favorited_by_profiles',
        verbose_name="Избранные проекты",
    )

    def save(self, *args, **kwargs):
        if not self.avatar:
            letter = self.name[0].upper() if self.name else "?"
            filename = f"avatar_{self.user.username}_{random.randint(1, RANDOM_FILENAME_MAX)}.png"
            self.avatar.save(filename, generate_avatar(letter), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}"
