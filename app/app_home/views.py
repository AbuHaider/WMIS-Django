from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from app_model.models import *
from app_model.models import Components

from django.views.decorators.csrf import csrf_exempt
from app_model.models import WatershedHealth
from app_model.models import Watershed, Indicators


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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        watershed_id = request.GET.get('watershed_id')
        if not watershed_id:
            return JsonResponse({'error': 'watershed_id is required'}, status=400)

        components = Components.objects.filter(monitoring_type='WH', indicators__parameters__watershed_healths__watershed_id=watershed_id).distinct().prefetch_related('indicators__parameters')
        
        # Build JSON structure
        data = []
        for component in components:
            indicators_data = []
            for indicator in component.indicators.all():
                parameters_data = [
                    {'id': p.id, 'name': p.parameter_name}
                    for p in indicator.parameters.all()
                    if p.watershed_healths.filter(watershed_id=watershed_id).exists()
                ]
                if parameters_data:
                    indicators_data.append({
                        'id': indicator.id,
                        'name': indicator.indicator_name,
                        'parameters': parameters_data
                    })

            if indicators_data:
                data.append({
                    'id': component.id,
                    'name': component.component_name,
                    'indicators': indicators_data
                })

        return JsonResponse({'components': data})

    # Regular page render
    watersheds = Watershed.objects.all().values('id', 'watershed_name', 'watershed_code')
    components = Components.objects.filter(monitoring_type='WH').prefetch_related('indicators__parameters')
    context = {'watersheds': watersheds, 'components': components}


    # watersheds = Watershed.objects.all().values('id', 'watershed_name', 'watershed_code')
    # components = Components.objects.filter(monitoring_type='WH').prefetch_related('indicators__parameters').all()
    # # # # components = Components.objects.filter(monitoring_type='WH').values('id', 'component_name').distinct()            
    # # # # components = Components.objects.all().values('id', 'component_name')
    # # # # filter(monitoring_type='WH').values_list('road_type_id', flat=True).distinct()

    # context = {'watersheds':watersheds, 'components': components }
    
    return render(request, "pages/menubar-pages/watershed_health.html", context)







def climate_resilience(request):
    return render(request, "pages/menubar-pages/climate_resilience.html") 



def monitoring_data(request):
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        param_id = request.GET.get('param_val')
        watershed_id = request.GET.get('watershedid')

        if not param_id:
            return JsonResponse({'error': 'param_val is required'}, status=400)

        if not watershed_id:
            return JsonResponse({'error': 'watershedid is required'}, status=400)


        try:
            param_id = int(param_id)
            watershed_id = int(watershed_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid parameter ID or watershed ID'}, status=400)



        data_qs = WatershedHealth.objects.filter(parameter_id=param_id, watershed_id=watershed_id)        
        # data_qs = WatershedHealth.objects.filter(parameter_id=param_id, watershed_id=str(watershed_id))
        # data_qs = WatershedHealth.objects.filter(parameter_id=param_id)

        print(data_qs)

        monitoring_data = []
        monitoring_baseline = []
        

        for record in data_qs:
            if record.baseline_2024 is not None:
                monitoring_baseline.append([2024, float(record.baseline_2024)])

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
        # Regular page load — return full HTML template 
        # from .models import Watershed, Indicators  # adjust if needed
        watersheds = Watershed.objects.all()
        indicators = Indicators.objects.prefetch_related('parameters').all()

        return render(request, 'pages/menubar-pages/monitoring_data.html', {
            'watersheds': watersheds,
            'indicators': indicators,
        })

    # return JsonResponse({'error': 'Invalid request type'}, status=400)  
    # else:
    #     # Initial page load — render HTML
    #     return render(request, 'pages/menubar-pages/monitoring_data.html')



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



