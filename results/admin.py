from django.contrib import admin
from django.utils import timezone
from .models import SessionTerm, Result


def approve_results(modeladmin, request, queryset):
    updated = queryset.update(status='approved', approved_at=timezone.now())
    modeladmin.message_user(request, f'{updated} result(s) successfully approved.')

approve_results.short_description = 'Approve selected results'


@admin.register(SessionTerm)
class SessionTermAdmin(admin.ModelAdmin):
    list_display = ['session', 'term', 'is_active']
    list_editable = ['is_active']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'school_class', 'ca_score', 'exam_score', 'total_score', 'grade', 'status']
    list_filter = ['status', 'session_term', 'school_class']
    search_fields = ['student__first_name', 'student__surname']
    actions = [approve_results]