from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('battle/', views.battle, name='battle'),
    path('battle/new/', views.battle_new, name='battle_new'),
    path('battle/check/', views.battle_check, name='battle_check'),
]
