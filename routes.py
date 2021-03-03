from flask import Flask, render_template, request, redirect, url_for, session, Markup, flash, send_file, make_response
import pandas as pd
from datetime import date
import plotly
import os, io, time
import numpy as np
import warnings
from pandas.core.common import SettingWithCopyWarning
from flask import current_app as app

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
pd.options.display.float_format = "{:,.2f}".format

today = str(date.today())
app.secret_key = today

static_folder = os.path.join('static')

@app.route("/")
def home():
    return render_template("home.html")
