from django.urls import path
from . import views

urlpatterns = [
    # notes
    path('notes/', views.note_list, name='note_list'),
    path('notes/upload/', views.upload_note, name='upload_note'),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'),

    # assignments
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/upload/', views.upload_assignment, name='upload_assignment'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignments/<int:pk>/submissions/', views.view_submissions, name='view_submissions'),
    path('assignments/delete/<int:pk>/', views.delete_assignment, name='delete_assignment'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('assignments/<int:pk>/my-grade/', views.my_assignment_grade, name='my_assignment_grade'),

    # videos
    path('videos/', views.video_list, name='video_list'),
    path('videos/upload/', views.upload_video, name='upload_video'),
    path('videos/<int:pk>/', views.video_detail, name='video_detail'),
    path('videos/delete/<int:pk>/', views.delete_video, name='delete_video'),
]