from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Target
import os
import pandas as pd
import json
import distutils.dir_util
from io import StringIO
from .utils import annotate_chemical_svg, get_detectables, get_producibles, get_prod_detec, get_detec_prod, get_chassis

# from bs4 import BeautifulSoup

def home(request):
    return render(request, 'home.html', {})

def contact(request):
    if request.method == "POST":
        message_email = request.POST['message-email']
        message = request.POST['message']

        # send an email
        send_mail(
           'Suggestions and additional help' , # subject
            message, # message
            message_email, # from email
            ['demo@gmail.com'], # To email
            )
        
        return render(request, 'contact.html', {})
    else:
        return render(request, 'contact.html', {})
def chassis(request):
    return render(request, 'chassis.html', {})

def about(request):
    return render(request, 'about.html', {})

def index(request):
    return render(request, 'index.html', {})

def api_home(request):
    return render(request, 'api.html', {})

def target(request):
    targets = Target.objects.order_by('name')
    #targets = Target.objects.all()
    return render(request, 'target.html', {'targets': targets})

def effector(request):
    return render(request, 'effector.html', {})

def plasmid(request):
    return render(request, 'plasmid.html', {})

def specifications(request):
    return render(request, 'specifications.html', {})

def info(request, target_id):
    targets = Target.objects.get(pk=target_id)
    #targets = Target.objects.all()
    return render(request, 'info.html', {'target': target})


def hola(request):
    #results = request.GET.get('chassis',None)+' y ya estaría'
    r = open('website/templates/index.html').read()
    results = {'url_data':r}
    return HttpResponse(results)

def vis_template(request):
    return render(request, 'vis_template.html', {})

def body_viz(request):
    return render(request, 'body_viz.html', {})

@api_view(['GET'])
def api(request, format=None):
    print(request)
    return Response({
        'version': reverse('version', request=request, format=format),
        'prod': reverse('producibles', request=request, format=format),
 #       'prod/det_id': reverse('detect_prod', request=request, format=format),
        'det': reverse('detectables', request=request, format=format),
 #       'det/prod_id': reverse('prod_detectable', request=request, format=format),
        'paths/prod_id/det_id': reverse('paths', request=request, format=format),
        'chassis': reverse('chassis', request=request, format=format),
    })

@api_view(['GET'])
def api_version(request, format=None):
    return Response({
        'app': 'DetSpace',
        'version': '1.0'
    })

@api_view(['GET'])
def prod(request, format=None):
    prods = get_producibles()
    return Response(prods)

@api_view(['GET'])
def detec(request, format=None):
    detecs = get_detectables()
    return Response(detecs)

@api_view(['GET'])
def prod_detect(request, detec='1', format=None):
    dl = get_detec_prod(detec)
    return Response(dl)

@api_view(['GET'])
def detect_prod(request, prod='1', format=None):
    pl = get_prod_detec(prod)
    return Response(pl)

@api_view(['GET'])
def path_prod_det(request, prod='1', det='1'):
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'website/files/D266P132.json')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

@api_view(['GET'])
def chassis(request, format=None):
    orgs = get_chassis()
    return Response(orgs)

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})

@api_view(['GET'])
def net_prod_det(request, prod='1', det='1'):
    data_path = os.getenv('DETSPACE_DATA')
    basename = 'D'+str(det)+'P'+str(prod)
    netname = basename+'_network.json'
    pathname = basename+'_pathway.json'
    netfile = os.path.join(data_path,'P'+str(prod),netname)
    pathfile = os.path.join(data_path,'P'+str(prod),pathname)
    net = json.load(open(netfile))
    pathway = json.load(open(pathfile))
    net = annotate_chemical_svg(net)
    nets = 'network = '+json.dumps(net)+'\n'+'pathway_info = '+json.dumps(pathway)
    with StringIO(nets) as fh:
        response = HttpResponse(fh.read(), content_type="application/js")
        response['Content-Disposition'] = 'inline; filename=' + basename+'.js'
        return response
    raise Http404