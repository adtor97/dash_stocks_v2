import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
import numpy as np

def df_indicators_columns(df):
    df["var"] = df[["High","Low","Close"]].std(axis = 1)
    df["mean"] = df[["High","Low","Close"]].mean(axis = 1)
    df["mean_rolling"] = df["mean"].rolling(15).mean()
    df["std_rolling"] = df["mean"].rolling(15).std()
    df["mean_std_rolling_plus"] = df["mean_rolling"] + df["std_rolling"]
    df["mean_std_rolling_less"] = df["mean_rolling"] - df["std_rolling"]

    return df

def graph_mean(df):
    if "Date" in list(df.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"
    fig = go.Figure()
    fig.update_layout(title="Typical daily price", width=600)

    fig.add_trace(go.Scatter(x=df[date_column], y=df["mean"], mode='lines', name="price"))
    return fig

def graph_Bollinger(df):
    if "Date" in list(df.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"

    fig = go.Figure()
    fig.update_layout(title="Bandas de Bollinger", width=600)

    fig.add_trace(go.Scatter(x=df[date_column], y=df["mean_rolling"], mode='lines', name="mean_rolling"))
    fig.add_trace(go.Scatter(x=df[date_column], y=df["mean_std_rolling_plus"], mode='lines', name="mean_std_rolling_plus"))
    fig.add_trace(go.Scatter(x=df[date_column], y=df["mean_std_rolling_less"], mode='lines', name="mean_std_rolling_less"))
    fig.add_trace(go.Scatter(x=df[date_column], y=df["mean"], mode='lines', name="Typical Price"))

    return fig

def mean_deviation_calculation(df):
    mean_deviations = []
    for index, row in df.iterrows():
        if str(row["mean_rolling"]) == "nan":
            mean_deviations.append(np.nan)
        else:
            mean_rolling = row["mean_rolling"]

            df_temp = df.iloc[:index+1]
            df_temp = df_temp.iloc[-20:]
            #print(len(df_temp))

            df_temp["diff"] = df_temp["mean"] - mean_rolling
            df_temp["diff"] = df_temp["diff"].abs()

            mean_deviation = df_temp["diff"].sum() / 20
            mean_deviations.append(mean_deviation)

    df["mean_deviation"] = mean_deviations
    return df

def graph_CCI(df):
    if "Date" in list(df.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"
    df = mean_deviation_calculation(df)
    df["CCI"] = (df["mean"] - df["mean_rolling"]) / (0.15 * df["mean_deviation"]) * 10
    fig = go.Figure()
    fig.update_layout(title="CCI", width=600)

    fig.add_trace(go.Scatter(x=df[date_column], y=df["CCI"], mode='lines', name="CCI"))
    return fig

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

def graph_ADX(df):
    if "Date" in list(df.columns):
        date_column = "Date"
    else:
        date_column = "Datetime"

    df = pos_DM_calculation(df)
    df = TR_calculation(df)
    df = neg_DM_calculation(df)
    df["pos_DM_rolling"] = df["pos_DM"].rolling(15).sum()
    df["neg_DM_rolling"] = df["neg_DM"].rolling(15).sum()
    df["TR_rolling"] = df["TR"].rolling(15).sum()

    df["pos_DI"] = ((df["pos_DM_rolling"]) - ((df["pos_DM_rolling"]) / 14) + (df["pos_DM"])) / ((df["TR_rolling"]) - ((df["TR_rolling"]) / 14) + (df["TR_rolling"]))
    df["pos_DI"] = df["pos_DI"]*100
    df["neg_DI"] = ((df["neg_DM_rolling"]) - ((df["neg_DM_rolling"]) / 14) + (df["neg_DM"])) / ((df["TR_rolling"]) - ((df["TR_rolling"]) / 14) + (df["TR_rolling"]))
    df["neg_DI"] = df["neg_DI"]*100
    df["ADX"] = df["pos_DI"] - df["neg_DI"]
    df["ADX"] = df["ADX"].abs()

    fig = go.Figure()
    fig.update_layout(title="ADX", width=600)

    fig.add_trace(go.Scatter(x=df[date_column], y=df["pos_DI"], mode='lines', name="pos_DI"))
    fig.add_trace(go.Scatter(x=df[date_column], y=df["neg_DI"], mode='lines', name="neg_DI"))
    fig.add_trace(go.Scatter(x=df[date_column], y=df["ADX"], mode='lines', name="ADX"))

    return fig
