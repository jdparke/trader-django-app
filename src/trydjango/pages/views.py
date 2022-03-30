import numpy as np 
# Allows for further data manipulation and analysis
import pandas as pd 
import matplotlib.pyplot as plt # Plotting
import matplotlib.dates as mdates # Styling dates

import datetime as dt # For defining dates

import time

# In Powershell Prompt : conda install -c conda-forge multitasking
# pip install -i https://pypi.anaconda.org/ranaroussi/simple yfinance

import yfinance as yf

# To show all your output File -> Preferences -> Settings Search for Notebook
# Notebook Output Text Line Limit and set to 100

# Used for file handling like deleting files
import os

# conda install -c conda-forge cufflinks-py
# conda install -c plotly plotly
import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go

# Make Plotly work in your Jupyter Notebook
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)
# Use Plotly locally
cf.go_offline()

from plotly.subplots import make_subplots

import os
from os import listdir
from os.path import isfile, join

from menus.models import Menu

from django.shortcuts import render

import hmac
from hashlib import sha1

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from django.views.decorators.http import require_POST
from git import Repo

import requests
from ipaddress import ip_address, ip_network

# Create your views here.

def home_view(request, *args, **kwargs):
    #return HttpResponse("<h1>Hello World</h1>")
    menu_list = Menu.objects.all().order_by('iOrder')
    my_context = {
        "my_test": "W'sup hommies!",
        "my_number": 123,
        "my_list": [4, 5, 6],
        "menu_list": menu_list
    }
    return render(request, "home.html", my_context)


def contact_view(request, *args, **kwargs):
    return render(request, "contact.html", {})

@require_POST
@csrf_exempt
def handle_github_hook(request):

    # # Verify if request came from GitHub
    # forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    # client_ip_address = ip_address(forwarded_for)
    # whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    # for valid_ip in whitelist:
    #     if client_ip_address in ip_network(valid_ip):
    #         break
    # else:
    #     return HttpResponseForbidden('Permission denied.')

    # return HttpResponse('pong')


    # Verify if request came from GitHub
    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape

    # Process the GitHub events
    # event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    # if event == 'ping':
    #     return HttpResponse('pong')
    # elif event == 'push':
    #     # Deploy some code for example
    #     repo = Repo(settings.REPO_PATH)
    #     origin = repo.remotes.origin
    #     origin.pull('--rebase')

    #     commit = request.json['after'][0:6]
    #     print('Repository updated with commit {}'.format(commit))
    #     return HttpResponse('success')

    #In case we receive an event that's not ping or push
    return HttpResponse(status=204)