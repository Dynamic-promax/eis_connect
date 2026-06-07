from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'target', 'created_by', 'is_pinned', 'created_at']
    list_filter = ['target', 'is_pinned']
    list_editable = ['is_pinned']