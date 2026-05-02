from django.contrib import admin
from .models import PremiumSubscription

# Register your models here.
@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'start_date', 'end_date', 'is_active']
    list_filter = ['start_date', 'end_date']
    search_fields = ['user__username']
    ordering = ['-start_date']