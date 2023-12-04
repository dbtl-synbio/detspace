from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('contact.html', views.contact, name="contact"),
    path('chassis.html', views.chassis, name="chassis"),
    path('about.html', views.about, name="about"),
    path('index.html', views.index, name="index"),
    path('target.html', views.target, name="target"),
    path('effector.html', views.effector, name="effector"),
    path('plasmid.html', views.plasmid, name="plasmid"),
    path('specifications.html', views.specifications, name="specifications"),
    path('<int:target_id>', views.info, name="info"),
    re_path(r'^get_log/$', views.hola, name='get_log'),
    path('vis_template.html', views.vis_template, name="vis_template"),
]
