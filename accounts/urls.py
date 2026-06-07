from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('set-password/', views.set_password_view, name='set_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('create-password/', views.create_password_view, name='create_password'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('learning-games/', views.learning_games, name='learning_games'),
]