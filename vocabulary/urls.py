from django.urls import path
from . import views

urlpatterns = [
    path('', views.vocab_home, name='vocab_home'),
    path('check/', views.check_word, name='vocab_check'),
    path('<str:level_code>/<str:mode>/', views.practice, name='vocab_practice'),
]
