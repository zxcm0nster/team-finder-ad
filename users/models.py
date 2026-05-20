import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models


# Цвета для аватара
AVATAR_COLORS = [
    (76, 175, 80),
    (33, 150, 243),
    (156, 39, 176),
    (255, 152, 0),
    (0, 150, 136),
    (244, 67, 54),
    (63, 81, 181),
    (121, 85, 72),
    (255, 193, 7),
]


def generate_avatar(letter, size=(200, 200)):
    color = random.choice(AVATAR_COLORS)
    image = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except IOError:
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2 - 10
    draw.text((x, y), letter, fill="white", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Аватар",
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=12, verbose_name="Телефон", blank=True, default='')
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub")
    about = models.TextField(max_length=256, blank=True, null=True, verbose_name="О себе")
    favorite_projects = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='favorited_by_profiles',
        verbose_name="Избранные проекты",
    )

    def save(self, *args, **kwargs):
        if not self.avatar:
            letter = self.name[0].upper() if self.name else "?"
            filename = f"avatar_{self.user.username}_{random.randint(1, 10000)}.png"
            self.avatar.save(filename, generate_avatar(letter), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}"
