from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('about.html', views.about, name="about"),
    path('index.html', views.index, name="index"),
    # path('contact.html', views.contact, name="contact"),
    # path('chassis.html', views.chassis, name="chassis"),
    # path('target.html', views.target, name="target"),
    # path('effector.html', views.effector, name="effector"),
    # path('plasmid.html', views.plasmid, name="plasmid"),
    # path('specifications.html', views.specifications, name="specifications"),
    # path('vis_template.html', views.vis_template, name="vis_template"),
    # path('body_viz.html', views.vis_template, name="body_viz"),
    path('<int:target_id>', views.info, name="info"),
    re_path(r'^get_log/$', views.hola, name='get_log'),
    path('rest_framework/api.html',views.api_home,name="hello"),
#    path('api.html',views.api_home,name="DetSpace API"),   
    path('api/',views.api,name="DetSpace API"),   
    path('api/version/',views.api_version,name="version"),   
    path('api/prod/',views.prod,name="producibles"),  
    path('api/prod/<int:detec>/',views.prod_detect,name="detect_producible"),  
    path('api/det/',views.detec,name="detectables"),  
    path('api/det/<int:prod>/',views.detect_prod,name="prod_detectable"),  
    path('api/paths/',views.path_prod_det,name="paths"),
    path('api/paths/<int:prod>/<int:det>/',views.path_prod_det,name="paths"),
    path('api/net/<int:prod>/<int:det>/',views.net_prod_det,name="paths"),
]
