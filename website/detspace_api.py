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


print("DetSpace API usage by DBDL https://carbonelllab.org")
print(version())
p = prod()
print("Total producibles:",len(p))
d = det()
print("Total detectables:",len(d))
# Get all products that can be detected by some effector
p0 = prod_det(d[0]["ID"])
# Get all effectors that can sense some product
d0 = det_prod(p[0]["ID"])
