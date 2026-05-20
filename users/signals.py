from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(
            user=instance,
            name=instance.first_name or "",
            surname=instance.last_name or "",
        )
        profile.save()
