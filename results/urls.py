from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_result, name='upload_result'),
    path('pending/', views.pending_results, name='pending_results'),
    path('approve/<int:pk>/', views.approve_result, name='approve_result'),
    path('approve-class/', views.approve_class_results, name='approve_class_results'),
    path('view/', views.view_result, name='view_result'),
    path('class-results/', views.class_result_sheet, name='class_result_sheet'),
]