from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from app_model.models import *
from app_model.models import Components


# Create your views here.


def homePage(request):
    return render(request, 'pages/home.html')



def ws_Activity(request):
    return render(request, 'pages/ws_Activity.html')

def factsheets(request):
    return render(request, "pages/menubar-pages/factsheets.html")

def map_gallery(request):
    return render(request, "pages/menubar-pages/map_gallery.html")

def news_events_list(request):
    return render(request, "pages/menubar-pages/news_events_list.html")





def watershed_health(request):
    components = Components.objects.all().values('id', 'component_name')



    context = {'components': components
               }
    
    return render(request, "pages/menubar-pages/watershed_health.html", context)







def climate_resilience(request):
    return render(request, "pages/menubar-pages/climate_resilience.html") 

def monitoring_data(request):
    return render(request, "pages/menubar-pages/monitoring_data.html")

def value_chain(request):
    return render(request, "pages/menubar-pages/value_chain.html")

def value_chain_agro(request):
    return render(request, "pages/menubar-pages/value_chain_agro.html")

def value_chain_business_model(request):
    return render(request, "pages/menubar-pages/value_chain_business_model.html")

def demonstration(request):
    return render(request, "pages/menubar-pages/demonstration.html")

def training(request):
    return render(request, "pages/menubar-pages/training.html")
        
def overview(request):
    return render(request, "pages/menubar-pages/overview.html")
        
def documents(request):
    return render(request, "pages/menubar-pages/documents.html")
            
def success_stories(request):
    return render(request, "pages/menubar-pages/success_stories.html")



