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

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render

from menus.models import Menu
import json


def ajax_sector(request):

	if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":

		obj = Menu.objects.all().order_by('iOrder')
		global PATH
		PATH = os.getcwd() 

		sec_df = pd.read_csv(PATH + "/big_stock_sectors.csv")

		discretion_df = sec_df.loc[sec_df['Sector'] == "Discretionary"]
		utility_df = sec_df.loc[sec_df['Sector'] == "Utilities"]
		financial_df = sec_df.loc[sec_df['Sector'] == "Financials"]
		material_df = sec_df.loc[sec_df['Sector'] == "Materials"]
		restate_df = sec_df.loc[sec_df['Sector'] == "Real Estate"]
		energy_df = sec_df.loc[sec_df['Sector'] == "Energy"]

		discretion = get_cum_ret_for_stocks(discretion_df)
		utility = get_cum_ret_for_stocks(utility_df)
		finance = get_cum_ret_for_stocks(financial_df)
		material = get_cum_ret_for_stocks(material_df)
		restate = get_cum_ret_for_stocks(restate_df)
		energy = get_cum_ret_for_stocks(energy_df)

		discretionSorted = discretion.sort_values(by=['CUM_RET'], ascending=False).head(20)
		utilitySorted = utility.sort_values(by=['CUM_RET'], ascending=False).head(20)
		financeSorted = finance.sort_values(by=['CUM_RET'], ascending=False).head(20)
		materialSorted = material.sort_values(by=['CUM_RET'], ascending=False).head(20)
		restateSorted = restate.sort_values(by=['CUM_RET'], ascending=False).head(20)
		energySorted = energy.sort_values(by=['CUM_RET'], ascending=False).head(20)

		data = {
			'discretion': json.loads(discretionSorted.to_json(orient='records')),
			'utility': json.loads(utilitySorted.to_json(orient='records')),
			'finance': json.loads(financeSorted.to_json(orient='records')),
			'material': json.loads(materialSorted.to_json(orient='records')),
			'restate': json.loads(restateSorted.to_json(orient='records')),
			'energy': json.loads(energySorted.to_json(orient='records'))
		}
		return JsonResponse(data, status=200)
	else:
		return JsonResponse({"error": ""}, status=400)

def sector_view(request, *args, **kwargs):
	obj = Menu.objects.all().order_by('iOrder')
	global PATH
	PATH = os.getcwd() 

	sec_df = pd.read_csv(PATH + "/big_stock_sectors.csv")

	indus_df = sec_df.loc[sec_df['Sector'] == "Industrial"]
	health_df = sec_df.loc[sec_df['Sector'] == "Healthcare"]
	it_df = sec_df.loc[sec_df['Sector'] == "Information Technology"]
	comm_df = sec_df.loc[sec_df['Sector'] == "Communication"]
	staple_df = sec_df.loc[sec_df['Sector'] == "Staples"]

	industrial = get_cum_ret_for_stocks(indus_df)
	health_care = get_cum_ret_for_stocks(health_df)
	it = get_cum_ret_for_stocks(it_df)
	commun = get_cum_ret_for_stocks(comm_df)
	staple = get_cum_ret_for_stocks(staple_df)

	industrialSorted = industrial.sort_values(by=['CUM_RET'], ascending=False).head(20)
	healthCareSorted = health_care.sort_values(by=['CUM_RET'], ascending=False).head(20)
	itSorted = it.sort_values(by=['CUM_RET'], ascending=False).head(20)
	communSorted = commun.sort_values(by=['CUM_RET'], ascending=False).head(20)
	stapleSorted = staple.sort_values(by=['CUM_RET'], ascending=False).head(20)

	context = {
		'menu_list': obj,
		'industrial': json.loads(industrialSorted.to_json(orient='records')),
		'healthcare': json.loads(healthCareSorted.to_json(orient='records')),
		'it': json.loads(itSorted.to_json(orient='records')),
		'commun': json.loads(communSorted.to_json(orient='records')),
		'staple': json.loads(stapleSorted.to_json(orient='records')),
	}	

	return render(request, "sector.html", context)

def get_column_from_csv(file, col_name):
    # Try to get the file and if it doesn't exist issue a warning
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print("File Doesn't Exist")
    else:
        return df[col_name]

# Reads a dataframe from the CSV file, changes index to date and returns it
def get_stock_df_from_csv(ticker):
    
    # Try to get the file and if it doesn't exist issue a warning
    try:
        df = pd.read_csv(PATH + '/Stocks/' + ticker + '.csv', index_col=0)
    except FileNotFoundError:
        #print("File Doesn't Exist, tried ticker: ", ticker)
        hello = "test"
    else:
        return df

def get_cum_ret_for_stocks(stock_df):
    tickers = []
    cum_rets = []

    for index, row in stock_df.iterrows():
        df = get_stock_df_from_csv(row['Ticker'])
        if df is None:
            pass
        else:
            tickers.append(row['Ticker'])
            try:
                cum = df['cum_return'].iloc[-1]
                #print("Ticker: " + row['Ticker'] + " | Cumulative Return: " + str(cum))
                cum_rets.append(cum)
            except:
                #print("An exception occured")
                cum_rets.append(0)
    #print("Tickers", len(tickers))
    #print("cum_returns", len(cum_rets))
    return pd.DataFrame({'Ticker':tickers, 'CUM_RET':cum_rets})

