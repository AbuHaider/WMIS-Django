from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
 
from app_map.views import *

##
urlpatterns = [ 
    path('map-view/', mapViewPage, name="map_view"),
    
    path('get-shape-file-path-and-map-legend-info/', getShapeFilePathAndLegndInfo),
    path('get-district-wise-watershed-list/', getDistrcitWiseWatershedList),
    path('get-shape-file-path-and-para-legend-info/', getShapeFilePathAndParaInfo),
    
    path('get-community-wise-tabular-data/', getCommunityWiseTabularData),
    path('get-education-info/', getEducationInfo),
    path('get-literacy-info/', getLiteracyInfo),
    path('get-one-value-based-tabular-data/', getOneValueBasedTableInfo),
    
]
 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)