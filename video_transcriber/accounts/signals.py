from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PremiumSubscription


@receiver(post_save, sender=User)
def create_subscription(sender, instance, created, **kwargs):
    if created:
        PremiumSubscription.objects.create(user=instance)