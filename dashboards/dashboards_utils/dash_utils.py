import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

import flask
from flask import Flask
import pandas as pd
import dateutil.relativedelta
from datetime import date
from datetime import datetime as dt
import datetime
import yfinance as yf
import numpy as np
import praw
import sqlite3

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def make_table(id, dataframe, lineHeight = '17px', page_size = 5):
    return   dash_table.DataTable(
                    id=id,
                    css=[{'selector': '.row', 'rule': 'margin: 0'}],
                    columns=[
                        {"name": i, "id": i} for i in dataframe.columns
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'},
                     style_cell={'textAlign': 'left'},
                     style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'lineHeight': lineHeight
                        },
                    # style_table = {'width':300},
                    style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ],
                    style_cell_conditional=[
                        {'if': {'column_id': 'title'},
                        'width': '130px'},
                        {'if': {'column_id': 'google_title'},
                        'width': '200px'},
                        {'if': {'column_id': 'link'},
                        'width': '175px'},
                        {'if': {'column_id': 'post'},
                        'width': '500px'},
                        {'if': {'column_id': 'datetime'},
                        'width': '130px'},
                        {'if': {'column_id': 'text'},
                        'width': '500px'}],
                    page_current=0,
                    page_size=page_size,
                    page_action='custom',

                    filter_action='custom',
                    filter_query='',

                    sort_action='custom',
                    sort_mode='multi',
                    sort_by=[],
                    #dataframe.to_dict('records')
                    )

def make_card(alert_message, color, cardbody, style_dict = None):
    return  dbc.Card([  dbc.Alert(alert_message, color=color)
                        ,dbc.CardBody(cardbody)
                    ], style = style_dict)#end card

def ticker_inputs(inputID, pickerID, MONTH_CUTTOFF):

        currentDate = date.today()
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=6)

        return html.Div([
                dcc.Input(id = inputID, type="text", placeholder="Ticker", value="MEL.MC")
             , html.P(" ")
             , dcc.DatePickerRange(
                id = pickerID,
                #min_date_allowed=pastDate,
                max_date_allowed=currentDate + dateutil.relativedelta.relativedelta(days=2),
                initial_visible_month=pastDate,
                start_date = pastDate,
                end_date = currentDate
                )])

def make_item(button, cardbody, i):
    # we use this function to make the example items to avoid code duplication
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        button,
                        color="link",
                        id=f"group-{i}-toggle",
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody(cardbody),
                id=f"collapse-{i}",
            ),
        ]
    )

def boxes_dropdown(id, options, value):
    dropdown = html.Div(
                        dcc.Dropdown(id=id,
                                    options=options,
                                    value=value,
                                    placeholder="Select graph timing"),
                        )
    return dropdown

def boxes_graph(df_boxes, comparison):
    fig = go.Figure(data=[go.Candlestick(x=df_boxes["Date"],
                                        open=df_boxes['Open'], high=df_boxes['High'],
                                        low=df_boxes['Low'], close=df_boxes['Close'],
                                        hovertext = [f'Var open to close: {x} | Var typical price: {y}' for x,y in list(zip(df_boxes['var_open_close'], df_boxes['var_mean']))],
                                        name="Period boxes")
                        ]
                )
    try:
        fig.add_trace(
                    go.Scatter(x=df_boxes["Date"], y=df_boxes["mean_rolling"], mode='lines', name="Period rolling avg", line=dict(color='green'))
                    )
    except: pass

    try:
        mean_rolling_comparison = list([np.nan]*comparison)
        #print(mean_rolling_comparison)
        #print(df_boxes["mean_rolling"])
        mean_rolling_comparison+=list(df_boxes["mean_rolling"].values)[:-comparison]
        #print(mean_rolling_comparison)

        fig.add_trace(
                    go.Scatter(x=df_boxes["Date"], y=mean_rolling_comparison, mode='lines', name="Comparison period rolling avg", line=dict(color='red'))
                    )
    except: pass

    fig.update_layout(title="Volatility analysis", height=600, hovermode='x unified')

    return fig
