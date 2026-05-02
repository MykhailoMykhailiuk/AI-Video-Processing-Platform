from django.contrib import admin
from twisted.test import obj
from .models import Upload, Output
from django.utils.html import format_html

# Register your models here.


class OutputInline(admin.TabularInline):
    model = Output
    extra = 0
    readonly_fields = ['output_type', 'content', 'file', 'created_at']
    can_delete = False
    

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = list_display = ['id', 'user', 'status', 'file_url', 'created_at']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['user__username', 'file_url']
    readonly_fields = ['created_at', 'thumbnail_preview']
    ordering = ['-created_at']
    inlines = [OutputInline]

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="200" style="border-radius:10px;" />',
                obj.thumbnail.url
            )
        return "No thumbnail"

    thumbnail_preview.short_description = "Thumbnail"

    actions = ['mark_completed']


    def mark_completed(self, request, queryset):
        queryset.update(status='completed')

    mark_completed.short_description = "Mark selected uploads as completed"


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'output_type', 'created_at']
    list_filter = ['output_type', 'created_at']
    search_fields = ['upload__user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

