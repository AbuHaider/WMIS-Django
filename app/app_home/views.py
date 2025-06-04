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
    components = Components.objects.filter(monitoring_type='WH').prefetch_related('indicators__parameters').all()
    # components = Components.objects.filter(monitoring_type='WH').values('id', 'component_name').distinct()            
    # components = Components.objects.all().values('id', 'component_name')
    # filter(monitoring_type='WH').values_list('road_type_id', flat=True).distinct()


    context = {'components': components }
    
    return render(request, "pages/menubar-pages/watershed_health.html", context)







def climate_resilience(request):
    return render(request, "pages/menubar-pages/climate_resilience.html") 



def monitoring_data(request):

    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    # if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json': 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':   
        param_id = request.GET.get('param_val')

        if not param_id:
            return JsonResponse({'error': 'param_val is required'}, status=400)

        data_qs = WatershedHealth.objects.filter(parameter_id=param_id)
        
        monitoring_data = []
        monitoring_baseline = []

        for record in data_qs:
            # Add baseline only once
            if record.baseline_2024 is not None:
                monitoring_baseline.append([2024, float(record.baseline_2024)])

            # Add targets if available
            targets = []
            if record.target_2030 is not None:
                targets.append([2030, float(record.target_2030)])
            if record.target_2035 is not None:
                targets.append([2035, float(record.target_2035)])
            if record.target_2041 is not None:
                targets.append([2041, float(record.target_2041)])
            if record.target_2050 is not None:
                targets.append([2050, float(record.target_2050)])

            monitoring_data.extend(targets)

        return JsonResponse({
            'categories': ['2024', '2030', '2035', '2041', '2050'],
            'baseline': monitoring_baseline,
            'target': monitoring_data,
        })
        
    else:
        # Initial page load — render HTML
        return render(request, 'pages/menubar-pages/monitoring_data.html')



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



