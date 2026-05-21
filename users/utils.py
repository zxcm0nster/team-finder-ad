import io
import random
import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

# Константы цветов для аватара
COLOR_GREEN = (76, 175, 80)
COLOR_BLUE = (33, 150, 243)
COLOR_PURPLE = (156, 39, 176)
COLOR_ORANGE = (255, 152, 0)
COLOR_TEAL = (0, 150, 136)
COLOR_RED = (244, 67, 54)
COLOR_INDIGO = (63, 81, 181)
COLOR_BROWN = (121, 85, 72)
COLOR_AMBER = (255, 193, 7)

AVATAR_COLORS = [
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_PURPLE,
    COLOR_ORANGE,
    COLOR_TEAL,
    COLOR_RED,
    COLOR_INDIGO,
    COLOR_BROWN,
    COLOR_AMBER,
]

# Константы для конфигурации изображения
DEFAULT_AVATAR_SIZE = (200, 200)
FONT_SIZE = 100
FONT_NAME = "arial.ttf"
Y_OFFSET = 10


def validate_and_normalize_phone(phone):
    phone = phone.strip()
    if not phone:
        raise ValidationError("Укажите номер телефона.")

    if not re.match(r"^(\+7|8)\d{10}$", phone):
        raise ValidationError(
            "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )

    if phone.startswith("8"):
        phone = "+7" + phone[1:]

    return phone


def validate_github_url(github_url):
    github_url = github_url.strip()
    if not github_url:
        return github_url

    parsed_url = urlparse(github_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValidationError("Введите корректный URL-адрес.")

    if "github.com" not in parsed_url.netloc.lower():
        raise ValidationError("Ссылка должна вести именно на сайт github.com.")

    return github_url


def generate_avatar(letter, size=DEFAULT_AVATAR_SIZE):
    color = random.choice(AVATAR_COLORS)
    image = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2 - Y_OFFSET

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())
