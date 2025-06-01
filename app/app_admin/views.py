from django.shortcuts import render, redirect
from django.http import JsonResponse



from app_model.models import *


# Create your views here.
def dashboardPage(request):
    return render(request, 'pages/dashboard.html')
