# -*- coding: utf-8 -*-

""" RTUG - RUB to USD Graphs
    - plotting graphs of russian stock prices in USD to compensate for the long-run devaluation of the RUB.

    Copyright © 2019  Boris Kharitontsev 

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



#Imports regarding GUI and Graphing
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.plotly as py
from plotly.graph_objs import *

#Imports regarding data management
import urllib2
import csv
import pandas as pd
import numpy as np
import datetime
import re

#An import for financial indicators
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


#Setting releveant dates in Datetime module format

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



#Declaring an app usinf Dash


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)




# App Layout

app.layout = html.Div(children = [

   html.H2("RUB To USD Graphs"),

   html.H6("Ticker:", style = {'width': '5%', 'display': 'inline-block'}),

   html.Div(" ", style = {'width': '10%', 'display': 'inline-block'}),

   html.H6("RSI:", style = {'width': '10%', 'display': 'inline-block'}),

   html.Div(" ", style = {'width': '5%', 'display': 'inline-block'}),

   html.H6("Choose an interval:", style = {'width': '70%', 'display': 'inline-block'}),




   dcc.Input(id='ticker', className = 'H1', type = 'text', size = "6", placeholder = 'Ticker', style = {'width': '5%', 'display': 'inline-block'}),

   html.Div(" ", style = {'width': '10%', 'display': 'inline-block'}),

   dcc.Input(id='rsi', className = 'H3', type = 'text', placeholder = 'RSI', value = '14', style = {'width': '5%', 'display': 'inline-block'}),

   html.Div(" ", style = {'width': '10%', 'display': 'inline-block'}),
   
   dcc.RadioItems(id = 'monthly',
        options=[
            {'label': "Monthly", 'value': "monthly"},
            {'label': "Weekly", 'value': "weekly"}
], value = 'monthly', style = {'width': '70%', 'display': 'inline-block', 'align': 'centre'}),
   

   dcc.Graph(id = "my-graph"),

   html.Div('Copyright © 2019  Boris Kharitontsev'),
   html.Div('bkhsev@gmail.com')

   ])

#Input the ticker above, start preparing data





@app.callback(
    Output('my-graph', 'figure'),
    [Input('ticker', 'n_submit'), Input('monthly', 'value'), Input('rsi', 'n_submit')],
    [State('ticker', 'value'), State('rsi', 'value')])
def update_output_1(ns1, input2, ns2, input1, input3):
   ticker = (str(input1)).upper()

    

   #downloading wtock quotes in RUB. Some initial pre-processing of the data.

   url = "http://export.rbc.ru/free/micex.0/free.fcgi?period=DAILY&tickers="+ticker+"&d1="+bday+"&m1="+bmonth+"&y1="+byear+"&d2="+nday+"&m2="+nmonth+"&y2="+nyear+"&lastdays="+diff+"&separator=,&data_format=EXCEL&header=1"
   g = urllib2.urlopen(url)
   data = g.read()
   with open("quotes.csv", "wb") as code:
             code.write(data)

   quotes = pd.read_csv("quotes.csv")   
   quotes.drop(columns = ["TICKER", "WAPRICE"], inplace = True)
   quotes = quotes[pd.notnull(quotes.CLOSE) == True]


    #downloading RUB/USD quotes, pre-processing.
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




    #Manually processing splits.
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




    #Changing the prices from RUB to USD, using the date as a basis for correlation.

   final = pd.merge(quotes, usd_all, how = "left", on = "DATE")

   final["open_usd"] = final.OPEN / final.KURS
   final["high_usd"] = final.HIGH / final.KURS
   final["low_usd"] = final.LOW / final.KURS
   final["close_usd"] = final.CLOSE / final.KURS

   final.drop(columns = ["OPEN", "HIGH", "CLOSE", "LOW", "KURS"], inplace = True)
 
    

    #adding total volume per last 5 days
   final["cumvol"] = final.VOL.rolling(window = 5).sum()

    #The most recent day i.e. representation for current week/month

   df1 = final.tail(1)


    #Creates a list of dates of each of the month ends in a range from 01/01/2001 till today.
   month_end_dates = []


   fm = pd.date_range(before, now, freq = "BM")
   for i in fm:
       month_end_dates.append(str(i.date()))

   month_end_dates = sorted(month_end_dates)


    #Creates a list of dates of each of the week ends in the range above

   week_end_dates = []

   weird_variable  = pd.date_range(before, now, freq = "W-FRI")

   for i in weird_variable:
       week_end_dates.append(str(i.date()))

   week_end_dates = sorted(week_end_dates)



    #Dataframe with monthly quotes (DF3 previously)
   m_quotes = final[final.DATE.isin(month_end_dates)]

   m_quotes_u = pd.concat([m_quotes, df1])

    #Dataframe with weekly quotes
   w_quotes = final[final.DATE.isin(week_end_dates)]

   w_quotes_u = pd.concat([w_quotes, df1])


    #adding SMA-60

   m_quotes_u["AVG"] = m_quotes_u.close_usd.rolling(window = 60).mean()
   w_quotes_u["AVG"] = w_quotes_u.close_usd.rolling(window = 60).mean()

    #adding total volume per month

   def monthly_vol(x):
   
       a = '^' + x[:8] + "..$"
       pattern = re.compile(a)
       matches = [e for e in final.DATE if pattern.match(e)]
   
   

       kukushka = 0 
       for i in matches:
   
           hleb = final.loc[final['DATE'] == i]["VOL"]
       kukushka += hleb.sum()
   
   
       return kukushka   




   m_quotes_u.drop(columns = ["cumvol"], inplace = True)
   m_quotes_u["cumvol"] = m_quotes_u.DATE.apply(monthly_vol)

    # For weekly volume, please see column cumvol_w in any dataframe. Managed at line 190.


    #managing the PERCENT value
   current_price = df1.iloc[0]['close_usd']

   sma_60_m = 0 
   sma_60_w = 0


   if pd.isnull(m_quotes_u["AVG"].iloc[-1]) == True:
      sma_60_m = m_quotes_u["close_usd"].mean()
   else: 
      sma_60_m = m_quotes_u.iloc[-1]['AVG']



   if pd.isnull(w_quotes_u["AVG"].iloc[-1]) == True:
      sma_60_w = w_quotes_u["close_usd"].mean()
   else: 
      sma_60_w = w_quotes_u.iloc[-1]['AVG']



   output = 0

   def calc(price, sma):
        if price > sma:
            output = int(-round(((price/sma-1)*100), 0))
        
        else:
            output = int(round(((sma/price-1)*100), 0))
        return output


   current_perc_m = str(calc(current_price, sma_60_m)) + "%"
   current_perc_w = str(calc(current_price, sma_60_w)) + "%"

    # In case we have historical data for less than 60 weeks/months, 
    # set SMA equal to the mean of all available data

   m_quotes_u.AVG.iloc[-1] = sma_60_m
   w_quotes_u.AVG.iloc[-1] = sma_60_w


    #Creating "PERCENT" values for all data points where both price and SMA are available
   perc = lambda row: np.NaN if pd.isnull(row.AVG) == True else (int(-round(((row.close_usd/row.AVG-1)*100), 0)) if row.close_usd > row.AVG else (0 if row.close_usd == row.AVG else int(round(((row.AVG/row.close_usd-1)*100), 0))))

   m_quotes_u["perc"] = m_quotes_u.apply(perc, axis = 1)
   w_quotes_u["perc"] = w_quotes_u.apply(perc, axis = 1)

   m_percentages = [str(x) for x in m_quotes_u.perc]
   w_percentages = [str(x) for x in w_quotes_u.perc]

    #Managing RSI

   lemor_m = m_quotes_u[["open_usd", "high_usd", "low_usd", "close_usd", "VOL"]]
   lemor_w = w_quotes_u[["open_usd", "high_usd", "low_usd", "close_usd", "VOL"]]

   rsi_m = lemor_m.rename(columns = {"open_usd": "Open",
                                "high_usd": "High",
                                "low_usd": "Low",
                                "close_usd": "Close",
                                "VOL": "Volume"
      })

   rsi_w = lemor_w.rename(columns = {"open_usd": "Open",
                                "high_usd": "High",
                                "low_usd": "Low",
                                "close_usd": "Close",
                                "VOL": "Volume"
      })

    
   stock_df_m = StockDataFrame.retype(rsi_m)
   stock_df_w = StockDataFrame.retype(rsi_w)

    #need to create a variable for the rsi category here, but for now it's rsi-14
   which_rsi = "rsi_" + str(input3)
   check_m = stock_df_m[which_rsi]
   check_w = stock_df_w[which_rsi]

   deer_m = []
   deer_w = []

   for i in check_m:
        deer_m.append(i)

   for i in check_w:
        deer_w.append(i)


   m_quotes_u["rsi"] = deer_m
   w_quotes_u["rsi"] = deer_w


    #seting default graph settings
   
   

   name_to_df = {"monthly": m_quotes_u,
         "weekly": w_quotes_u}

   name_to_perc = {"monthly": current_perc_m,
                    "weekly": current_perc_w}

   name_to_percentages = {"monthly": m_percentages,
                           "weekly": w_percentages}

   
   df_to_use = name_to_df[input2]
   perc_to_use = name_to_perc[input2]
   percentages_to_use = name_to_percentages[input2]


   trace1 = {
  "x": df_to_use.DATE, 
  "y": df_to_use.close_usd, 
  "fill": "none", 
  "hoverinfo": "x+y", 
  "mode": "lines", 
  "name": "Price", 
  "type": "scatter"
}
   trace2 = {
  "x": df_to_use.DATE, 
  "y": df_to_use.AVG, 
  "fill": "none", 
  "hoverinfo": "x+y+text",
  "text": percentages_to_use,
  "line": {"color": "rgb(255, 38, 14)"}, 
  "marker": {"size": 3},
  "mode": "lines", 
  "name": "SMA", 
  "type": "scatter"
}
   trace3 = {
  "x": df_to_use.DATE, 
  "y": df_to_use.cumvol, 
  "hoverinfo": "x+y", 
  "marker": {"color": "#2ca02c"}, 
  "name": "Volume", 
  "orientation": "v", 
  "type": "bar", 
  "xaxis": "x", 
  "yaxis": "y2" 
}


   trace4 = {
  "x": df_to_use.DATE, 
  "y": df_to_use.rsi, 
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





   return  {'data': data,
            'layout': layout}
         






if __name__ == '__main__':
    app.run_server(debug=True)









