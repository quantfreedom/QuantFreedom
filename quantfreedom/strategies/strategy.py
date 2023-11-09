from datetime import datetime
from logging import getLogger
import os
import numpy as np
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from dash import Dash
from IPython import get_ipython
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

logger = getLogger("info")

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
from quantfreedom.indicators.tv_indicators import rsi_rma_tv_calc

from typing import NamedTuple

from quantfreedom.enums import CandleBodyType, CandleProcessingType, LoggerFuncType, StringerFuncType


class IndicatorSettingsArrays(NamedTuple):
    rsi_is_below: np.array
    rsi_period: np.array


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


class Strategy:
    starting_bar: int

    def __init__(
        self,
        candle_processing_type: CandleProcessingType,
        rsi_is_below: np.array,
        rsi_period: np.array,
    ) -> None:
        logger.debug("Creating Strategy class init")

        ind_set_arrays = IndicatorSettingsArrays(
            rsi_is_below=rsi_is_below,
            rsi_period=rsi_period,
        )
        self.indicator_settings_arrays = create_ind_cart_product(ind_set_arrays=ind_set_arrays)

        if candle_processing_type == CandleProcessingType.Backtest:
            self.set_indicator = self.set_backtesting_indicator
        elif candle_processing_type == CandleProcessingType.LiveTrading:
            self.set_indicator = self.set_live_trading_indicator

    def set_ind_settings(self, ind_set_index: int):
        self.rsi_is_below = self.indicator_settings_arrays.rsi_is_below[ind_set_index]
        self.rsi_period = self.indicator_settings_arrays.rsi_period[ind_set_index]
        logger.debug("Set Indicator Settings")

    def log_indicator_settings(self):
        logger.info(
            f"Indicator Settings\n\
rsi_is_below={self.rsi_is_below}\n\
rsi_period={self.rsi_period}".strip()
        )

    def set_backtesting_indicator(
        self,
        bar_index: int,
        candles: np.array,
    ):
        start = max(bar_index - self.starting_bar, 0)
        try:
            self.rsi = rsi_rma_tv_calc(
                source=candles[start : bar_index + 1, CandleBodyType.Close],
                length=self.rsi_period,
            )
            self.rsi = np.around(self.rsi, 3)
            logger.info(f"Created RSI rsi_is_below= {self.rsi_is_below} rsi_period= {self.rsi_period}")
        except Exception as e:
            logger.info(f"Exception creating RSI -> {e}")
            raise Exception(f"Exception creating RSI -> {e}")

    def set_live_trading_indicator(self, bar_index: int, candles: np.array):
        try:
            self.rsi = rsi_rma_tv_calc(
                source=candles[:, CandleBodyType.Close],
                length=self.rsi_period,
            )
            self.rsi = np.around(self.rsi, 3)
            logger.info(f"Created RSI rsi_is_below= {self.rsi_is_below} rsi_period= {self.rsi_period}")
        except Exception as e:
            logger.info(f"Exception creating rsi -> {e}")
            raise Exception(f"Exception creating rsi -> {e}")

    def evaluate(self, bar_index: int, candles: np.array):
        try:
            self.set_indicator(bar_index=bar_index, candles=candles)
            if self.rsi[-1] < self.rsi_is_below:
                logger.info("\n\n")
                logger.info(f"Entry time!!! rsi= {self.rsi[-1]} < rsi_is_below= {self.rsi_is_below}")
                return True
            else:
                logger.info("No entry")
                return False
        except Exception as e:
            raise Exception(f"Exception evalutating strat -> {e}")

    def get_strategy_plot_filename(self, candles):
        logger.debug("Getting entry plot file")
        last_20 = self.rsi[-20:]
        last_20_datetimes = pd.to_datetime(candles[-20:, CandleBodyType.Timestamp], unit="ms")

        fig = go.Figure()
        fig.add_scatter(
            x=last_20_datetimes,
            y=last_20,
            name=f"Liq Price",
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
        entry_filename = os.path.join(
            ".",
            "logs",
            "images",
            f'indicator_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.png',
        )
        fig.write_image(entry_filename)
        return entry_filename