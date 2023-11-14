from django.shortcuts import render
from django.core.mail import send_mail
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



