from datetime import datetime
from logging import getLogger
from quantfreedom.helper_funcs import cart_product
from quantfreedom.indicators.tv_indicators import rsi_tv

from typing import NamedTuple

from quantfreedom.enums import CandleBodyType
import os
import numpy as np
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from jupyter_dash import JupyterDash
from dash import Dash
from IPython import get_ipython
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from quantfreedom.strategies.strategy import Strategy

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


class IndicatorSettingsArrays(NamedTuple):
    rsi_is_above: np.array
    rsi_is_below: np.array
    rsi_length: np.array


class RSIBelowAbove(Strategy):
    starting_bar: int

    def __init__(
        self,
        long_short: str,
        rsi_length: np.array,
        rsi_is_above: np.array = np.array([0]),
        rsi_is_below: np.array = np.array([0]),
    ) -> None:
        logger.debug("Creating Strategy class init")
        self.long_short = long_short

        cart_arrays = cart_product(
            named_tuple=IndicatorSettingsArrays(
                rsi_is_above=rsi_is_above,
                rsi_is_below=rsi_is_below,
                rsi_length=rsi_length,
            )
        )
        self.indicator_settings_arrays = IndicatorSettingsArrays(
            rsi_is_above=cart_arrays.T[0],
            rsi_is_below=cart_arrays.T[1],
            rsi_length=cart_arrays.T[2].astype(np.int_),
        )

        if long_short == "long":
            self.set_entries_exits_array = self.long_set_entries_exits_array
            self.log_indicator_settings = self.long_log_indicator_settings
            self.entry_message = self.long_entry_message
        else:
            self.set_entries_exits_array = self.short_set_entries_exits_array
            self.log_indicator_settings = self.short_log_indicator_settings
            self.entry_message = self.short_entry_message

    """
    #######################################################
    #######################################################
    #######################################################
    ##################      short    ######################
    ##################      short    ######################
    ##################      short    ######################
    #######################################################
    #######################################################
    #######################################################
    """

    def short_set_entries_exits_array(
        self,
        candles: np.array,
        ind_set_index: int,
    ):
        try:
            self.rsi_is_above = self.indicator_settings_arrays.rsi_is_above[ind_set_index]
            self.rsi_length = self.indicator_settings_arrays.rsi_length[ind_set_index]
            rsi = rsi_tv(
                source=candles[:, CandleBodyType.Close],
                length=self.rsi_length,
            )
            self.rsi = np.around(rsi, 2)
            logger.info(f"Created RSI rsi_is_above= {self.rsi_is_above} rsi_length= {self.rsi_length}")

            self.entries_strat = np.where(self.rsi > self.rsi_is_above, True, False)
            self.exits_strat = np.full_like(self.rsi, np.nan)

        except Exception as e:
            logger.info(f"Exception short_set_entries_exits_array -> {e}")
            raise Exception(f"Exception short_set_entries_exits_array -> {e}")

    def short_log_indicator_settings(self, ind_set_index: int):
        logger.info(
            f"Indicator Settings Index= {ind_set_index}\
            \nrsi_length= {self.rsi_length}\
            \nrsi_is_above= {self.rsi_is_above}"
        )

    def short_entry_message(self, bar_index: int):
        logger.info("\n\n")
        logger.info(f"Entry time!!! rsi= {self.rsi[bar_index]} < rsi_is_above= {self.rsi_is_above}")

    """
    #######################################################
    #######################################################
    #######################################################
    ##################      Long     ######################
    ##################      Long     ######################
    ##################      Long     ######################
    #######################################################
    #######################################################
    #######################################################
    """

    def long_set_entries_exits_array(
        self,
        candles: np.array,
        ind_set_index: int,
    ):
        try:
            self.rsi_is_below = self.indicator_settings_arrays.rsi_is_below[ind_set_index]
            self.rsi_length = self.indicator_settings_arrays.rsi_length[ind_set_index]
            rsi = rsi_tv(
                source=candles[:, CandleBodyType.Close],
                length=self.rsi_length,
            )
            self.rsi = np.around(rsi, 2)
            logger.info(f"Created RSI rsi_is_below= {self.rsi_is_below} rsi_length= {self.rsi_length}")

            self.entries_strat = np.where(self.rsi < self.rsi_is_below, True, False)
            self.exits_strat = np.full_like(self.rsi, np.nan)

        except Exception as e:
            logger.info(f"Exception long_set_entries_exits_array -> {e}")
            raise Exception(f"Exception long_set_entries_exits_array -> {e}")

    def long_log_indicator_settings(self, ind_set_index: int):
        logger.info(
            f"Indicator Settings Index= {ind_set_index}\
            \nrsi_length= {self.rsi_length}\
            \nrsi_is_below= {self.rsi_is_below}"
        )

    def long_entry_message(self, bar_index: int):
        logger.info("\n\n")
        logger.info(f"Entry time!!! rsi= {self.rsi[bar_index]} < rsi_is_below= {self.rsi_is_below}")

    """
    #######################################################
    #######################################################
    #######################################################
    ##################      Live     ######################
    ##################      Live     ######################
    ##################      Live     ######################
    #######################################################
    #######################################################
    #######################################################
    """

    def live_set_indicator(self, closes: np.array):
        try:
            self.rsi = rsi_tv(
                source=closes,
                length=self.rsi_length,
            )
            self.rsi = np.around(self.rsi, 2)
            logger.info(f"Created RSI rsi_is_below= {self.rsi_is_below} rsi_length= {self.rsi_length}")
        except Exception as e:
            logger.info(f"Exception set_live_trading_indicator -> {e}")
            raise Exception(f"Exception set_live_trading_indicator -> {e}")

    def live_evaluate(self, candles: np.array):
        try:
            self.live_set_indicator(closes=candles[:, CandleBodyType.Close])
            if self.rsi[-1] < self.rsi_is_below:
                logger.info("\n\n")
                logger.info(f"Entry time!!! rsi= {self.rsi[-1]} < rsi_is_below= {self.rsi_is_below}")
                return True
            else:
                logger.info("No entry")
                return False
        except Exception as e:
            raise Exception(f"Exception evalutating strat -> {e}")

    """
    #######################################################
    #######################################################
    #######################################################
    ##################      Plot     ######################
    ##################      Plot     ######################
    ##################      Plot     ######################
    #######################################################
    #######################################################
    #######################################################
    """

    def get_strategy_plot_filename(self, candles: np.array):
        logger.debug("Getting entry plot file")
        last_20 = self.rsi[-20:]
        last_20_datetimes = pd.to_datetime(candles[-20:, CandleBodyType.Timestamp], unit="ms")

        fig = go.Figure()
        fig.add_scatter(
            x=last_20_datetimes,
            y=last_20,
            name="RSI",
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
