import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
from dash.exceptions import PreventUpdate

import flask
from flask import Flask
import pandas as pd
import dateutil.relativedelta
from datetime import date
import datetime
import yfinance as yf
import numpy as np
import praw

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash_utils import make_table, make_card, ticker_inputs, make_item
#from reddit_data import get_reddit
#from tweet_data import get_options_flow
#from fin_report_data import get_financial_report #, get_financial_reportformatted

from google_extractor import *
from technical_indicators_utils import *

server = Flask(__name__)
app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])

app.config.suppress_callback_exceptions = True

df_google = pd.DataFrame(data = [], columns = ["google_title", "link"])
global n_clicks_google
n_clicks_google = 0


layout1 = html.Div([
        # html.Div(id = 'cards')


                dbc.Row([dbc.Col(make_card("Enter Ticker", "success", ticker_inputs('ticker-input', 'date-picker', 36)))]) #row 1
                , dbc.Row([make_card("select ticker", "warning", "select ticker")],id = 'cards') #row 2

                , dbc.Row([dbc.Alert("________________________Technical indicators________________________", color="primary")], justify = 'center')
                , dbc.Row([make_card("select ticker", "warning", "select ticker for technical graphs")], id='technical_graphs')

                , dbc.Row([dbc.Col([make_card("Google Order Flow", 'primary', [html.P(html.Button('Refresh', id='refresh_google')), make_table('table-sorting-filtering2', df_google, '17px', 10)])])
                        #,dbc.Col([make_card("Fin table ", "secondary", html.Div(id="fin-table"))])
                        ]) #row 3

                    ]) #end div

app.layout= layout1


@app.callback(Output('cards', 'children'),
[Input('ticker-input', 'value')])
def refresh_cards(ticker):
        print("refresh_cards")
        ticker = ticker.upper()
        if ticker is None:
                TICKER = 'MSFT'
        else:
                TICKER = yf.Ticker(ticker)

        cards = [ dbc.Col(make_card("Previous Close ", "secondary", TICKER.info['previousClose']))
                        , dbc.Col(make_card("Open", "secondary", TICKER.info['open']))
                        , dbc.Col(make_card("Sector", 'secondary', TICKER.info['sector']))
                        , dbc.Col(make_card("Beta", 'secondary', TICKER.info['beta']))
                        , dbc.Col(make_card("50d Avg Price", 'secondary', TICKER.info['fiftyDayAverage']))
                        , dbc.Col(make_card("Avg 10d Vol", 'secondary', TICKER.info['averageVolume10days']))
                        ] #end cards list
        return cards

@app.callback(Output('technical_graphs', 'children'),
[Input('ticker-input', 'value')
, Input('date-picker', 'start_date')
, Input('date-picker', 'end_date')
])
def create_technical_graphs(ticker,startdate, enddate):
        print("create_technical_graphs")
        ticker = ticker.upper()
        df_tech = yf.download(ticker,startdate, enddate+dateutil.relativedelta.relativedelta(days=1))
        print(len(df_tech))
        df_tech.reset_index(inplace=True)
        print(df_tech)
        df_tech = df_indicators_columns(df_tech)
        print(df_tech)
        fig1 = graph_Bollinger(df_tech)
        fig2 = graph_CCI(df_tech)
        fig3 = graph_ADX(df_tech)

        graphs = dbc.Row([
                            dcc.Graph(figure = fig1)
                            , dcc.Graph(figure = fig2)
                            , dcc.Graph(figure = fig3)
                            ], className="graphs")

        #plotly.offline.plot(fig1, filename='C:/Users/Usuario/Documents/Locus/Finances/dash_stocks/fig1.html')
        #plotly.offline.plot(fig2, filename='C:/Users/Usuario/Documents/Locus/Finances/dash_stocks/fig2.html')
        #plotly.offline.plot(fig3, filename='C:/Users/Usuario/Documents/Locus/Finances/dash_stocks/fig3.html')
        return graphs

#@app.callback(
#    Output('tweets', 'children'),
#    [Input('interval-component2', 'n_intervals'),
#     ])
#def new_tweets(n):
#        get_options_flow()
#        return html.P(f"Reloaded Tweets {n}")

@app.callback(
    Output('table-sorting-filtering2', 'data'),
    [Input('ticker-input', 'value')
    , Input('refresh_google', 'n_clicks')]
    )
def update_table2(ticker, n_clicks):
    global n_clicks_google
    n_clicks_google = n_clicks_google

    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks>n_clicks_google:
        n_clicks_google = n_clicks
        name = yf.Ticker(ticker)

        name = name.info['longName']
        print("update_table2")
        df_google = news_dataframe(name)
        df_google = df_google.to_dict('records')
        return df_google
    else:
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug = False)
