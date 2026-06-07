from django.db import models
from academics.models import Student, Subject, SchoolClass, Teacher


class SessionTerm(models.Model):
    TERM_CHOICES = [
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term'),
    ]

    session = models.CharField(max_length=20)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.session} — {self.get_term_display()}"

    def save(self, *args, **kwargs):
        if self.is_active:
            SessionTerm.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Session & Term"
        verbose_name_plural = "Sessions & Terms"


class Result(models.Model):
    GRADE_CHOICES = [
        ('A', 'A — Excellent'),
        ('B', 'B — Very Good'),
        ('C', 'C — Good'),
        ('D', 'D — Pass'),
        ('E', 'E — Poor'),
        ('F', 'F — Fail'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    session_term = models.ForeignKey(SessionTerm, on_delete=models.CASCADE)

    ca_score = models.DecimalField(max_digits=5, decimal_places=2)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)

    teacher_comment = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'subject', 'session_term')
        ordering = ['subject__name']

    def calculate_grade(self, total):
        if total >= 70:
            return 'A'
        elif total >= 60:
            return 'B'
        elif total >= 50:
            return 'C'
        elif total >= 45:
            return 'D'
        elif total >= 40:
            return 'E'
        else:
            return 'F'

    def save(self, *args, **kwargs):
        self.total_score = self.ca_score + self.exam_score
        self.grade = self.calculate_grade(self.total_score)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} — {self.subject} — {self.session_term}"