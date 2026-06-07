from django.contrib import admin
from .models import Note, Assignment, AssignmentSubmission


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['topic', 'subject', 'school_class', 'week', 'teacher', 'uploaded_at']
    list_filter = ['school_class', 'subject', 'session_term']
    search_fields = ['topic']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'school_class', 'deadline', 'teacher']
    list_filter = ['school_class', 'subject', 'session_term']
    search_fields = ['title']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at']
    list_filter = ['assignment']