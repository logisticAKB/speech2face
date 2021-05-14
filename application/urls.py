from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/speech2face/', views.submit_speech2face_task),
    path('api/speech2face/<task_id>/', views.manage_speech2face_task),
]
