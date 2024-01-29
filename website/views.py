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

def info(request):
    return render(request, 'info.html', {})

def index(request):
    return render(request, 'index.html', {})

def api_home(request):
    return render(request, 'api.html', {})

def body_viz(request):
    return render(request, 'body_viz.html', {})

def detect(request, prod='27', det='0', chassis='ECOLI',):
    #Find chassis name
    list_chassis = get_chassis()
    chassis_name = 'Escherichia Coli'
    for i in list_chassis:
        if i['Orgid'] == chassis:
            chassis_name = i['Organism']
    #Find detectable and producible name
    data_path = os.getenv('DETSPACE_DATA')
    detectables = pd.read_csv(os.path.join(data_path, 'data','Detectable.csv'))
    det_name = detectables['Name'][det]
    producibles = pd.read_csv(os.path.join(data_path, 'data','Producible.csv'))
    prod_name = producibles['Name'][prod]
    return render(request, 'index.html', {
        'prod': prod,
        'prod_name': prod_name,
        'det': det,
        'det_name': det_name,
        'chassis': chassis,
        'chassis_name': chassis_name,
    }
    )

@api_view(['GET'])
def api(request, format=None):
    return Response({
        'version': reverse('version', request=request, format=format),
        'prod': reverse('producibles', request=request, format=format),
        'det': reverse('detectables', request=request, format=format),
        'chassis': reverse('chassis', request=request, format=format),
        'paths/prod_id/det_id': reverse('paths', request=request, format=format),
        'json_paths/prod_id/det_id': reverse('json_paths', request=request, format=format),
        'det_info/det_id': reverse('det_info', request=request, format=format),
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
def path_prod_det(request, prod=None, det=None):
    if prod is None or det is None:
        return Response({'Error': "Missing prod and/or det arguments"})
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
def json_paths(request,prod=None, det=None):
    if prod is None or det is None:
        return Response({'Error': "Missing prod and/or det arguments"})
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
def get_detectable_info(request, det=None):
    if det is None:
        return Response({'Error': "Missing det argument"})
    data_path = os.getenv('DETSPACE_DATA')
    all_data = pd.read_csv(os.path.join(data_path,'data','sensbio_info.csv'))
    detectables = pd.read_csv(os.path.join(data_path,'data','Detectable.csv'))
    det_name = detectables[detectables['ID'] == int(det)]['Name'].tolist()
    det_name = det_name[0]
    data = all_data[all_data['Molecule'] == det_name]
    data.reset_index(inplace=True, drop=True)
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    print(data)
    data.to_csv(tmp.name,index=False)
    if os.path.exists(tmp.name):
        with open(tmp.name, 'rb') as fh:
            var = fh.read()
            print(var)
            response = HttpResponse(var, content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=Sensbio_info.csv'
            return response
    try:
        os.unlink(tmp.name)
    except:
        pass
    raise Http404

@api_view(['GET'])
def chassis(request, format=None):
    orgs = get_chassis()
    return Response(orgs)

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
