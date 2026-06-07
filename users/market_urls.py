from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_view, name='market'),
    path('buy/<int:pk>/', views.buy_sticker, name='buy_sticker'),
]
