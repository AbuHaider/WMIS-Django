from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from app_model.models import *


# Create your views here.
def mapViewPage(request):
    return render(request, 'pages/map_view.html')


@require_POST
def getShapeFilePathAndLegndInfo(request):
    try:
        v_watershed_id = request.POST.get('p_watershed_id')
        p_category_id = request.POST.get('dataToSend')
        
        ret_data = MapShapeFile.objects.filter(category_id=v_watershed_id)
        json_data = [{
            'row_id': obj.id,
            'cat_name': obj.category_name,
            # 'file_path': str(obj.file_path.url) if obj.file_path else None,
            'file_path': f"/static/map_files/{obj.file_path.name}" if obj.file_path else None,  
        } for obj in ret_data]
        
        layer_color_data = LayerMapColor.objects.filter(category_id=p_category_id)
        layer_json_data = [{
            'row_id': obj.id,
            'para_name': obj.para_name,  
            'legend_name': obj.legend_value,  
            'layer_color': obj.layer_color,  
        } for obj in layer_color_data] if layer_color_data.exists() else []
        
        legend_data = MapLegend.objects.filter(category_id=p_category_id)
        legend_json_data = [{
            'row_id': obj.id,
            'title_name': obj.display_header,  
            'legend_name': obj.legend_value,  
            'legend_color': obj.legend_color,  
        } for obj in legend_data] if legend_data.exists() else []

        return JsonResponse({
            'status': True, 
            'response': {'map_data': json_data, 'layer_color': layer_json_data, 'legend_data': legend_json_data}
        })
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})
    
    
@require_POST    
def getDistrcitWiseWatershedList(request):
    try:
        district_name = request.POST.get('district')
            
        if not district_name:
            return JsonResponse({
                'status': False,
                'message': 'District parameter is required'
            }, status=400)
        
        watersheds = Watershed.objects.filter(
            district=district_name
        ).order_by('serial').values(
            'watershed_code',
            'watershed_name'
        )
        
        return JsonResponse({
            'status': True,
            'watersheds': list(watersheds)  # Convert QuerySet to list
        })

    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})
    


@require_POST
def getShapeFilePathAndParaInfo(request):
    try:
        p_category_id = request.POST.get('dataToSend')
        
        ret_data = MapShapeFile.objects.filter(category_id=p_category_id)
        json_data = [{
            'row_id': obj.id,
            'cat_name': obj.category_name,
            # 'file_path': str(obj.file_path.url) if obj.file_path else None,
            'file_path': f"/static/map_files/{obj.file_path.name}" if obj.file_path else None,  
        } for obj in ret_data]
        
        legend_data = ParaMapLegend.objects.filter(watershed_id=p_category_id)
        legend_json_data = [{
            'row_id': obj.id,
            'title_name': obj.legend_title,  
            'para_name': obj.para_name,  
            'para_map_color': obj.legend_color,  
        } for obj in legend_data] if legend_data.exists() else []

        return JsonResponse({'status': True, 'response': {'map_data': json_data, 'legend_data': legend_json_data}})
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})
    

@require_POST
def getCommunityWiseTabularData(request):
    try:
        p_categry_id = request.POST.get('categry_id')
        p_para_name = request.POST.get('para_name')
        print(f"Received para_name: {p_para_name}")
        # p_para_name = p_para_name.strip()
        
        ret_data = ParaWiseLayerInfo.objects.filter(category_id=p_categry_id, para_name=p_para_name).order_by('sorting')
        
        json_data = [{
            'description': obj.description, 
            'chakma': obj.chakma,
            'marma': obj.marma,
            'tripura': obj.tripura,
            'manipuri': obj.manipuri,
            'tanchangya': obj.tanchangya,
            'non_ips': obj.non_ips,
            'total': obj.total,
        } for obj in ret_data]

        response_data = {
            'para_name': p_para_name,
            'details': json_data
        }

        return JsonResponse({'status': True, 'response': json_data })
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})



@require_POST
def getEducationInfo(request):
    try:
        p_para_name = request.POST.get('para_name')
        print(f"Received para_name: {p_para_name}")
        # p_para_name = p_para_name.strip()
        ret_data = ParaWiseEducationInfo.objects.filter(para_name=p_para_name).order_by('sorting')
        
        json_data = [{
            'description': obj.description, 
            'No. of Institution': obj.institution_number, 
            'Average Distance (km)': obj.average_distance,
            'Average Time (min)': obj.average_time,
        } for obj in ret_data]

        return JsonResponse({'status': True, 'response': json_data })
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})



@require_POST
def getLiteracyInfo(request):
    try:
        p_para_name = request.POST.get('para_name')
        print(f"Received para_name: {p_para_name}")
        # p_para_name = p_para_name.strip()
        ret_data = ParaWiseLiteracyInfo.objects.filter(para_name=p_para_name).order_by('sorting')
        
        json_data = [{
            'description': obj.description, 
            'male': obj.male, 
            'female': obj.female,
            'total': obj.total,
        } for obj in ret_data]

        return JsonResponse({'status': True, 'response': json_data })
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})



@require_POST
def getOneValueBasedTableInfo(request):
    try:
        p_para_name = request.POST.get('para_name')
        p_category_id = request.POST.get('category_id')
        print(f"Received para_name: {p_para_name}")
        # p_para_name = p_para_name.strip()
        ret_data = OneValueBasedTabular.objects.filter(category_id=p_category_id, para_name=p_para_name).order_by('sorting')
        
        json_data = [{
            'description': obj.description, 
            'value': obj.value,
        } for obj in ret_data]

        return JsonResponse({'status': True, 'response': json_data })
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})
