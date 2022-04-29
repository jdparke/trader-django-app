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
import plotly
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


def ajax_portfolio(request):

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":

        # Start end date defaults
        S_DATE = '2017-02-01'
        E_DATE = '2022-12-06'
        S_DATE_DT = pd.to_datetime(S_DATE)
        E_DATE_DT = pd.to_datetime(E_DATE)

        risk_free_rate = 0.0125 # Approximate 10 year bond rate

        port_list = json.loads(request.POST.get('port_list'))
        global num_stocks
        num_stocks = len(port_list)

        obj = Menu.objects.all().order_by('iOrder')

        global PATH
        PATH = os.getcwd() + "/Stocks/"

        mult_df = merge_df_by_column_name('Close',  S_DATE, E_DATE, *port_list)
        mult_cum_df = merge_df_by_column_name('cum_return',  S_DATE, E_DATE, *port_list)

        # Plot out prices for each stock since beginning of 2017
        fig = px.line(mult_df, x=mult_df.index, y=mult_df.columns)
        fig.update_xaxes(title="Date", rangeslider_visible=True)
        fig.update_yaxes(title="Price")
        fig.update_layout(height=1200, width=1800, showlegend=True)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Plot out cumulative returns for each stock since beginning of 2017
        fig2 = px.line(mult_cum_df, x=mult_cum_df.index, y=mult_cum_df.columns)
        fig2.update_xaxes(title="Date", rangeslider_visible=True)
        fig2.update_yaxes(title="Price")
        fig2.update_layout(height=1200, width=1800, showlegend=True)
        cum_retJSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

        #Mean returns
        returns = np.log(mult_df / mult_df.shift(1))
        mean_ret = returns.mean() * 252 # 252 average trading days per year
        correlation = returns.corr()

        get_random_weights(risk_free_rate, returns)

        # Return the index of the largest Sharpe Ratio
        SR_idx = np.argmax(p_SR)

        # Find the ideal portfolio weighting at that index
        i = 0
        bestSharpeRatio = {}
        while i < num_stocks:
            bestSharpeRatio[port_list[i]] = (p_wt[SR_idx][i] * 100)
            i += 1
        
        print("bestSharpeRatio:", bestSharpeRatio)

        # Find volatility of that portfolio
        print("\nVolatility :", p_vol[SR_idx])
            
        # Find return of that portfolio
        print("Return :", p_ret[SR_idx])

        data = {
           "merged_data": json.loads(mult_df.to_json(orient='records')),
           "mult_cum_df": json.loads(mult_cum_df.to_json(orient='records')),
           "graph_json": graphJSON,
           "graph_cum_ret_json": cum_retJSON,
           "mean_ret": json.loads(mean_ret.to_json(orient='records')),
           "correlation": json.loads(correlation.to_json(orient='records')),
           "bestSharpeRatio": bestSharpeRatio,
           "volatility": p_vol[SR_idx],
           "return": p_ret[SR_idx]
        }
        return JsonResponse(data, status=200)
    else:
        return JsonResponse({"error": ""}, status=400)


def portfolio_view(request, *args, **kwargs):
    obj = Menu.objects.all().order_by('iOrder')
    tickers = get_stock_df_from_csv_no_path("Wilshire-5000-Stocks.csv")
    tickers_json = tickers.to_json(orient="records")

    context = {
        'menu_list': obj,
        'tickers_json': tickers_json
    }

    return render(request, "portfolio.html", context)

def get_stock_df_from_csv_no_path(file):
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print("File Doesn't Exist")
    else:
        return df

def get_stock_df_from_csv(ticker):
    
    # Try to get the file and if it doesn't exist issue a warning
    try:
        df = pd.read_csv(PATH + ticker + '.csv', index_col=0)
    except FileNotFoundError:
        print("File Doesn't Exist")
    else:
        return df

def merge_df_by_column_name(col_name, sdate, edate, *tickers):
    # Will hold data for all dataframes with the same column name
    mult_df = pd.DataFrame()
    
    for x in tickers:
        df = get_stock_df_from_csv(x)
        
        # NEW Check if your dataframe has duplicate indexes
        # if not df.index.is_unique:
        #     # Delete duplicates 
        #     df = df.loc[~df.index.duplicated(), :]
        
        mask = (df.index >= sdate) & (df.index <= edate)
        mult_df[x] = df.loc[mask][col_name]
        
    return mult_df

def get_random_weights(risk_free_rate, returns):
  
    global p_ret
    global p_vol
    global p_SR
    global p_wt
    
    p_ret_arr = [] # Returns list
    p_vol_arr = [] # Volatility list
    p_SR_arr = [] # Sharpe Ratio list
    p_wt_arr = [] # Stock weights list

    for x in range(1000):
        # Generate random weights
        p_weights = np.random.random(num_stocks)
        p_weights /= np.sum(p_weights)
        
        # Add return using those weights to list
        ret_1 = np.sum(p_weights * returns.mean()) * 252
        p_ret_arr.append(ret_1)
        
        # Add volatility or standard deviation to list
        vol_1 = np.sqrt(np.dot(p_weights.T, np.dot(returns.cov() * 252, p_weights)))
        p_vol_arr.append(vol_1)
        
        # Get Sharpe ratio
        SR_1 = (ret_1 - risk_free_rate) / vol_1
        p_SR_arr.append(SR_1)
        
        # Store the weights for each portfolio
        p_wt_arr.append(p_weights)
        
        # Convert to Numpy arrays
        p_ret = np.array(p_ret_arr)
        p_vol = np.array(p_vol_arr)
        p_SR = np.array(p_SR_arr)
        p_wt = np.array(p_wt_arr)

