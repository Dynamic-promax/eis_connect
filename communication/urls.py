from django.urls import path
from . import views

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('create/', views.create_announcement, name='create_announcement'),
    path('<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),
    path('<int:pk>/pin/', views.pin_announcement, name='pin_announcement'),
]