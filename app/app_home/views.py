from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict
import json
from app_model.models import *
from app_model.models import Components, WatershedOverallStatus

from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict

from itertools import groupby
from operator import attrgetter



# Create your views here.


def homePage(request):
    return render(request, 'pages/home.html')



def ws_Activity(request):
    return render(request, 'pages/ws_Activity.html')

def factsheets(request):
    return render(request, "pages/menubar-pages/factsheets.html")


def map_gallery(request):
    watersheds = Watershed.objects.prefetch_related('mapgallery_set').all()

    data = []
    for ws in watersheds:
        map_groups = defaultdict(list)
        for m in ws.mapgallery_set.all():
            map_groups[m.map_type].append(m)
        data.append({
            "watershed": ws,
            "map_groups": dict(map_groups)
        })

    context = {"watershed_data": data}
    
    return render(request, "pages/menubar-pages/map_gallery.html", context)
    


def reports(request):
    reports = Reports.objects.all().order_by('kp_type', '-id')

    # group reports by kp_type
    grouped_reports = {}
    for kp_type, items in groupby(reports, key=attrgetter('kp_type')):
        grouped_reports[kp_type] = list(items)
    
    context = {"reports": grouped_reports}
    
    return render(request, "pages/menubar-pages/reports.html", context)
        

def news_events_list(request):
    return render(request, "pages/menubar-pages/news_events_list.html")





def watershed_health(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            watershed_id = request.GET.get('watershed_id')
            if not watershed_id:
                return JsonResponse({'error': 'A watershed_id is required.'}, status=400)
            # watershed_status = WatershedOverallStatus.objects.filter(watershed=watershed_id).values().first()

            status_obj = WatershedOverallStatus.objects.filter(watershed=watershed_id).first()
            watershed_status = model_to_dict(status_obj) if status_obj else {}
            # components = Components.objects.filter(
            #     monitoring_type='WH',
            #     indicators__monitoring_type='WH',
            #     indicators__parameters__monitoring_type='WH',
            #     indicators__parameters__climate_resiliences__watershed_id=watershed_id
            # ).distinct().prefetch_related('indicators__parameters')
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

            return JsonResponse({'watershed_status':watershed_status, 'components': data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Regular page render
    watersheds = Watershed.objects.all().values('id', 'watershed_name', 'watershed_code')    
    # watershed_status = WatershedOverallStatus.objects.filter(watershed=1).values().first()

    # Load default watershed status for watershed ID 1 (or pick first dynamically)
    default_watershed_id = 1
    watershed_status = WatershedOverallStatus.objects.filter(watershed=default_watershed_id).values().first()

    components = Components.objects.filter(monitoring_type='WH').prefetch_related('indicators__parameters')
    context = {'watersheds': watersheds, 'watershed_status':watershed_status, 'components': components, }


    # watersheds = Watershed.objects.all().values('id', 'watershed_name', 'watershed_code')
    # components = Components.objects.filter(monitoring_type='WH').prefetch_related('indicators__parameters').all()
    # # # # components = Components.objects.filter(monitoring_type='WH').values('id', 'component_name').distinct()            
    # # # # components = Components.objects.all().values('id', 'component_name')
    # # # # filter(monitoring_type='WH').values_list('road_type_id', flat=True).distinct()

    # context = {'watersheds':watersheds, 'components': components }
    
    return render(request, "pages/menubar-pages/watershed_health.html", context)







def climate_resilience(request):    
    watersheds = Watershed.objects.all().values('id', 'watershed_name', 'watershed_code')    
    context = {'watersheds': watersheds}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            watershed_id = request.GET.get('watershed_id')
            if not watershed_id:
                return JsonResponse({'error': 'A watershed_id is required.'}, status=400)
            # watershed_status = WatershedOverallStatus.objects.filter(watershed=watershed_id).values().first()

            status_obj = WatershedOverallStatus.objects.filter(watershed=watershed_id).first()
            watershed_status = model_to_dict(status_obj) if status_obj else {}
            components = Components.objects.filter(
                monitoring_type='CR',
                indicators__monitoring_type='CR',
                indicators__parameters__monitoring_type='CR',
                indicators__parameters__climate_resiliences__watershed_id=watershed_id
            ).distinct().prefetch_related('indicators__parameters')
            # components = Components.objects.filter(monitoring_type='CR', indicators__parameters__climate_resiliences__watershed_id=watershed_id).distinct().prefetch_related('indicators__parameters')
        
            # Build JSON structure
            data = []
            for component in components:
                indicators_data = []
                for indicator in component.indicators.all():
                    if indicator.monitoring_type != 'CR':
                        continue  # Skip non-CR indicators

                    parameters_data = [
                        {'id': p.id, 'name': p.parameter_name}
                        for p in indicator.parameters.all()
                        if p.monitoring_type == 'CR' and p.climate_resiliences.filter(watershed_id=watershed_id).exists()
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

            return JsonResponse({'watershed_status':watershed_status, 'components': data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Regular page render
    watersheds = Watershed.objects.all().values('id', 'watershed_name', 'watershed_code')    
    # watershed_status = WatershedOverallStatus.objects.filter(watershed=1).values().first()

    # Load default watershed status for watershed ID 1 (or pick first dynamically)
    default_watershed_id = 1
    watershed_status = WatershedOverallStatus.objects.filter(watershed=default_watershed_id).values().first()

    components = Components.objects.filter(monitoring_type='CR').prefetch_related('indicators__parameters')    
    context = {'watersheds': watersheds, 'watershed_status':watershed_status, 'components': components, }

    return render(request, "pages/menubar-pages/climate_resilience.html", context) 



def monitoring_data(request):    
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

        # print(data_qs)
        categories = []
        monitoring_data = []
        monitoring_baseline = []
        unit = ""
        is_special = ""

        for record in data_qs:

            
            if record.is_special == 0:     

                categories = ['2024', '2030', '2035', '2041', '2050']

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
                is_special = record.is_special

            else:         

                if record.baseline_2024 is not None:
                    baseline_obj = Units.objects.filter(id=int(record.baseline_2024)).first()
                    if baseline_obj:
                        monitoring_baseline.append([2024, baseline_obj.unit_name]) 
                        
                targets = []
                if record.target_2030 is not None:
                    unit_obj = Units.objects.filter(id=int(record.target_2030)).first()
                    if unit_obj:
                        targets.append([2030, unit_obj.unit_name])
                        
                if record.target_2035 is not None:
                    unit_obj = Units.objects.filter(id=int(record.target_2035)).first()
                    if unit_obj:
                        targets.append([2035, unit_obj.unit_name])
                        
                if record.target_2041 is not None:
                    unit_obj = Units.objects.filter(id=int(record.target_2041)).first()
                    if unit_obj:
                        targets.append([2041, unit_obj.unit_name])
                        
                if record.target_2050 is not None:
                    unit_obj = Units.objects.filter(id=int(record.target_2050)).first()
                    if unit_obj:
                        targets.append([2050, unit_obj.unit_name])
                        
                monitoring_data.extend(targets)
                is_special = record.is_special

            if record.unit:
                unit = record.unit.unit_name
                categories = unit.split('/')

        return JsonResponse({
            'categories': categories,
            'baseline': monitoring_baseline,
            'target': monitoring_data,
            'unit' : unit,
            'is_special' : is_special
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


def monitoring_data_cr(request):        
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



        data_qs = ClimateResilience.objects.filter(parameter_id=param_id, watershed_id=watershed_id)        
        # data_qs = WatershedHealth.objects.filter(parameter_id=param_id, watershed_id=str(watershed_id))
        # data_qs = WatershedHealth.objects.filter(parameter_id=param_id)

        # print(data_qs)
        categories = []
        monitoring_data = []
        monitoring_baseline = []
        unit = ""
        is_special = ""

        for record in data_qs:

            
            if record.is_special == 0:     

                categories = ['2024', '2030', '2035', '2041', '2050']

                if record.baseline_2024 is not None:
                    monitoring_baseline.append([2024, float(record.baseline_2024)])

                targets = []
                for year, value in [
                    (2030, record.target_2030),
                    (2035, record.target_2035),
                    (2041, record.target_2041),
                    (2050, record.target_2050)
                ]:
                    if value is not None:
                        targets.append([year, float(value)])
                # if record.target_2030 is not None:
                #     targets.append([2030, float(record.target_2030)])
                # if record.target_2035 is not None:
                #     targets.append([2035, float(record.target_2035)])
                # if record.target_2041 is not None:
                #     targets.append([2041, float(record.target_2041)])
                # if record.target_2050 is not None:
                #     targets.append([2050, float(record.target_2050)])

                monitoring_data.extend(targets)
                is_special = record.is_special

            else:         

                if record.baseline_2024 is not None:
                    baseline_obj = Units.objects.filter(id=int(record.baseline_2024)).first()
                    if baseline_obj:
                        monitoring_baseline.append([2024, baseline_obj.unit_name]) 
                        
                targets = []
                for year, unit_id in [
                    (2030, record.target_2030),
                    (2035, record.target_2035),
                    (2041, record.target_2041),
                    (2050, record.target_2050)
                ]:
                    if unit_id is not None:
                        unit_obj = Units.objects.filter(id=int(unit_id)).first()
                        if unit_obj:
                            targets.append([year, unit_obj.unit_name])

                # if record.target_2030 is not None:
                #     unit_obj = Units.objects.filter(id=int(record.target_2030)).first()
                #     if unit_obj:
                #         targets.append([2030, unit_obj.unit_name])
                        
                # if record.target_2035 is not None:
                #     unit_obj = Units.objects.filter(id=int(record.target_2035)).first()
                #     if unit_obj:
                #         targets.append([2035, unit_obj.unit_name])
                        
                # if record.target_2041 is not None:
                #     unit_obj = Units.objects.filter(id=int(record.target_2041)).first()
                #     if unit_obj:
                #         targets.append([2041, unit_obj.unit_name])
                        
                # if record.target_2050 is not None:
                #     unit_obj = Units.objects.filter(id=int(record.target_2050)).first()
                #     if unit_obj:
                #         targets.append([2050, unit_obj.unit_name])
                        
                monitoring_data.extend(targets)
                is_special = record.is_special

            if record.unit and record.unit.unit_name:
                unit = record.unit.unit_name
                categories = unit.split('/')

        return JsonResponse({
            'categories': categories,
            'baseline': monitoring_baseline,
            'target': monitoring_data,
            'unit' : unit,
            'is_special' : is_special
        })
    
    else:
        # Regular page load — return full HTML template 
        # from .models import Watershed, Indicators  # adjust if needed
        watersheds = Watershed.objects.all()
        indicators = Indicators.objects.prefetch_related('parameters').all()

        return render(request, 'pages/menubar-pages/monitoring_data_cr.html', {
            'watersheds': watersheds,
            'indicators': indicators,
        })

        
def con_measures(request):    
    # Fetch all categories with related measures
    con_measure_cat = Conservation_Measure_Categories.objects.prefetch_related("conservation_measure_set").all()

    # Build dictionary { "Category Name": [list of measures] }
    con_measures_data = {}
    for cmc in con_measure_cat:
        measures = cmc.conservation_measure_set.all()
        con_measures_data[cmc.con_measure_category_name] = measures

    context = {"con_measures_data": con_measures_data}
    
    return render(request, "pages/menubar-pages/con_measures.html", context)
    
            

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
        
def success_stories(request):
    return render(request, "pages/menubar-pages/success_stories.html")



