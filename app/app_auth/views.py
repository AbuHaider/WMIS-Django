from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
import json

from app_model.models import *

# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/login.html')

# if request.user.is_authenticated:
#     if request.user.is_superuser:
#         return redirect('admin_dashboard')
#     return redirect('user_dashboard')

def registerPage(request):
    return render(request, 'pages/register.html')


def logoutPage(request):
    return render(request, 'pages/logout.html')


@csrf_exempt
@require_POST 
def loginUser(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        print(f'user is : {username}')
        
        if not username or not password:
            return JsonResponse({'status': False, 'message': 'All fields are required...'})
        
        if not User.objects.filter(username=username).exists():
            return JsonResponse({'status': False, 'message': 'Username does not match.'})
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            token = request.session.session_key
            return JsonResponse({'status': True, "message": "Login successful",  'token': token, 'username': user.username })
        else:
            return JsonResponse({'status': False, 'message': 'Password does not match'})
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})



@csrf_exempt
@require_POST
def registerUser(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        print(f'Username : {username}, Email : {email}')

        if not username or not email or not password or not confirm_password:
            return JsonResponse({'status': False, 'message': 'All fields are required...'})

        if password != confirm_password:
            return JsonResponse({'status': False, 'message': 'Passwords do not match...'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': False, 'message': 'Username already exists...'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': False, 'message': 'Email already registered...'})

        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'status': True, 'message': 'User registered successfully', "user_id": user.id})
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})



@require_POST
def logoutUser(request):
    try:
        cache.clear()
        logout(request)  
        return redirect('login')

    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})