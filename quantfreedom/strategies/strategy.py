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
    rsi_lenth: np.array = np.array([10, 15])
    rsi_is_below: np.array = np.array([100, 150, 200])


class Strategy:
    indicator_setting_index = None

    def __init__(
        self,
        candle_processing_mode: CandleProcessingType,
        candles: pd.DataFrame = None,
        num_candles: int = None,
        indicator_setting_index: int = None,
    ) -> None:
        self.candles = candles
        self.indicator_settings_array = self.__create_ind_cart_product_nb(IndicatorSettingsArrays())

        if candle_processing_mode == CandleProcessingType.RegularBacktest:
            self.create_indicator = self.__create_indicator_reg_backtest
            self.closing_prices = candles.close
            self.rsi = self.__get_rsi()
        elif candle_processing_mode == CandleProcessingType.BacktestCandleByCandle:
            if num_candles is None:
                raise TypeError("num candles has to be > 1 or not None when backtesting candle by candle")
            else:
                self.num_candles = -(num_candles - 1)
                self.set_price_data = self.__create_indicator_candle_by_candle
        elif candle_processing_mode == CandleProcessingType.LiveTrading:
            self.ind_settings_or_results(indicator_setting_index)
            self.bar_index = -1

    #########################################################################
    ###################                                  ####################
    ################### Regular Backtest Functions Start ####################
    ###################                                  ####################
    #########################################################################

    def __create_indicator_reg_backtest(self, bar_index):
        self.bar_index = bar_index

    #########################################################################
    ###################                                  ####################
    ################### Candle by Candle Backtest Start  ####################
    ###################                                  ####################
    #########################################################################

    def __create_indicator_candle_by_candle(self, bar_index):
        self.bar_index = bar_index
        bar_start = max(self.num_candles + bar_index, 0)
        self.closing_prices = self.candles.iloc[bar_start : bar_index + 1, 4]
        self.rsi = pta.rsi(close=self.closing_prices, length=self.rsi_lenth).round(decimals=2)

    #########################################################################
    ###################                                  ####################
    ###################      Live Trading Start          ####################
    ###################                                  ####################
    #########################################################################

    def set_indicator_live_trading(self, price_data):
        try:
            self.rsi = pta.rsi(close=price_data.close, length=self.rsi_lenth).round(decimals=2)
        except Exception as e:
            logging.error(f"Something went wrong creating rsi ")
            Exception(f"Something went wrong creating rsi ")

    #########################################################################
    ###################                                  ####################
    ###################     Strategy Functions Start     ####################
    ###################                                  ####################
    #########################################################################

    def ind_settings_or_results(self, indicator_setting_index):
        self.rsi_lenth = int(self.indicator_settings_array.rsi_lenth[indicator_setting_index])
        self.rsi_is_below = int(self.indicator_settings_array.rsi_is_below[indicator_setting_index])
        print(f"\n\nRSI lenth = {self.rsi_lenth} and RSI is below {self.rsi_is_below}")

    def evaluate(self):
        try:
            if self.rsi.iloc[self.bar_index] < self.rsi_is_below:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Something is wrong evaluting the RSI is below -> {e}")
            raise Exception(f"Something is wrong evaluting the RSI is below -> {e}")

    def return_plot_image(self, price_data: pd.DataFrame, entry_price, sl_price, tp_price, liq_price, **vargs):
        logging.info(f"return_plot_image(self, price_data: pd.DataFrame, entry_price")
        graph_entry = [price_data.timestamp.iloc[-1]]
        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            vertical_spacing=0.02,
        )
        fig.add_candlestick(
            x=price_data.timestamp,
            open=price_data.open,
            high=price_data.high,
            low=price_data.low,
            close=price_data.close,
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
            x=price_data.timestamp,
            y=self.rsi,
            name="RSI",
            row=2,
            col=1,
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
        fig_filename = os.path.join(
            ".",
            "images",
            f'{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.png',
        )
        fig.write_image(fig_filename)
        return fig_filename

    def __create_ind_cart_product_nb(self, indicator_settings_array):
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
