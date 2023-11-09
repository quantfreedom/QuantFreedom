import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from IPython import get_ipython
import dash_bootstrap_components as dbc

load_figure_template("darkly")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
try:
    shell = str(get_ipython())
    if "ZMQInteractiveShell" in shell:
        app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
    elif shell == "TerminalInteractiveShell":
        app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
    else:
        app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
except NameError:
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

bg_color = "#0b0b18"


def plot_candles_1_ind_same_pane(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    datetimes = pd.to_datetime(candles[:, 0], unit="ms")
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=datetimes,
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
            go.Scatter(
                x=datetimes,
                y=indicator,
                name=ind_name,
                line_color=f"rgb({ind_color})",
            ),
        ]
    )
    fig.update_layout(height=600, xaxis_rangeslider_visible=False)
    fig.show()


def plot_candles_1_ind_dif_pane(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    datetimes = pd.to_datetime(candles[:, 0], unit="ms")
    fig = make_subplots(
        cols=1,
        rows=2,
        shared_xaxes=True,
        subplot_titles=["Candles", ind_name],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1,
    )
    fig.add_trace(
        go.Candlestick(
            x=datetimes,
            open=candles[:, 1],
            high=candles[:, 2],
            low=candles[:, 3],
            close=candles[:, 4],
            name="Candles",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=datetimes,
            y=indicator,
            name=ind_name,
            line_color=f"rgb({ind_color})",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()


def plot_rma(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    return plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name=ind_name,
        ind_color=ind_color,
    )


def plot_sma(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    return plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name=ind_name,
        ind_color=ind_color,
    )


def plot_ema(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    return plot_candles_1_ind_same_pane(
        candles=candles,
        indicator=indicator,
        ind_name=ind_name,
        ind_color=ind_color,
    )


def plot_rsi(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    return plot_candles_1_ind_dif_pane(
        candles=candles,
        indicator=indicator,
        ind_name=ind_name,
        ind_color=ind_color,
    )


def plot_stdev(
    candles: np.array,
    indicator: np.array,
    ind_name: str,
    ind_color: str = "46, 145, 229",
):
    return plot_candles_1_ind_dif_pane(
        candles=candles,
        indicator=indicator,
        ind_name=ind_name,
        ind_color=ind_color,
    )


def plot_bollinger_bands(
    candles: np.array,
    indicator: np.array,
    ul_rgb: str = "48, 123, 255",
    basis_color: str = "255, 176, 0",
):
    datetimes = pd.to_datetime(candles[:, 0], unit="ms")
    fig = go.Figure(
        data=[
            go.Scatter(
                x=datetimes,
                y=indicator[:, 2],
                name="lower",
                line_color=f"rgb({ul_rgb})",
            ),
            go.Scatter(
                x=datetimes,
                y=indicator[:, 0],
                name="upper",
                line_color=f"rgb({ul_rgb})",
                fillcolor=f"rgba({ul_rgb}, 0.07)",
                fill="tonexty",
            ),
            go.Scatter(
                x=datetimes,
                y=indicator[:, 1],
                name="bb_sma",
                line_color=f"rgb({basis_color})",
            ),
            go.Candlestick(
                x=datetimes,
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
        ]
    )
    fig.update_layout(height=600, xaxis_rangeslider_visible=False)
    fig.show()


def plot_or_results(candles: np.array, order_records_df: pd.DataFrame):
    fig = make_subplots(
        cols=1,
        rows=2,
        shared_xaxes=True,
        subplot_titles=["Candles", "Cumulative Realized PnL"],
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1,
    )

    try:
        # Candles
        fig.add_trace(
            go.Candlestick(
                x=pd.to_datetime(candles[:, 0], unit="ms"),
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
            col=1,
            row=1,
        )
    except:
        pass

    try:
        entries_df = order_records_df[order_records_df["order_status"] == "EntryFilled"]
        entries_dt = entries_df["datetime"]
        # Entries
        fig.add_trace(
            go.Scatter(
                x=entries_dt,
                y=entries_df["entry_price"],
                mode="markers",
                name="Entries",
                marker=dict(size=10, symbol="circle", color="#00F6FF", line=dict(width=1, color="DarkSlateGrey")),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        fig.add_trace(
            # Stop Losses
            go.Scatter(
                x=entries_dt,
                y=entries_df["sl_price"],
                mode="markers",
                name="Stop Losses",
                marker=dict(size=10, symbol="square", color="#FFCA00", line=dict(width=1, color="DarkSlateGrey")),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Take Profits
        fig.add_trace(
            go.Scatter(
                x=entries_dt,
                y=entries_df["tp_price"],
                mode="markers",
                name="Take Profits",
                marker=dict(size=10, symbol="triangle-up", color="#FF7B00", line=dict(width=1, color="DarkSlateGrey")),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Stop Loss Filled
        fig.add_trace(
            go.Scatter(
                x=order_records_df[order_records_df["order_status"] == "StopLossFilled"]["datetime"],
                y=order_records_df[order_records_df["order_status"] == "StopLossFilled"]["exit_price"],
                mode="markers",
                name="Stop Loss Filled",
                marker=dict(size=10, symbol="x", color="#FF00BB", line=dict(width=1, color="DarkSlateGrey")),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Take Profit Filled
        fig.add_trace(
            go.Scatter(
                x=order_records_df[order_records_df["order_status"] == "TakeProfitFilled"]["datetime"],
                y=order_records_df[order_records_df["order_status"] == "TakeProfitFilled"]["exit_price"],
                mode="markers",
                name="Take Profit Filled",
                marker=dict(size=10, symbol="star", color="#14FF00", line=dict(width=1, color="DarkSlateGrey")),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        # Moved SL
        fig.add_trace(
            go.Scatter(
                x=order_records_df[order_records_df["order_status"].isin(["MovedTSL", "MovedSLToBE"])]["datetime"],
                y=order_records_df[order_records_df["order_status"].isin(["MovedTSL", "MovedSLToBE"])]["sl_price"],
                mode="markers",
                name="Moved SL",
                marker=dict(
                    size=10, symbol="diamond-cross", color="#F1FF00", line=dict(width=1, color="DarkSlateGrey")
                ),
            ),
            col=1,
            row=1,
        )
    except:
        pass
    try:
        pnl_dt_df = order_records_df[~order_records_df["realized_pnl"].isna()]["datetime"]
        dt_list = pnl_dt_df.to_list()
        dt_list.insert(0, pd.to_datetime(candles[0, 0], unit="ms"))

        pnl_df = order_records_df[~order_records_df["realized_pnl"].isna()]["realized_pnl"]
        pnl_list = pnl_df.to_list()
        pnl_list.insert(0, 0)
        cumulative_pnl = np.array(pnl_list).cumsum()
        # Cumulative Realized PnL
        fig.add_trace(
            go.Scatter(
                x=dt_list,
                y=cumulative_pnl,
                name="Cumulative Realized PnL",
                line_color="#3EA3FF",
            ),
            col=1,
            row=2,
        )
    except:
        pass
    fig.update_layout(height=1000, xaxis_rangeslider_visible=False)
    fig.update_yaxes(tickformat="$,")
    fig.show()
