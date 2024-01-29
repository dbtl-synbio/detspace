from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('info', views.info, name="info"),
    path('index', views.index, name="index"),
    path('detect/<int:prod>/<int:det>/<str:chassis>',views.detect,name="detect"),
    path('api/',views.api,name="DetSpace API"),   
    path('api/version/',views.api_version,name="version"),   
    path('api/prod/',views.prod,name="producibles"),  
    path('api/prod/<int:detec>/',views.prod_detect,name="detect_producible"),  
    path('api/det/',views.detec,name="detectables"),  
    path('api/det/<int:prod>/',views.detect_prod,name="prod_detectable"),  
    path('api/paths/',views.path_prod_det,name="paths"),
    path('api/paths/<int:prod>/<int:det>/',views.path_prod_det,name="paths"),
    path('api/json_paths/',views.path_prod_det,name="json_paths"),
    path('api/json_paths/<int:prod>/<int:det>/',views.json_paths,name="json_paths"),
    path('api/det_info/',views.get_detectable_info,name="det_info"),
    path('api/det_info/<str:det>/',views.get_detectable_info,name="det_info"),
    path('api/net/<int:prod>/<int:det>/',views.net_prod_det,name="paths"),
    path('api/chassis/',views.chassis,name="chassis"),  
]
