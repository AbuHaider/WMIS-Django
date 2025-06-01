
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_auth.urls')),
    path('', include('app_home.urls')),
    path('', include('app_admin.urls')),
    path('', include('app_map.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
