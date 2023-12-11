from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, Http404

from .models import Target
import os
# import pandas
import distutils.dir_util

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

