from django.db import models
from django.contrib.auth.models import User


class Section(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SchoolClass(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.section.name})"

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} — {self.school_class.name}"


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Student(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='students')
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    passport = models.ImageField(upload_to='students/passports/', blank=True, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} ({self.admission_number})"

    def get_full_name(self):
        return f"{self.first_name} {self.surname}"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    phone = models.CharField(max_length=20, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name='teachers')

    def __str__(self):
        return self.user.get_full_name()