import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


from .models import PremiumSubscription


logger = logging.getLogger('accounts')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User logged in: {user.username}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User logged out: {user.username}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(f"User login failed: {credentials.get('username')}")


@receiver(post_save, sender=User)
def create_subscription(sender, instance, created, **kwargs):
    if created:
        PremiumSubscription.objects.create(user=instance)