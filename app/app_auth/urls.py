
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    
    path('register-user/', views.registerUser),
    path('login-user/', views.loginUser),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)