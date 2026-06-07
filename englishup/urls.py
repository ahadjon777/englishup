"""
URL configuration for englishup project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls')),
    path('lessons/', include('lessons.urls')),
    path('quiz/', include('quiz.urls')),
    path('vocabulary/', include('vocabulary.urls')),
    path('market/', include('users.market_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
