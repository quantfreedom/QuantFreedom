from datetime import datetime
from logging import getLogger
from quantfreedom.helper_funcs import cart_product
from quantfreedom.indicators.tv_indicators import rsi_tv

from typing import NamedTuple

from quantfreedom.enums import CandleBodyType
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from quantfreedom.strategies.strategy import Strategy

logger = getLogger("info")


class IndicatorSettingsArrays(NamedTuple):
    volatility_lb: np.array
    max_high_lb: np.array


class SimpleBreakoutDynamicLookback(Strategy):
    starting_bar: int

    def __init__(
        self,
        long_short: str,
        volatility_lb: np.array,
        max_high_lb: np.array,
    ) -> None:
        logger.debug("Creating Strategy class init")
        self.long_short = long_short

        cart_arrays = cart_product(
            named_tuple=IndicatorSettingsArrays(
                volatility_lb=volatility_lb,
                max_high_lb=max_high_lb,
            )
        )
        self.indicator_settings_arrays: IndicatorSettingsArrays = IndicatorSettingsArrays(
            volatility_lb=cart_arrays.T[0].astype(np.int_),
            max_high_lb=cart_arrays.T[1].astype(np.int_),
        )

        if long_short == "long":
            self.set_entries_exits_array = self.long_set_entries_exits_array
            self.log_indicator_settings = self.long_log_indicator_settings
            self.entry_message = self.long_entry_message
        else:
            self.set_entries_exits_array = self.short_set_entries_exits_array
            self.log_indicator_settings = self.short_log_indicator_settings
            self.entry_message = self.short_entry_message

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
        pass

    def short_log_indicator_settings(self, ind_set_index: int):
        pass

    def short_entry_message(self, bar_index: int):
        pass

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
            close = candles[:, CandleBodyType.Close]
            high = candles[:, CandleBodyType.High]

            self.volatility_lb = self.indicator_settings_arrays.volatility_lb[ind_set_index]
            self.max_high_lb = self.indicator_settings_arrays.max_high_lb[ind_set_index]

            self.max_high = np.full_like(close, np.nan)
            current_vol = np.std(close[0 : self.volatility_lb])

            vol_lb_m_1 = self.volatility_lb - 1

            for i in range(max(self.volatility_lb, self.max_high_lb), close.size):
                prev_vol = current_vol
                current_vol = np.std(close[i - vol_lb_m_1 : i + 1])

                delta_vol = (current_vol - prev_vol) / current_vol

                real_max_high_lb = self.max_high_lb * (1 + delta_vol)
                try:
                    self.max_high[i] = high[max(i - int(real_max_high_lb), 0) : i].max()
                except:
                    self.max_high[i] = high[i]

            self.entry_prices = np.where(close >= self.max_high, close, np.nan)

            self.entries = np.where(np.isnan(self.entry_prices), False, True)
            self.exit_prices = np.full_like(self.entries, np.nan)

        except Exception as e:
            logger.info(f"Exception long_set_entries_exits_array -> {e}")
            raise Exception(f"Exception long_set_entries_exits_array -> {e}")

    def long_log_indicator_settings(self, ind_set_index: int):
        logger.info(
            f"Indicator Settings Index= {ind_set_index}\
            \nvolatility_lb= {self.volatility_lb}\
            \nrmax_high_lb= {self.max_high_lb}"
        )

    def long_entry_message(self, bar_index: int):
        logger.info("\n\n")
        logger.info(
            f"Entry time!!! Close is higher than the High {self.entry_prices[bar_index]} > {self.max_high[bar_index]}"
        )

    #######################################################
    #######################################################
    #######################################################
    ##################      Live     ######################
    ##################      Live     ######################
    ##################      Live     ######################
    #######################################################
    #######################################################
    #######################################################

    def live_set_indicator(self, closes: np.array):
        pass

    def live_evaluate(self, candles: np.array):
        pass

    #######################################################
    #######################################################
    #######################################################
    ##################      Plot     ######################
    ##################      Plot     ######################
    ##################      Plot     ######################
    #######################################################
    #######################################################
    #######################################################

    def get_strategy_plot_filename(self, candles: np.array):
        logger.debug("Getting entry plot file")
        not_nan = ~np.isnan(self.entry_prices)
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=pd.to_datetime(candles[:, CandleBodyType.Timestamp], unit="ms"),
                    open=candles[:, 1],
                    high=candles[:, 2],
                    low=candles[:, 3],
                    close=candles[:, 4],
                    name="Candles",
                ),
                go.Scatter(
                    x=pd.to_datetime(candles[not_nan, CandleBodyType.Timestamp], unit="ms"),
                    y=self.entry_prices[not_nan],
                    name="entries",
                    mode="markers",
                    marker=dict(color="yellow"),
                ),
            ]
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
