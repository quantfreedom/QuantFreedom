import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from logging import getLogger
from quantfreedom.helper_funcs import cart_product
from typing import NamedTuple
from quantfreedom.enums import CandleBodyType
from quantfreedom.strategies.strategy import Strategy

logger = getLogger("info")

from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from dash import Dash
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


class IndicatorSettingsArrays(NamedTuple):
    max_high_lb: np.array
    volatility_lb: np.array


class SimpleBreakoutDynmaicLookback(Strategy):
    starting_bar: int

    def __init__(
        self,
        long_short: str,
        max_high_lb: np.array,
        volatility_lb: np.array,
    ) -> None:
        logger.debug("Created strategy class init")
        self.long_short = long_short

        cart_arrays = cart_product(
            named_tuple=IndicatorSettingsArrays(
                max_high_lb=max_high_lb,
                volatility_lb=volatility_lb,
            )
        )
        self.indicator_settings_arrays: IndicatorSettingsArrays = IndicatorSettingsArrays(
            max_high_lb=cart_arrays[0].astype(np.int_),
            volatility_lb=cart_arrays[1].astype(np.int_),
        )

        if long_short == "long":
            self.set_entries_exits_array = self.long_set_entries_exits_array
            self.log_indicator_settings = self.long_log_indicator_settings
            self.entry_message = self.long_entry_message
        elif long_short == "short":
            pass
        else:
            raise Exception("You need to put either long or short in lowercase")

    def long_set_entries_exits_array(
        self,
        candles: np.array,
        ind_set_index: int,
    ):
        try:
            high = candles[:, CandleBodyType.High]
            close = candles[:, CandleBodyType.Close]

            self.volatility_lb = self.indicator_settings_arrays.volatility_lb[ind_set_index]
            self.max_high_lb = self.indicator_settings_arrays.max_high_lb[ind_set_index]

            self.max_high = np.full_like(close, np.nan)
            current_volatility = np.std(close[0 : self.volatility_lb])

            vol_lb_m_1 = self.volatility_lb - 1

            for i in range(max(self.volatility_lb, self.max_high_lb), close.size):
                prev_vol = current_volatility
                current_volatility = np.std(close[i - vol_lb_m_1 : i + 1])

                delta_vol = (current_volatility - prev_vol) / current_volatility

                real_max_high_lb = self.max_high_lb * (1 + delta_vol)
                try:
                    self.max_high[i] = high[max(i - int(real_max_high_lb), 0) : i].max()
                except:
                    self.max_high[i] = high[i]
            self.entry_prices = np.where(close >= self.max_high, close, np.nan)

            self.entries_strat = ~np.isnan(self.entry_prices)
            self.exits_strat = np.full_like(self.entries_strat, np.nan)
        except Exception as e:
            logger.info(f"Exception long_set_entries_exits_array -> {e}")
            raise Exception(f"Exception long_set_entries_exits_array -> {e}")

    def long_log_indicator_settings(
        self,
        ind_set_index: int,
    ):
        logger.info(
            f"Indicator Settings Index= {ind_set_index}\
            \nmax_high_lb= {self.max_high_lb}\
            \nvolitility_lb= {self.volatility_lb}"
        )

    def long_entry_message(
        self,
        bar_index: int,
    ):
        logger.info("\n\n")
        logger.info(
            f"Entry time!!! Close is higher than the High {self.entry_prices[bar_index]} > {self.max_high[bar_index]}"
        )
