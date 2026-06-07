from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('academics/', include('academics.urls')),
    path('results/', include('results.urls')),
    path('learning/', include('learning.urls')),
    path('announcements/', include('communication.urls')),
    path('games/', include('games.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)