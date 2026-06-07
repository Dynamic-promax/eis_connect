from django.db import models
from academics.models import SchoolClass, Subject, Teacher
from results.models import SessionTerm


class Note(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='notes')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='notes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    session_term = models.ForeignKey(SessionTerm, on_delete=models.CASCADE, related_name='notes')
    topic = models.CharField(max_length=200)
    week = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.topic} — {self.subject.name} — {self.school_class.name}"

    def filename(self):
        return self.file.name.split('/')[-1]

    def file_extension(self):
        name = self.filename()
        if '.' in name:
            return name.split('.')[-1].upper()
        return 'FILE'


class Assignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    session_term = models.ForeignKey(SessionTerm, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    instruction = models.TextField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    deadline = models.DateTimeField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} — {self.subject.name} — {self.school_class.name}"

    def filename(self):
        if self.file:
            return self.file.name.split('/')[-1]
        return None

    def file_extension(self):
        name = self.filename()
        if name and '.' in name:
            return name.split('.')[-1].upper()
        return 'FILE'

    def is_overdue(self):
        from django.utils import timezone
        return timezone.now() > self.deadline


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('academics.Student', on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text_answer = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # grading fields
    grade = models.CharField(max_length=5, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_remark = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student} — {self.assignment.title}"

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student} — {self.assignment.title}"
    
class ClassVideo(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='videos')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='videos')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    session_term = models.ForeignKey(SessionTerm, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    week = models.CharField(max_length=20)
    video_file = models.FileField(upload_to='class_videos/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} — {self.subject.name} — {self.school_class.name}"

    def is_url(self):
        return bool(self.video_url)

    def is_file(self):
        return bool(self.video_file)