from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from app_auth.middleware.admin_auth import IsUserAdmin as is_admin

urlpatterns = [
    
    # path('dashboard/', views.dashboardPage, name="dashboard"),
    path('dashboard/', is_admin(views.dashboardPage), name="dashboard"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)