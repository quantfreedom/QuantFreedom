import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from IPython import get_ipython
from dash import Dash, dcc, html, dash_table
from jupyter_dash import JupyterDash
from plotly.subplots import make_subplots
from dash_bootstrap_templates import load_figure_template

from quantfreedom.enums.enums import OrderType
from quantfreedom._typing import pdFrame, RecordArray, pdIndex, Array1d

np.set_printoptions(formatter={"float_kind": "{:.2f}".format})

pd.options.display.float_format = "{:,.2f}".format

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


def get_candle_trace_data():
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.6, 0.2, 0.2],
    )
    fig.add_traces(
        data=get_candle_trace_data(
            index_prices=index_prices,
            prices=prices,
            order_records=order_records,
            indicator_dict=indicator_dict,
        ),
        rows=1,
        cols=1,
    )
    return fig.show()


get_candle_trace_data()
