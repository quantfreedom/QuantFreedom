import datetime
import os
import numpy as np
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from dash import Dash
from IPython import get_ipython
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

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
from quantfreedom.indicators.indicators import rsi_calc

from typing import NamedTuple

from quantfreedom.enums import CandleBodyType, LoggerFuncType, StringerFuncType


class IndicatorSettingsArrays(NamedTuple):
    rsi_is_below: np.array
    rsi_period: np.array


class IndicatorSettings(NamedTuple):
    rsi_is_below: float
    rsi_period: int


ind_set_arrays = IndicatorSettingsArrays(
    rsi_is_below=np.array([70, 50, 30]),
    rsi_period=np.array([14, 20]),
)


def create_ind_cart_product(ind_set_arrays: IndicatorSettingsArrays):
    n = 1
    for x in ind_set_arrays:
        n *= x.size
    out = np.empty((n, len(ind_set_arrays)))

    for i in range(len(ind_set_arrays)):
        m = int(n / ind_set_arrays[i].size)
        out[:n, i] = np.repeat(ind_set_arrays[i], m)
        n //= ind_set_arrays[i].size

    n = ind_set_arrays[-1].size
    for k in range(len(ind_set_arrays) - 2, -1, -1):
        n *= ind_set_arrays[k].size
        m = int(n / ind_set_arrays[k].size)
        for j in range(1, ind_set_arrays[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    return IndicatorSettingsArrays(
        rsi_is_below=out.T[0],
        rsi_period=out.T[1].astype(np.int_),
    )


ind_set_arrays = create_ind_cart_product(ind_set_arrays=ind_set_arrays)


def strat_bt_create_ind(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    logger,
):
    start = max(bar_index - starting_bar, 0)
    try:
        rsi = rsi_calc(
            source=candles[start : bar_index + 1, CandleBodyType.Close],
            length=indicator_settings.rsi_period,
        )
        rsi = np.around(rsi, 2)
        logger[LoggerFuncType.Info]("strategy.py - strat_bt_create_ind() - Created RSI")
        return rsi
    except Exception:
        logger[LoggerFuncType.Info]("strategy.py - strat_bt_create_ind() - Exception creating RSI")
        raise Exception


def strat_live_create_ind(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    logger,
):
    try:
        rsi = rsi_calc(
            source=candles[:, CandleBodyType.Close],
            length=indicator_settings.rsi_period,
        )
        rsi = np.around(rsi, 2)
        logger[LoggerFuncType.Info]("strategy.py - strat_liv_create_ind() - Created RSI")
        return rsi
    except Exception:
        logger[LoggerFuncType.Info]("strategy.py - strat_liv_create_ind() - Exception creating rsi")
        raise Exception


def strat_get_total_ind_settings():
    return ind_set_arrays[0].size


def strat_get_current_ind_settings(
    ind_set_index: int,
    logger,
):
    indicator_settings = IndicatorSettings(
        rsi_is_below=ind_set_arrays.rsi_is_below[ind_set_index],
        rsi_period=ind_set_arrays.rsi_period[ind_set_index],
    )
    logger[LoggerFuncType.Info]("strategy.py - get_current_ind_settings() - Created indicator settings")
    return indicator_settings


def strat_get_ind_set_str(
    indicator_settings: IndicatorSettings,
    stringer,
):
    msg = (
        "strategy.py - strat_get_ind_set_str() - "
        + "RSI Period= "
        + str(indicator_settings.rsi_period)
        + " RSI is below= "
        + stringer[StringerFuncType.float_to_str](indicator_settings.rsi_is_below)
    )
    return msg


def strat_evaluate(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    ind_creator,
    logger,
    stringer,
):
    rsi = ind_creator(
        bar_index=bar_index,
        starting_bar=starting_bar,
        candles=candles,
        indicator_settings=indicator_settings,
        logger=logger,
    )
    try:
        current_rsi = rsi[-1]
        rsi_is_below = indicator_settings.rsi_is_below

        if current_rsi < rsi_is_below:
            logger[LoggerFuncType.Info]("\n\n")
            logger[LoggerFuncType.Info](
                "strategy.py - evaluate() - Entry time!!! "
                + "current rsi= "
                + stringer[StringerFuncType.float_to_str](current_rsi)
                + " < rsi_is_below= "
                + stringer[StringerFuncType.float_to_str](rsi_is_below)
            )

            return True
        else:
            logger[LoggerFuncType.Info](
                "strategy.py - evaluate() - No entry "
                + "current rsi= "
                + stringer[StringerFuncType.float_to_str](current_rsi)
            )
            return False
    except Exception:
        raise Exception("strategy.py - evaluate() - Exception evalutating strat")


def get_strategy_plot_filename(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    ind_creator,
    logger,
):
    rsi = ind_creator(
        bar_index=bar_index,
        starting_bar=starting_bar,
        candles=candles,
        indicator_settings=indicator_settings,
        logger=logger,
    )
    logger[LoggerFuncType.Debug]("Getting entry plot file")
    last_20 = rsi[-20:]
    last_20_datetimes = pd.to_datetime(candles[-20:, 0], unit="ms")
    fig = go.Figure()
    fig.add_scatter(
        x=last_20_datetimes,
        y=last_20,
        mode="markers",
        marker=dict(size=10, symbol="hexagram", color="red"),
        name=f"Liq Price",
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()
    entry_filename = os.path.join(
        ".",
        "logs",
        "images",
        f'entry_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.png',
    )
    fig.write_image(entry_filename)
    return entry_filename
