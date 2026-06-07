from django.db import models
from django.contrib.auth.models import User


class Announcement(models.Model):
    TARGET_CHOICES = [
        ('all', 'Everyone'),
        ('teachers', 'Teachers Only'),
        ('parents', 'Parents Only'),
        ('students', 'Students Only'),
        ('parents_students', 'Parents and Students'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    target = models.CharField(max_length=30, choices=TARGET_CHOICES, default='all')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title