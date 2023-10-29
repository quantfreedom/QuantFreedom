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


def plot_candles_1_ind_same_pane(candles: np.array, indicator: np.array, ind_name: str, ind_hex_color: str = "#2E91E5"):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=pd.to_datetime(candles[:, 0], unit="ms"),
                open=candles[:, 1],
                high=candles[:, 2],
                low=candles[:, 3],
                close=candles[:, 4],
                name="Candles",
            ),
            go.Scatter(
                x=pd.to_datetime(candles[:, 0], unit="ms"),
                y=indicator,
                marker=dict(color=ind_hex_color),
                name=ind_name,
            ),
        ]
    )
    fig.update_layout(height=600, xaxis_rangeslider_visible=False)
    fig.show()


def plot_candles_1_ind_dif_pane(candles: np.array, indicator: np.array, ind_name: str, ind_hex_color: str = "#2E91E5"):
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
            x=pd.to_datetime(candles[:, 0], unit="ms"),
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
            x=pd.to_datetime(candles[:, 0], unit="ms"),
            y=indicator,
            marker=dict(color=ind_hex_color),
            name=ind_name,
        ),
        row=2,
        col=1,
    )
    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    fig.show()
