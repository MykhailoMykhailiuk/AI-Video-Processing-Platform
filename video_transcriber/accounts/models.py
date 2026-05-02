from django.db import models
from django.utils import timezone

# Create your models here.
class PremiumSubscription(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        if self.end_date:
            return self.end_date > timezone.now()
        return False

    def __str__(self):
        return f"{self.user.username} - {'Active' if self.is_active() else 'Inactive'}"