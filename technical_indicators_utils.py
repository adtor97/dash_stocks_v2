import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
import numpy as np

def df_indicators_columns(df):
    df["var"] = df[["High","Low","Close"]].std(axis = 1)
    df["mean"] = df[["High","Low","Close"]].mean(axis = 1)

    df["mean_rolling_15"] = df["mean"].rolling(15).mean()
    df["std_rolling_15"] = df["mean"].rolling(15).std()
    df["mean_std_rolling_plus_15"] = df["mean_rolling_15"] + df["std_rolling_15"]
    df["mean_std_rolling_less_15"] = df["mean_rolling_15"] - df["std_rolling_15"]

    df["mean_rolling_45"] = df["mean"].rolling(45).mean()
    df["std_rolling_45"] = df["mean"].rolling(45).std()
    df["mean_std_rolling_plus_45"] = df["mean_rolling_45"] + df["std_rolling_45"]
    df["mean_std_rolling_less_45"] = df["mean_rolling_45"] - df["std_rolling_45"]

    df["mean_rolling_100"] = df["mean"].rolling(100).mean()
    df["std_rolling_100"] = df["mean"].rolling(100).std()
    df["mean_std_rolling_plus_100"] = df["mean_rolling_100"] + df["std_rolling_100"]
    df["mean_std_rolling_less_100"] = df["mean_rolling_100"] - df["std_rolling_100"]

    return df

def graph_mean(df):
    if "Date" in list(df.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"
    fig = go.Figure()
    fig.update_layout(title="Typical daily price", width=600, hovermode='x unified')

    fig.add_trace(go.Scatter(x=df[date_column], y=df["mean"], mode='lines', name="price"))
    return fig

def graph_Bollinger(df_bollinger, bollinger_days):
    df_bollinger["mean_rolling"] = df_bollinger["mean"].rolling(bollinger_days).mean()
    df_bollinger["std_rolling"] = df_bollinger["mean"].rolling(bollinger_days).std()
    df_bollinger["mean_std_rolling_plus"] = df_bollinger["mean_rolling"] + df_bollinger["std_rolling"]
    df_bollinger["mean_std_rolling_less"] = df_bollinger["mean_rolling"] - df_bollinger["std_rolling"]

    if "Date" in list(df_bollinger.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"

    fig_boll = go.Figure()
    fig_boll.update_layout(title="Bollinger bands", width=600, hovermode='x unified')

    fig_boll.add_trace(go.Scatter(x=df_bollinger[date_column], y=df_bollinger["mean_rolling"], mode='lines', name=str(bollinger_days) + " rolling avg"))
    fig_boll.add_trace(go.Scatter(x=df_bollinger[date_column], y=df_bollinger["mean_std_rolling_plus"], mode='lines', name=str(bollinger_days) + " upper band"))
    fig_boll.add_trace(go.Scatter(x=df_bollinger[date_column], y=df_bollinger["mean_std_rolling_less"], mode='lines', name=str(bollinger_days) + " lower band"))

    fig_boll.add_trace(go.Scatter(x=df_bollinger[date_column], y=df_bollinger["mean"], mode='lines', name=str(bollinger_days) + " Typical Price"))

    return fig_boll

def mean_deviation_calculation(df_CCI, CCI_days):
    df_CCI["mean_rolling"] = df_CCI["mean"].rolling(CCI_days).mean()
    mean_deviations = []

    for index, row in df_CCI.iterrows():
        #print(row["mean_rolling" + days])
        if str(row["mean_rolling"]) == "nan":
            mean_deviations.append(np.nan)
        else:
            mean_rolling = row["mean_rolling"]
            df_temp = df_CCI.iloc[:index+1]
            df_temp = df_temp.iloc[-20:]
            #print(len(df_temp))

            df_temp["diff"] = df_temp["mean"] - mean_rolling
            df_temp["diff"] = df_temp["diff"].abs()

            mean_deviation = df_temp["diff"].sum() / 20
            #print(mean_deviation)
            mean_deviations.append(mean_deviation)
        #print(mean_deviations)
    df_CCI["mean_deviation"] = mean_deviations
    return df_CCI

def graph_CCI(df_CCI, CCI_days):
    if "Date" in list(df_CCI.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"
    df_CCI = mean_deviation_calculation(df_CCI, CCI_days)
    fig_CCI = go.Figure()
    fig_CCI.update_layout(title="CCI", width=600, hovermode='x unified')

    #for days in ["_15", "_45", "_100"]:
    df_CCI["CCI"] = (df_CCI["mean"] - df_CCI["mean_rolling"]) / (0.15 * df_CCI["mean_deviation"]) * 10
    fig_CCI.add_trace(go.Scatter(x=df_CCI[date_column], y=df_CCI["CCI"], mode='lines', name="CCI " + str(CCI_days)))
    return fig_CCI

def pos_DM_calculation(df):
    pos_DMs = [np.nan]
    for index, row in df.iloc[1:].iterrows():
        current_high = row["High"]
        previous_high = df.iloc[index-1:index]["High"].values[0]

        pos_DM = current_high - previous_high
        pos_DMs.append(pos_DM)
    df["pos_DM"] = pos_DMs

    return df

def TR_calculation(df):
    TRs = [np.nan]
    for index, row in df.iloc[1:].iterrows():
        current_high = row["High"]
        current_low = row["Low"]
        current_high_current_low = current_high-current_low

        previous_close = df.iloc[index-1:index]["Close"].values[0]
        current_high_previous_close = abs(current_high-previous_close)

        current_low_previous_close = abs(current_low-previous_close)

        TR = max([current_high_current_low, current_high_previous_close, current_low_previous_close])
        TRs.append(TR)
    df["TR"] = TRs

    return df

def neg_DM_calculation(df):
    neg_DMs = [np.nan]
    for index, row in df.iloc[1:].iterrows():
        current_low = row["Low"]
        previous_low = df.iloc[index-1:index]["Low"].values[0]

        neg_DM = previous_low - current_low
        neg_DMs.append(neg_DM)
    df["neg_DM"] = neg_DMs

    return df

def graph_ADX(df_ADX):
    if "Date" in list(df_ADX.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"

    df_ADX = pos_DM_calculation(df_ADX)
    df_ADX = TR_calculation(df_ADX)
    df_ADX = neg_DM_calculation(df_ADX)
    df_ADX["pos_DM_rolling"] = df_ADX["pos_DM"].rolling(15).sum()
    df_ADX["neg_DM_rolling"] = df_ADX["neg_DM"].rolling(15).sum()
    df_ADX["TR_rolling"] = df_ADX["TR"].rolling(15).sum()

    df_ADX["pos_DI"] = ((df_ADX["pos_DM_rolling"]) - ((df_ADX["pos_DM_rolling"]) / 14) + (df_ADX["pos_DM"])) / ((df_ADX["TR_rolling"]) - ((df_ADX["TR_rolling"]) / 14) + (df_ADX["TR_rolling"]))
    df_ADX["pos_DI"] = df_ADX["pos_DI"]*100
    df_ADX["neg_DI"] = ((df_ADX["neg_DM_rolling"]) - ((df_ADX["neg_DM_rolling"]) / 14) + (df_ADX["neg_DM"])) / ((df_ADX["TR_rolling"]) - ((df_ADX["TR_rolling"]) / 14) + (df_ADX["TR_rolling"]))
    df_ADX["neg_DI"] = df_ADX["neg_DI"]*100
    df_ADX["ADX"] = df_ADX["pos_DI"] - df_ADX["neg_DI"]
    df_ADX["ADX"] = df_ADX["ADX"].abs()

    fig_ADX = go.Figure()
    fig_ADX.update_layout(title="ADX", width=600, hovermode='x unified')

    fig_ADX.add_trace(go.Scatter(x=df_ADX[date_column], y=df_ADX["pos_DI"], mode='lines', name="+ DI"))
    fig_ADX.add_trace(go.Scatter(x=df_ADX[date_column], y=df_ADX["neg_DI"], mode='lines', name="- DI"))
    fig_ADX.add_trace(go.Scatter(x=df_ADX[date_column], y=df_ADX["ADX"], mode='lines', name="ADX"))

    return fig_ADX
