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
from time import sleep

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash_utils import *
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
boxes_dropdown_options = [{"label":"daily", "value":"1d"},
                        {"label":"weekly", "value":"1wk"},
                        {"label":"monthly", "value":"1mo"}
                        ]
df_boxes = pd.DataFrame(columns = ["Open", "High", "Low", "Close"])
#df_boxes = yf.download("ADMP", "2020-01-27", "2021-02-27", interval = "1wk")



layout1 = html.Div([
        # html.Div(id = 'cards')


                dbc.Row([dbc.Col(make_card("Enter Ticker", "success", ticker_inputs('ticker-input', 'date-picker', 36)))])
                , dcc.Loading(
                            id="loading-cards",
                            type="default",
                            children=dbc.Row([make_card("select ticker", "warning", "select ticker")],id = 'cards', style={"margin-top":"2%", "margin-left":"1%"}))

                , dbc.Row([dbc.Alert("________________________Technical indicators________________________", color="primary")], justify = 'center', style={"margin-top":"2%"})
                , html.Div(id='tech-df', style={'display': 'none'})
                , dbc.Row([
                            dbc.Col([
                                    dcc.Input(id = "bollinger-days", type="number", value=30, placeholder="Select # days analysis", style={"margin-top":"1%", "margin-left":"1%"})
                                    , dcc.Loading(
                                                id="loading-bollinger",
                                                type="graph",
                                                children=dcc.Graph(id="bollinger-graph", figure=go.Figure(layout = {"title": "Bollinger bands"})))
                                    ])

                            , dbc.Col([
                                    dcc.Input(id = "CCI-days", type="number", value=30, placeholder="Select # days rolling deviation", style={"margin-top":"1%", "margin-left":"1%"})
                                    , dcc.Loading(
                                                id="loading-CCI",
                                                type="graph",
                                                children=dcc.Graph(id="CCI-graph", figure=go.Figure(layout = {"title": "CCI"})))
                                    ])

                            , dbc.Col([
                                    dcc.Loading(
                                                id="loading-ADX",
                                                type="graph",
                                                children=dcc.Graph(id="ADX-graph", figure=go.Figure(layout = {"title": "ADX"})))
                                    ])
                            ])

                , dbc.Row([
                            dbc.Col([boxes_dropdown(id="boxes-dropdown", options=boxes_dropdown_options, value="1wk")
                                    , dbc.Label("Periods rolling avg", style={"margin-top":"5%", "margin-left":"1%"})
                                    , dcc.Input(id = "boxes-period", type="number", value=10, placeholder="Select # periods", style={"margin-top":"1%", "margin-left":"1%"})
                                    , dbc.Label("Periods comparison rolling avg", style={"margin-top":"2%", "margin-left":"1%"})
                                    , dcc.Input(id = "boxes-comparison", type="number", value=5, placeholder="Select # comparison periods", style={"margin-top":"1%", "margin-left":"1%"})
                                    , dbc.Label("Periods variation open vs close (Var)", style={"margin-top":"2%", "margin-left":"1%"})
                                    , dcc.Input(id = "boxes-variation", type="number", value=10, placeholder="Select # variation periods", style={"margin-top":"1%", "margin-left":"1%"})
                                    , dbc.Button("Update volatility analysis", id="boxes-button", color="secondary", style={"margin-top":"8%", "margin-left":"1%"})
                                    ], width=2, align = 'center'
                                )
                        , dbc.Col(
                                dcc.Loading(
                                            id="loading-boxes",
                                            type="graph",
                                            children=dcc.Graph(id="boxes-graph", figure=go.Figure(layout = {"title": "Volatility analysis"}))), width=10)

                        ], justify = 'center')

                , dcc.Loading(
                            id="loading-google",
                            type="cube",
                            children=dbc.Row([dbc.Col([make_card("Google News, Forecasts, Analysis", 'primary', [html.P(dbc.Button('Refresh', color="secondary", id='google-button')), make_table('table-sorting-filtering2', df_google, '17px', 10)])])])
                            )
                    ]) #end div

def serve_layout():
    return layout1

app.layout= serve_layout


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
@app.callback(Output('tech-df', 'children'),
[Input('ticker-input', 'value')
, Input('date-picker', 'start_date')
, Input('date-picker', 'end_date')
])
def create_technical_df(ticker,startdate, enddate):
    print("create_technical_df")
    print("dates", startdate, enddate)
    try:
        ticker = ticker.upper()
        df_tech = yf.download(ticker,startdate, enddate)
        df_tech.reset_index(inplace=True)
    except:
        sleep(2)
        ticker = ticker.upper()
        df_tech = yf.download(ticker,startdate, enddate)
        df_tech.reset_index(inplace=True)
    #print(len(df_tech))

    #print(df_tech)
    df_tech["var"] = df_tech[["High","Low","Close"]].std(axis = 1)
    df_tech["mean"] = df_tech[["High","Low","Close"]].mean(axis = 1)


    return df_tech.to_json(date_format='iso', orient='split')

@app.callback(Output('bollinger-graph', 'figure'),
[Input('tech-df', 'children')
, Input('bollinger-days', 'value')
])
def create_bollinger_graph(df_bollinger, bollinger_days):
        print("create_bollinger_graph")
        df_bollinger = pd.read_json(df_bollinger, orient='split')
        fig_bollinger = graph_Bollinger(df_bollinger, bollinger_days)

        return fig_bollinger

@app.callback(Output('CCI-graph', 'figure'),
[Input('tech-df', 'children')
, Input('CCI-days', 'value')
])
def create_CCI_graph(df_CCI, CCI_days):
        print("create_CCI_graph")
        df_CCI = pd.read_json(df_CCI, orient='split')
        fig_CCI = graph_CCI(df_CCI, CCI_days)

        return fig_CCI

@app.callback(Output('ADX-graph', 'figure'),
[Input('tech-df', 'children')
])
def create_ADX_graph(df_ADX):
        print("create_ADX_graph")
        df_ADX = pd.read_json(df_ADX, orient='split')
        fig_ADX = graph_ADX(df_ADX)

        return fig_ADX


@app.callback(
Output('boxes-graph', 'figure'),
[Input('boxes-button', 'n_clicks')],
state = [State('ticker-input', 'value')
, State('date-picker', 'start_date')
, State('date-picker', 'end_date')
, State('boxes-dropdown', 'value')
, State('boxes-period', 'value')
, State('boxes-comparison', 'value')
, State('boxes-variation', 'value')
])
def update_boxes_graph(n_clicks, ticker, startdate, enddate, interval, periods, comparison, variation):
        print("update_boxes_graph")
        #print(n_clicks)
        if n_clicks is None:
            raise PreventUpdate
        ticker = ticker.upper()
        df_boxes = yf.download(ticker, startdate, enddate, interval = interval)
        df_boxes.reset_index(drop=False, inplace=True)
        df_boxes = df_boxes.dropna(axis=0, how='any')
        #print(df_boxes.head(), df_boxes.columns, df_boxes.shape)
        try:
            df_boxes["mean"] = df_boxes[["High","Low","Close"]].mean(axis = 1)
            #print(df_boxes["mean"])
            df_boxes["mean_rolling"] = df_boxes["mean"].rolling(periods).mean()
            #print(df_boxes["mean_rolling"])
            df_boxes["mean_rolling"] = df_boxes["mean_rolling"].round(3)
        except: pass

        try:
            list_open_var = [np.nan] * variation
            list_open_var += list(df_boxes["Open"].values)[:-variation]

            df_boxes["open_variation"] = list_open_var
            df_boxes["var_open_close"] = df_boxes["Close"] - df_boxes["open_variation"]
            df_boxes["var_open_close"] = df_boxes["var_open_close"] / df_boxes["open_variation"]
            df_boxes["var_open_close"] = df_boxes["var_open_close"].round(4)*100
            df_boxes["var_open_close"] = df_boxes["var_open_close"].apply(lambda x: str(x)[:5]) + "%"
        except:
            df_boxes["var_open_close"] = "-"

        try:
            df_boxes["mean"] = df_boxes[["High","Low","Close"]].mean(axis = 1)
            list_mean_var = [np.nan] * variation
            list_mean_var += list(df_boxes["mean"].values)[:-variation]

            df_boxes["mean_variation"] = list_mean_var
            df_boxes["var_mean"] = df_boxes["mean"] - df_boxes["mean_variation"]
            df_boxes["var_mean"] = df_boxes["var_mean"] / df_boxes["mean_variation"]
            df_boxes["var_mean"] = df_boxes["var_mean"].round(4)*100
            df_boxes["var_mean"] = df_boxes["var_mean"].apply(lambda x: str(x)[:5]) + "%"
        except:
            df_boxes["var_mean"] = "-"

        fig_boxes = boxes_graph(df_boxes, comparison)
        return fig_boxes


@app.callback(
    Output('table-sorting-filtering2', 'data'),
    [Input('google-button', 'n_clicks')],
    state = [State('ticker-input', 'value')]
    )
def update_table2(n_clicks, ticker):
    print("update_table2")
    #print(n_clicks)
    if n_clicks is None:
        raise PreventUpdate

    name = yf.Ticker(ticker)
    name = name.info['longName']
    df_google = news_dataframe(name)
    df_google = df_google.to_dict('records')
    return df_google


if __name__ == '__main__':
    app.run_server(debug = True)
