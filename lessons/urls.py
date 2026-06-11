from django.urls import path
from . import views

urlpatterns = [
    path('', views.level_list, name='level_list'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:pk>/watched/', views.mark_video_watched, name='mark_video_watched'),
    path('<str:level_code>/', views.lesson_list, name='lesson_list'),
]
