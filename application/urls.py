from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/tasks/add/', views.submit_speech2face_task),
    path('api/tasks/', views.speech2face_task_list),
    path('api/tasks/<task_id>/', views.manage_speech2face_task),
]
