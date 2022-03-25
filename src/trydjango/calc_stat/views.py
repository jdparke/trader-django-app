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

def ajax_calc_stat(request):
    if request.is_ajax and request.method == "POST":

        global PATH
        PATH = os.getcwd() + "/Stocks/"

        ticker = request.POST.get('ticker_val')
        # Start end date defaults
        S_DATE = "2017-02-01"
        E_DATE = "2022-12-06"
        S_DATE_DT = pd.to_datetime(S_DATE)
        E_DATE_DT = pd.to_datetime(E_DATE)

        save_to_csv_from_yahoo(PATH, ticker)

        new_df = get_stock_df_from_csv(ticker)
        new_df = add_daily_return_to_df(new_df)
        new_df = add_cum_return_to_df(new_df)
        new_df = add_bollinger_bands(new_df)
        new_df = add_Ichimoku(new_df)
        new_df.to_csv(PATH + ticker + '.csv')

        data = {'message': ticker, 'code': 'SUCCESS'}

        return JsonResponse(data, status=200)
    else:
        return JsonResponse({"error": ""}, status=400)

# Create your views here.
def download_view(request, *args, **kwargs):
    current_dir = os.getcwd()
    tickers = get_column_from_csv("Wilshire-5000-Stocks.csv", "Ticker")
    tickers_json = tickers.to_json(orient="values")
    obj = Menu.objects.all().order_by('iOrder')

    context = {
        'menu_list': obj,
        "tickers": tickers,
        "tickers_json": tickers_json,
    }
    #print("context: ", context)
    return render(request, "download.html", context)


def get_column_from_csv(file, col_name):
    # Try to get the file and if it doesn't exist issue a warning
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print("File Doesn't Exist")
    else:
        return df[col_name]



def save_to_csv_from_yahoo(folder, ticker):
    stock = yf.Ticker(ticker)
    
    try:
        print("Get Data for : ", ticker)
        # Get historical closing price data
        df = stock.history(period="5y")
    
        # Wait 2 seconds
        #time.sleep(2)
        
        # Remove the period for saving the file name
        # Save data to a CSV file
        # File to save to 
        the_file = folder + ticker.replace(".", "_") + '.csv'
        print(the_file, " Saved")
        df.to_csv(the_file)
    except Exception as ex:
        print("Exception: ", ex)
        print("Couldn't Get Data for :", ticker)
        
def get_stock_df_from_csv(ticker):
    
    # Try to get the file and if it doesn't exist issue a warning
    try:
        df = pd.read_csv(PATH + ticker + '.csv', index_col=0)
    except FileNotFoundError:
        print("File Doesn't Exist")
    else:
        return df
        

# Shift provides the value from the previous day
# NaN is displayed because there was no previous day price for the 1st calculation
def add_daily_return_to_df(df):
    df['daily_return'] = (df['Close'] / df['Close'].shift(1)) - 1
    return df  

def add_cum_return_to_df(df):
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    return df

# Here we will add a middle band (20 days), upper band (20 days + 1.96 std),
# and lower band (20 days - 1.96 std)
def add_bollinger_bands(df):
    df['middle_band'] = df['Close'].rolling(window=20).mean()
    df['upper_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=20).std()
    df['lower_band'] = df['middle_band'] - 1.96 * df['Close'].rolling(window=20).std()
    return df

def add_Ichimoku(df):
    # Conversion
    hi_val = df['High'].rolling(window=9).max()
    low_val = df['Low'].rolling(window=9).min()
    df['Conversion'] = (hi_val + low_val) / 2

    # Baseline
    hi_val2 = df['High'].rolling(window=26).max()
    low_val2 = df['Low'].rolling(window=26).min()
    df['Baseline'] = (hi_val2 + low_val2) / 2

    # Spans
    df['SpanA'] = ((df['Conversion'] + df['Baseline']) / 2).shift(26)
    hi_val3 = df['High'].rolling(window=52).max()
    low_val3 = df['Low'].rolling(window=52).min()
    df['SpanB'] = ((hi_val3 + low_val3) / 2).shift(26)
    df['Lagging'] = df['Close'].shift(-26)
    return df        