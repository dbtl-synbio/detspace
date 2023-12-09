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
]
