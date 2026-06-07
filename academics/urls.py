from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('classes/', views.class_list, name='class_list'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/add/', views.add_parent, name='add_parent'),
]