from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
 
from app_home.views import *

##
urlpatterns = [
     
    path('', homePage, name="home"),
    
    # Other pages Urls ::
    path('ws-activity/', ws_Activity, name="ws_activity"),
    path('factsheets', factsheets, name="factsheets"),
    path('map_gallery', map_gallery, name="map_gallery"),
    path('news_events_list', news_events_list, name="news_events_list"),
    path('watershed_health', watershed_health, name="watershed_health"),
    path('climate_resilience', climate_resilience, name="climate_resilience"),
    path('monitoring_data', monitoring_data, name="monitoring_data"),
    path('value_chain', value_chain, name="value_chain"),
    path('value_chain_agro', value_chain_agro, name="value_chain_agro"),
    path('value_chain_business_model', value_chain_business_model, name="value_chain_business_model"),    
    path('demonstration', demonstration, name="demonstration"),
    path('training', training, name="training"),
    path('overview', overview, name="overview"),
    path('documents', documents, name="documents"),
    path('success_stories', success_stories, name="success_stories"),
    
]
 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)