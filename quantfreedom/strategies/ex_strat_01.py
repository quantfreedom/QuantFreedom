import os
import numpy as np
import plotly.graph_objects as go

from datetime import datetime
from logging import getLogger
from typing import NamedTuple

from quantfreedom.helper_funcs import cart_product
from quantfreedom.indicators.tv_indicators import rsi_tv
from quantfreedom.enums import CandleBodyType
from quantfreedom.strategies.strategy import Strategy

logger = getLogger("info")


class IndicatorSettingsArrays(NamedTuple):
    rsi_is_above: np.array
    rsi_is_below: np.array
    rsi_length: np.array


class RSIBelowAbove(Strategy):
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
        self.indicator_settings_arrays: IndicatorSettingsArrays = IndicatorSettingsArrays(
            rsi_is_above=cart_arrays[0],
            rsi_is_below=cart_arrays[1],
            rsi_length=cart_arrays[2].astype(np.int_),
        )

        if long_short == "long":
            self.set_entries_exits_array = self.long_set_entries_exits_array
            self.log_indicator_settings = self.long_log_indicator_settings
            self.entry_message = self.long_entry_message
            self.live_evalutate = self.long_live_evaluate
        else:
            self.set_entries_exits_array = self.short_set_entries_exits_array
            self.log_indicator_settings = self.short_log_indicator_settings
            self.entry_message = self.short_entry_message
            self.live_evalutate = self.short_live_evaluate

    #######################################################
    #######################################################
    #######################################################
    ##################      short    ######################
    ##################      short    ######################
    ##################      short    ######################
    #######################################################
    #######################################################
    #######################################################

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

            self.entries = np.where(self.rsi > self.rsi_is_above, True, False)
            self.exit_prices = np.full_like(self.rsi, np.nan)

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

    #######################################################
    #######################################################
    #######################################################
    ##################      Long     ######################
    ##################      Long     ######################
    ##################      Long     ######################
    #######################################################
    #######################################################
    #######################################################

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

            self.entries = np.where(self.rsi < self.rsi_is_below, True, False)
            self.exit_prices = np.full_like(self.rsi, np.nan)

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

    #######################################################
    #######################################################
    #######################################################
    ##################      Live     ######################
    ##################      Live     ######################
    ##################      Live     ######################
    #######################################################
    #######################################################
    #######################################################

    def live_set_ind_settings(
        self,
        ind_set_index: int,
    ):
        self.rsi_is_below = self.indicator_settings_arrays.rsi_is_below[ind_set_index]
        self.rsi_is_above = self.indicator_settings_arrays.rsi_is_above[ind_set_index]
        self.rsi_length = self.indicator_settings_arrays.rsi_length[ind_set_index]
        logger.info(f"live_set_ind_settings finished")

    def live_set_indicator(
        self,
        close_prices: np.array,
    ):
        try:
            rsi = rsi_tv(
                length=self.rsi_length,
                source=close_prices,
            )
            self.rsi = np.around(rsi, 2)
            logger.info(f"Created RSI rsi_length= {self.rsi_length}")
        except Exception as e:
            logger.info(f"Exception live_set_indicator -> {e}")
            raise Exception(f"Exception live_set_indicator -> {e}")

    def long_live_evaluate(
        self,
        candles: np.array,
    ):
        try:
            self.live_set_indicator(close_prices=candles[:, CandleBodyType.Close])
            if self.rsi[-1] < self.rsi_is_below:
                logger.info("\n\n")
                logger.info(f"Entry time!!! rsi= {self.rsi[-1]} < rsi_is_below= {self.rsi_is_below}")
                return True
            else:
                logger.info("No entry")
                return False
        except Exception as e:
            raise Exception(f"Exception long_live_evaluate -> {e}")

    def short_live_evaluate(
        self,
        candles: np.array,
    ):
        try:
            self.live_set_indicator(close_prices=candles[:, CandleBodyType.Close])
            if self.rsi[-1] > self.rsi_is_above:
                logger.info("\n\n")
                logger.info(f"Entry time!!! rsi= {self.rsi[-1]} > rsi_is_above= {self.rsi_is_above}")
                return True
            else:
                logger.info("No entry")
                return False
        except Exception as e:
            raise Exception(f"Exception short_live_evaluate -> {e}")

    #######################################################
    #######################################################
    #######################################################
    ##################      Plot     ######################
    ##################      Plot     ######################
    ##################      Plot     ######################
    #######################################################
    #######################################################
    #######################################################

    def get_strategy_plot_filename(
        self,
        candles: np.array,
    ):
        logger.debug("Getting entry plot file")
        last_50 = self.rsi[-50:]
        last_50_datetimes = candles[-50:, CandleBodyType.Timestamp].astype("datetime64[ms]")

        fig = go.Figure()
        fig.add_scatter(
            x=last_50_datetimes,
            y=last_50,
            name="RSI",
        )
        fig.update_layout(height=800, xaxis_rangeslider_visible=False)
        fig.show()
        entry_filename = os.path.join(
            ".",
            "logs",
            "images",
            f'indicator_{datetime.utcnow().strftime("%m-%d-%Y_%H-%M-%S")}.png',
        )
        fig.write_image(entry_filename)
        return entry_filename
