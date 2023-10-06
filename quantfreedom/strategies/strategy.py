from datetime import datetime
import logging
import os
import pandas_ta as pta
import pandas as pd
import numpy as np

from typing import NamedTuple
from plotly.subplots import make_subplots

from quantfreedom.enums import CandleProcessingType


class IndicatorSettingsArrays(NamedTuple):
    rsi_lenth: np.array = np.array([14, 30])
    rsi_is_below: np.array = np.array([70, 60])


class Strategy:
    indicator_settings_index = None
    num_candles = None

    def __init__(
        self,
        candle_processing_mode: CandleProcessingType,
        candles: pd.DataFrame = None,
        indicator_settings_index: int = None,
    ) -> None:
        self.candles = candles
        self.indicator_settings_arrays = self.create_ind_cart_product_nb(IndicatorSettingsArrays())

        if candle_processing_mode == CandleProcessingType.RegularBacktest:
            self.current_exit_signals = np.full_like(candles.close.values, np.nan)
            self.create_indicator = self.__set_bar_index
            self.closing_prices = candles.close
            self.set_indicator_settings(indicator_settings_index=0)
            self.__set_rsi()
        elif candle_processing_mode == CandleProcessingType.CandleBacktest:
            self.current_exit_signals = np.full_like(candles.close.values, np.nan)
            self.create_indicator = self.__create_indicator_candle_by_candle
            self.bar_index = -1
        elif candle_processing_mode == CandleProcessingType.LiveTrading:
            self.set_indicator_settings(indicator_settings_index)
            self.bar_index = -1

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ################### Regular Backtest Functions Start ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_bar_index(self, bar_index):
        self.bar_index = bar_index

    def __set_rsi(self):
        """
        we have to shift the info by one so that way we enter on the right candle
        if we have a yes entry on candle 15 then in real life we wouldn't enter until 16
        so that is why we have to shift by one
        """
        try:
            self.rsi = (
                pta.rsi(
                    close=self.closing_prices,
                    length=self.rsi_lenth,
                )
                .round(decimals=2)
                .shift(1, fill_value=np.nan)
            )
        except Exception as e:
            Exception(f"Strategy class __get_rsi = Something went wrong creating rsi -> {e}")

    def get_rsi(self):
        return self.rsi

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ################### Candle by Candle Backtest Start  ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __create_indicator_candle_by_candle(self, bar_index):
        """
        we have to shift the info by one so that way we enter on the right candle
        if we have a yes entry on candle 15 then in real life we wouldn't enter until 16
        so that is why we have to shift by one
        """
        bar_start = max(self.num_candles + bar_index, 0)
        self.closing_prices = self.candles.close.iloc[bar_start : bar_index + 1]
        self.rsi_exit = pta.rsi(
            close=self.closing_prices,
            length=self.rsi_lenth,
        ).round(decimals=2)
        self.rsi_entry = (
            pta.rsi(
                close=self.closing_prices,
                length=self.rsi_lenth,
            )
            .round(decimals=2)
            .shift(1, fill_value=np.nan)
        )

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################      Live Trading Start          ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def set_indicator_live_trading(self, candles):
        try:
            self.rsi = pta.rsi(close=candles.close, length=self.rsi_lenth).round(decimals=2)
        except Exception as e:
            Exception(f"Strategy class set_indicator_live_trading = Something went wrong creating rsi -> {e}")

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################     Strategy Functions Start     ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def set_indicator_settings(self, indicator_settings_index):
        self.rsi_lenth = int(self.indicator_settings_arrays.rsi_lenth[indicator_settings_index])
        self.rsi_is_below = int(self.indicator_settings_arrays.rsi_is_below[indicator_settings_index])

    def evaluate(self):
        try:
            # exit price
            if self.rsi_exit.iloc[self.bar_index] > 60:
                self.current_exit_signals[self.bar_index] = self.candles.close.values[self.bar_index]

            if self.rsi_entry.iloc[self.bar_index] < self.rsi_is_below:
                return True
            else:
                return False
        except Exception as e:
            Exception(f"Strategy class evaluate -> {e}")

    def return_plot_image(self, candles: pd.DataFrame, entry_price, sl_price, tp_price, liq_price, **vargs):
        graph_entry = [candles.index.iloc[-1]]
        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            vertical_spacing=0.02,
        )
        fig.add_candlestick(
            x=candles.index,
            open=candles.open,
            high=candles.high,
            low=candles.low,
            close=candles.close,
            name="Candles",
            row=1,
            col=1,
        )
        # entry
        fig.add_scatter(
            x=graph_entry,
            y=[entry_price],
            mode="markers",
            marker=dict(size=10, color="Blue"),
            name=f"Entry",
            row=1,
            col=1,
        )
        # take profit
        fig.add_scatter(
            x=graph_entry,
            y=[tp_price],
            mode="markers",
            marker=dict(size=10, symbol="arrow-up", color="Green"),
            name=f"Take Profit",
            row=1,
            col=1,
        )
        # stop loss
        fig.add_scatter(
            x=graph_entry,
            y=[sl_price],
            mode="markers",
            marker=dict(size=10, symbol="octagon", color="orange"),
            name=f"Stop Loss",
            row=1,
            col=1,
        )
        # liq price
        fig.add_scatter(
            x=graph_entry,
            y=[liq_price],
            mode="markers",
            marker=dict(size=10, symbol="hexagram", color="red"),
            name=f"Liq Price",
            row=1,
            col=1,
        )

        # RSI
        fig.add_scatter(
            x=candles.index,
            y=self.rsi,
            name="RSI",
            row=2,
            col=1,
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
        fig_filename = os.path.join(
            ".",
            "logs",
            "images",
            f'{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.png',
        )
        fig.write_image(fig_filename)
        return fig_filename

    def create_ind_cart_product_nb(self, indicator_settings_array):
        # cart array loop
        n = 1
        for x in indicator_settings_array:
            n *= x.size
        out = np.empty((n, len(indicator_settings_array)))

        for i in range(len(indicator_settings_array)):
            m = int(n / indicator_settings_array[i].size)
            out[:n, i] = np.repeat(indicator_settings_array[i], m)
            n //= indicator_settings_array[i].size

        n = indicator_settings_array[-1].size
        for k in range(len(indicator_settings_array) - 2, -1, -1):
            n *= indicator_settings_array[k].size
            m = int(n / indicator_settings_array[k].size)
            for j in range(1, indicator_settings_array[k].size):
                out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

        return IndicatorSettingsArrays(
            rsi_lenth=out.T[0],
            rsi_is_below=out.T[1],
        )
