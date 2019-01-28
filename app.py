
""" RTUG - RUB to USD Graphs
	- plotting graphs of russian stock prices in USD to compensate for the long-run devaluation of the RUB.

    Copyright (C) 2019  Boris Kharitontsev 

    bkhsev@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>. """


# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import urllib2
import multipart
import pandas as pd
import csv
import datetime
import re
import plotly.plotly as py
from plotly.graph_objs import *
import webbrowser
import time
import email
import numpy as np
from stockstats import StockDataFrame

#SPLITS
split_stocks = ["SBER", "NVTK", "PHOR", "SBERP"]
split_ratios = {"SBER": 1000,
                "SBERP": 20,
                "NVTK": 1000,
                "PHOR": 10}
split_dates = {"SBER": datetime.date(2007, 7, 19),
               "SBERP": datetime.date(2007, 7, 19),
               "NVTK": datetime.date(2006, 8, 17),
               "PHOR": datetime.date(2012, 3, 25)}
#DATE
now = datetime.date.today()
before = datetime.date(2001, 1, 01)
def m(x):
	if x.month < 10:
		return "0" + str(x.month)
	else:
		return str(x.month)
def d(x):
	if x.day < 10:
		return "0" + str(x.day)
	else:
		return str(x.day)	



difference = now - before
diff = str(difference.days)


nmonth = m(now)
nyear = str(now.year)
nday = d(now)

bmonth = m(before)
byear = str(before.year)
bday = d(before)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(children=[
    
    dcc.Input(id='ticker', className = "H1", type='text', placeholder = "Ticker"),
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Div(id = "output-state"),
    


] )


@app.callback(Output('output-state', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('ticker', 'value')])
def update_output(n_clicks, input1):
    ticker = (str(input1)).upper()

    url = "http://export.rbc.ru/free/micex.0/free.fcgi?period=DAILY&tickers="+ticker+"&d1="+bday+"&m1="+bmonth+"&y1="+byear+"&d2="+nday+"&m2="+nmonth+"&y2="+nyear+"&lastdays="+diff+"&separator=,&data_format=EXCEL&header=1"
    
    g = urllib2.urlopen(url)
    data = g.read()
    with open("quotes.csv", "wb") as code:
   	    	code.write(data)

    quotes = pd.read_csv("quotes.csv")	
    quotes.drop(columns = ["TICKER", "WAPRICE"], inplace = True)
    quotes = quotes[pd.notnull(quotes.CLOSE) == True]


	

    url2 = "http://export.rbc.ru/free/cb.0/free.fcgi?period=DAILY&tickers=USD&d1="+bday+"&m1="+bmonth+"&y1="+byear+"&d2="+nday+"&m2="+nmonth+"&y2="+nyear+"&lastdays="+diff+"&separator=,&data_format=EXCEL&header=1"
    s = urllib2.urlopen(url2)
    data2 = s.read()
    with open("usd.csv", "wb") as code:
    		code.write(data2)

    usd = pd.read_csv("usd.csv")
    usd.drop(columns = ["TICKER", "OPEN", "HIGH", "LOW", "VOL", "WAPRICE", "NOMINAL"], inplace = True)
    usd.rename(columns = {"CLOSE" : "KURS"}, inplace = True)



    dates = pd.date_range(start=before, end=now)
    date = pd.DataFrame({"DATE":dates})
    date.DATE = date.DATE.astype(str)

    usd_all = pd.merge(date, usd, how = "left", on = "DATE")
    usd_all.fillna(method = "ffill", inplace = True) 





    #SPLITS CONT
    if ticker in split_stocks:


      dates_to_change = []
  

      mama_mia = pd.date_range(before, split_dates[ticker])
      for i in mama_mia:
        dates_to_change.append(str(i.date()))
        dates_to_change = sorted(dates_to_change)   

      quotes["CLOSE"] = quotes.apply(
        lambda x: x.CLOSE / split_ratios[ticker] if x.DATE in dates_to_change else x.CLOSE,
        axis = 1,
      )      








    final = pd.merge(quotes, usd_all, how = "left", on = "DATE")

    final["open_usd"] = final.OPEN / final.KURS
    final["high_usd"] = final.HIGH / final.KURS
    final["low_usd"] = final.LOW / final.KURS
    final["close_usd"] = final.CLOSE / final.KURS

    final.drop(columns = ["OPEN", "HIGH", "CLOSE", "LOW", "KURS"], inplace = True)

    

    final["AVG"] = final.close_usd.rolling(window=1260).mean()

    
    
    
    

    def cumvol(x):
	
    	a = '^' + x[:8] + "..$"
    	pattern = re.compile(a)
    	matches = [e for e in final.DATE if pattern.match(e)]
	
	

    	kukushka = 0 
    	for i in matches:
		
    		hleb = final.loc[final['DATE'] == i]["VOL"]
    		kukushka += hleb.sum()
		
	
    	return kukushka	


      


    df1 = final.tail(1)

    
    pricedf1 = df1.iloc[0]['close_usd']
    smadf1 = 0

    if pd.isnull(final["AVG"].iloc[-1]) == True:
      smadf1 = final["close_usd"].mean()
    else: 
      smadf1 = df1.iloc[0]['AVG']

    
    output = 0
    
    def calc():
    	if pricedf1 > smadf1:
    		output = int(-round(((pricedf1/smadf1-1)*100), 0))
		
    	else:
    		output = int(round(((smadf1/pricedf1-1)*100), 0))
    	return output


    o = str(calc()) + "%" 

    
    
	
    start_end_dates = []
	

    fm = pd.date_range(before, now, freq = "BM")
    for i in fm:
    	start_end_dates.append(str(i.date()))

    start_end_dates = sorted(start_end_dates)
	



    df2 = final[final.DATE.isin(start_end_dates)]




    df3 = pd.concat([df2, df1])
    
    
	
    df3.AVG.iloc[-1] = smadf1

    
    

    perc = lambda row: np.NaN if pd.isnull(row.AVG) == True else (int(-round(((row.close_usd/row.AVG-1)*100), 0)) if row.close_usd > row.AVG else (0 if row.close_usd == row.AVG else int(round(((row.AVG/row.close_usd-1)*100), 0))))


    df3["perc"] = df3.apply(perc, axis = 1)
    percentages = [str(x) for x in df3.perc]

    

    df3["cumvol"] = df3.DATE.apply(cumvol)

    lemor = df3[["open_usd", "high_usd", "low_usd", "close_usd", "VOL"]]
    rsi = lemor.rename(columns = {"open_usd": "Open",
                                "high_usd": "High",
                                "low_usd": "Low",
                                "close_usd": "Close",
                                "VOL": "Volume"
      })    

    stock_df = StockDataFrame.retype(rsi)

    check= stock_df["rsi_14"]
    
    deer = []

    for i in check:
      deer.append(i)
    

    df3["rsi"] = deer

    

    trace1 = {
  "x": df3.DATE, 
  "y": df3.close_usd, 
  "fill": "none", 
  "hoverinfo": "x+y", 
  "mode": "lines", 
  "name": "Price", 
  "type": "scatter"
}
    trace2 = {
  "x": df3.DATE, 
  "y": df3.AVG, 
  "fill": "none", 
  "hoverinfo": "x+y+text",
  "text": percentages,
  "line": {"color": "rgb(255, 38, 14)"}, 
  "marker": {"size": 3},
  "mode": "markers+lines", 
  "name": "SMA", 
  "type": "scatter"
}
    trace3 = {
  "x": df3.DATE, 
  "y": df3.cumvol, 
  "hoverinfo": "x+y", 
  "marker": {"color": "#2ca02c"}, 
  "name": "Volume", 
  "orientation": "v", 
  "type": "bar", 
  "xaxis": "x", 
  "yaxis": "y2" 
}


    trace4 = {
  "x": df3.DATE, 
  "y": df3.rsi, 
  "fill": "tozeroy",
  "fillcolor": "rgba(255, 255, 255, 0.5)", 
  "hoverinfo": "x+y", 
  "line": {"color": "rgb(106, 197, 227)"}, 
  "mode": "lines", 
  "name": "RSI", 
  "opacity": 1, 
  "type": "scatter",  
  "yaxis": "y3"
}

    data = Data([trace1, trace2, trace3, trace4])



    layout = {
  "height": 820,
  "autosize": True, 
  "dragmode": "orbit", 
  "showlegend": False,  
  "titlefont": {"family": "Arial"}, 
  "xaxis": {
    "anchor": "y3", 
    "automargin": False, 
    "autorange": True, 
    "domain": [0, 1], 
    "fixedrange": True,
    "range": [-0.5, 202.5], 
    "rangeslider": {
      "autorange": True, 
      "bgcolor": "rgb(183, 190, 196)", 
      "borderwidth": 2, 
      "range": [-0.5, 202.5], 
      "thickness": 0.01, 
      "visible": True, 
      "yaxis": {"rangemode": "match"}, 
      "yaxis2": {"rangemode": "match"},
      "yaxis3": {"rangemode": "match"}
    }, 
    "showline": False, 
    "showspikes": False,
    "showticklabels": False,  
    "titlefont": {
      "family": "Arial", 
      "size": 12
    }, 
    "type": "category"
  }, 
  "yaxis": {
    "autorange": True, 
    "domain": [0.375, 1], 
    "range": [-0.0143559820551, 4.6083293975], 
    "showspikes": False, 
    "side": "right", 
    "title": "Price", 
    "type": "linear"  
  }, 
  "yaxis2": {
    "autorange": True, 
    "domain": [0.1875, 0.375], 
    "overlaying": False, 
    "range": [0, 282853473.684], 
    "showspikes": False, 
    "side": "right", 
    "title": "Volume", 
    "type": "linear"
  },
  "yaxis3": {
    "autorange": True, 
    "domain": [0, 0.1875], 
    "overlaying": False, 
    "range": [-977026.555556, 18957504.5556], 
    "side": "right",
    "title": "RSI", 
    "type": "linear"
  }
}




    return html.H1(children = ticker), html.H3(children = o), dcc.Graph(
        id='my-graph',
        figure={
            'data': data,
            'layout': layout
            
        }
    )	









if __name__ == '__main__':
    app.run_server(debug=True)
    








