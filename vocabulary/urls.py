from django.urls import path
from . import views

urlpatterns = [
    path('', views.vocab_home, name='vocab_home'),
    path('check/', views.check_word, name='vocab_check'),
    path('not-learned/', views.not_learned, name='not_learned'),
    path('lesson/<int:lesson_id>/<str:mode>/', views.practice_lesson, name='vocab_practice_lesson'),
    path('<str:level_code>/<str:mode>/', views.practice, name='vocab_practice'),

]
