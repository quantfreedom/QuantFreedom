import logging
import pandas_ta as pta
import pandas as pd
import numpy as np

from typing import NamedTuple

from quantfreedom.enums import CandleProcessingType


class IndicatorSettingsArrays(NamedTuple):
    rsi_lenth: np.array = np.array([10, 15])
    rsi_is_below: np.array = np.array([30, 40, 50])


class Strategy:
    indicator_setting_index = None

    def __init__(
        self,
        candles: pd.DataFrame = None,
        candle_processing_mode: CandleProcessingType = None,
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
        self.rsi = self.__get_rsi()

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
            if self.rsi[self.bar_index] < self.rsi_is_below:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Something is wrong evaluting the strat -> {repr(e)}")
            raise Exception

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
