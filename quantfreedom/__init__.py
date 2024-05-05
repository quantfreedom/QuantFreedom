from dash import Dash
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from IPython import get_ipython
import dash_bootstrap_components as dbc
from quantfreedom.helpers.utils import pretty_qf, pretty_qf_string
from quantfreedom.helpers.helper_funcs import dl_ex_candles

__all__ = [
    "pretty_qf",
    "dl_ex_candles",
    "pretty_qf_string",
]

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
