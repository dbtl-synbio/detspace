import requests
import urllib.parse

url = "https://detspace.i2sysbio.uv.es"

def version():
    """ Returns API version"""
    api_url = urllib.parse.urljoin(url,"api/version")
    response = requests.get(api_url)
    return response.json()

def prod():
    """ Returns producibles"""
    api_url = urllib.parse.urljoin(url,"api/prod")
    response = requests.get(api_url)
    return response.json()

def det():
    """ Returns detectables"""
    api_url = urllib.parse.urljoin(url,"api/det")
    response = requests.get(api_url)
    return response.json()

def chassis():
    """ Returns chassis"""
    api_url = urllib.parse.urljoin(url,"api/chassis")
    response = requests.get(api_url)
    return response.json()

def prod_det(det):
    """ Returns producibles connected to given detectable"""
    api_url = urllib.parse.urljoin(url,"/".join(["api/prod",str(det)]))
    response = requests.get(api_url)
    return response.json()

def det_prod(prod):
    """ Returns detectables connected to given producible"""
    api_url = urllib.parse.urljoin(url,"/".join(["api/det",str(prod)]))
    response = requests.get(api_url)
    return response.json()

def paths_prod_det(prod,det):
    """ Returns pathways from producible to detectable in SBML format"""
    api_url = urllib.parse.urljoin(url,"/".join(["api/paths",str(prod),str(det)]))
    response = requests.get(api_url)
    return response

def paths_json_prod_det(prod,det):
    """ Returns pathways from producible to detectable in JSON format"""
    api_url = urllib.parse.urljoin(url,"/".join(["api/json_paths",str(prod),str(det)]))
    response = requests.get(api_url)
    return response

def det_info(det):
    """ Returns Sensbio information about the detectable compound"""
    api_url = urllib.parse.urljoin(url,"/".join(["api/det_info",str(det)]))
    response = requests.get(api_url)
    return response

def pathways():
    """ Returns detectable pathways connected to producibles"""
    pathways = {}
    targets = prod()
    for compound in targets:
        detectables = det_prod(compound)
        pathways[compound] = {}
        for effector in detectables:
            pathways[compound][effector] = paths_json_prod_det(compound,effector)
    return pathways


print("DetSpace API usage by DBDL https://carbonelllab.org")
print(version())
p = prod()
print("Total producibles:",len(p))
d = det()
print("Total detectables:",len(d))
c = chassis()
print("Total chassis:",len(c))
# Select campesterol as product
for pr in p:
    if pr["Name"] == "Campesterol":
        break
# Get all effectors that can sense some product
d0 = det_prod(pr["ID"])
for de in d0:
    if de["Name"] == "Caffeoyl-coa":
        break
# Get all products that can be detected by some effector
p0 = prod_det(de["ID"])
# Get all paths in SBML format for a given pair product, effector
ps00 = paths_prod_det(pr["ID"],de["ID"])
# Get all paths in JSON format for a given pair product, effector
pj00 = paths_json_prod_det(pr["ID"],de["ID"])
# Get info about the caffeoyl-CoA transcription factor-based biosensor
bs = det_info(de["ID"])
