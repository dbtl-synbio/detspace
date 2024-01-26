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
import zipfile
from io import StringIO
import tarfile, tempfile
from .utils import annotate_chemical_svg, get_detectables, get_producibles, get_prod_detec, get_detec_prod, get_chassis

# from bs4 import BeautifulSoup

def chassis(request):
    return render(request, 'chassis.html', {})

def info(request):
    return render(request, 'info.html', {})

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

# def info(request, target_id):
#     targets = Target.objects.get(pk=target_id)
#     #targets = Target.objects.all()
#     return render(request, 'info.html', {'target': target})


# def hola(request):
#     #results = request.GET.get('chassis',None)+' y ya estaría'
#     r = open('website/templates/index.html').read()
#     results = {'url_data':r}
#     return HttpResponse(results)

def vis_template(request):
    return render(request, 'vis_template.html', {})

def body_viz(request):
    return render(request, 'body_viz.html', {})

def detect(request, prod='27', det='0', chassis='ECOLI',):
    return render(request, 'index.html', {
        'prod': prod,
        'det': det,
        'chassis': chassis,
    }
    )

@api_view(['GET'])
def api(request, format=None):
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
def path_prod_det(request, prod='27', det='0'):
    data_path = os.getenv('DETSPACE_PATHDATA')
    name = 'D'+str(det)+'P'+str(prod)
    source_dir = os.path.join(data_path,name)
    tmp = tempfile.NamedTemporaryFile(delete=False)
    if os.path.exists(source_dir) and os.path.isdir(source_dir):
        with tarfile.open(tmp.name, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        if os.path.exists(tmp.name):
            with open(tmp.name, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/gzip")
                response['Content-Disposition'] = 'inline; filename=' + name+'.tar.gz'
#                response.headers["Content-Security-Policy"] = "default-src 'self' https://polyfill.io"
                return response
    try:
        os.unlink(tmp.name)
    except:
        pass
    raise Http404

@api_view(['GET'])
def json_paths(request,prod='27', det='0'):
    data_path = os.getenv('DETSPACE_DATA')
    try:
        zf = zipfile.ZipFile(os.path.join(data_path,'data','json_pair_files.zip'))
        basename = 'D'+str(det)+'P'+str(prod)
        netname = basename+'_network.json'
        pathname = basename+'_pathway.json'
        netfile = os.path.join('json_pair_files','P'+str(prod),netname)
        pathfile = os.path.join('json_pair_files','P'+str(prod),pathname)
        net = json.load(zf.open(netfile))
        pathway = json.load(zf.open(pathfile))
    except:
        return Http404
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp_net = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    tmp_path = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    json.dump(net,tmp_net)
    json.dump(pathway,tmp_path)
    with tarfile.open(tmp.name, "w:gz") as tar:
        tar.add(tmp_net.name, arcname=netname)
        tar.add(tmp_path.name, arcname=pathname)
    if os.path.exists(tmp.name):
        with open(tmp.name, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/gzip")
            response['Content-Disposition'] = 'inline; filename=' + basename + '.tar.gz'
            return response
    try:
        os.unlink(tmp.name)
        os.unlink(tmp_net.name)
        os.unlink(tmp_path.name)
    except:
        pass
    raise Http404

@api_view(['GET'])
def chassis(request, format=None):
    orgs = get_chassis()
    return Response(orgs)

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})

@api_view(['GET'])
def net_prod_det(request, prod='27', det='0'):
    data_path = os.getenv('DETSPACE_DATA')
    zf=zipfile.ZipFile(os.path.join(data_path,'data','json_pair_files.zip'))
    basename = 'D'+str(det)+'P'+str(prod)
    netname = basename+'_network.json'
    pathname = basename+'_pathway.json'
    netfile = os.path.join('json_pair_files','P'+str(prod),netname)
    pathfile = os.path.join('json_pair_files','P'+str(prod),pathname)
    net = json.load(zf.open(netfile))
    pathway = json.load(zf.open(pathfile))
    net = annotate_chemical_svg(net)
    nets = 'network = '+json.dumps(net)+'\n'+'pathways_info = '+json.dumps(pathway)
    with StringIO(nets) as fh:
        response = HttpResponse(fh.read(), content_type="application/js")
        response['Content-Disposition'] = 'inline; filename=' + basename+'.js'
        return response
    raise Http404
