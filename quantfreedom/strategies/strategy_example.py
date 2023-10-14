import logging
import pandas as pd
import numpy as np
import talib

from typing import NamedTuple

from quantfreedom.enums import CandleProcessingType
import logging

from quantfreedom.strategies.strategy import DIR_PATH, FORMATTER, Strategy


info_logger = logging.getLogger("info")


class IndicatorSettingsArrays(NamedTuple):
    rsi_length: np.array = np.array([14, 20])
    rsi_is_below: np.array = np.array([200, 75])


indicator_settings_array = IndicatorSettingsArrays()


def create_ind_cart_product():
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
        rsi_length=out.T[0].astype(np.int_),
        rsi_is_below=out.T[1].astype(np.int_),
    )


class StrategyExample(Strategy):
    set_indicator_settings = None
    num_candles = None
    create_indicator = None

    def __init__(
        self,
        candle_processing_mode: CandleProcessingType,
        candles: np.array = None,
        indicator_settings_index: int = None,
        log_debug: bool = True,
        disable_logging: bool = False,
        custom_path: str = DIR_PATH,
        formatter: str = FORMATTER,
        create_trades_logger: bool = False,
    ) -> None:
        super().__init__(
            candle_processing_mode,
            candles,
            indicator_settings_index,
            log_debug,
            disable_logging,
            custom_path,
            formatter,
            create_trades_logger,
        )

        self.indicator_settings_arrays = create_ind_cart_product()

        if candle_processing_mode == CandleProcessingType.Backtest:
            self.closing_prices = candles[:, 3]
            self.create_indicator = self.__set_bar_index
            self.current_exit_signals = np.full_like(self.closing_prices, np.nan)
            self.set_indicator_settings = self.__set_ids_and_indicator

        elif candle_processing_mode == CandleProcessingType.RealBacktest:
            self.bar_index = -1
            self.closing_prices = candles[:, 3]
            self.create_indicator = self.__set_indicator_real_backtest
            self.current_exit_signals = np.full_like(self.closing_prices, np.nan)
            self.set_indicator_settings = self.__set_ind_set

        elif candle_processing_mode == CandleProcessingType.LiveTrading:
            self.bar_index = -1
            self.__set_ind_set(indicator_settings_index=indicator_settings_index)

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ################### Regular Backtest Functions Start ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_bar_index(self, bar_index, strat_num_candles):
        self.bar_index = bar_index

    def __set_ids_and_indicator(self, indicator_settings_index: int):
        """
        we have to shift the indicator by one so that way we enter on the right candle
        if we have a yes entry on candle 15 then in real life we wouldn't enter until 16
        so that is why we have to shift by one

        if you have an exit then you don't have to shift
        """
        self.rsi_length = self.indicator_settings_arrays.rsi_length[indicator_settings_index]
        self.rsi_is_below = self.indicator_settings_arrays.rsi_is_below[indicator_settings_index]
        info_logger.info(f"Indicator Settings: rsi_length={self.rsi_length} rsi_is_below={self.rsi_is_below}")
        try:
            self.rsi = np.around(talib.RSI(self.candles.values[:,3], 14),2)
        except Exception as e:
            raise Exception(f"Exception creating rsi -> {e}")

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################        Real Backtesting          ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_indicator_real_backtest(self, bar_index, strat_num_candles):
        """
        we have to shift the info by one so that way we enter on the right candle
        if we have a yes entry on candle 15 then in real life we wouldn't enter until 16
        so that is why we have to shift by one
        """
        start = max(strat_num_candles + bar_index, 0)
        closing_series = pd.Series(self.closing_prices[start : bar_index + 1])
        try:
            self.rsi = (
                pta.rsi(
                    close=closing_series,
                    length=self.rsi_length,
                )
                .round(decimals=2)
                .values
            )
        except Exception as e:
            raise Exception(f"Exception creating rsi -> {e}")

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################      Live Trading Start          ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def set_indicator_live_trading(self, candles):
        try:
            self.rsi = pta.rsi(close=pd.Series(candles[:, 3]), length=self.rsi_length).round(decimals=2).values
            info_logger.debug("Created rsi entry")
        except Exception as e:
            raise Exception(f"Exception creating rsi -> {e}")

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################     Strategy Functions Start     ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_ind_set(self, indicator_settings_index):
        self.rsi_length = self.indicator_settings_arrays.rsi_length[indicator_settings_index]
        self.rsi_is_below = self.indicator_settings_arrays.rsi_is_below[indicator_settings_index]
        info_logger.info(f"Indicator Settings: rsi_length={self.rsi_length} rsi_is_below={self.rsi_is_below}")

    def evaluate(self):
        try:
            if self.rsi[self.bar_index] < self.rsi_is_below:
                info_logger.info(f"\n\n")
                info_logger.info(f"Entry time!!! rsi {self.rsi[self.bar_index]} is below {self.rsi_is_below}")
                return True
            else:
                info_logger.info(f"No entry rsi {self.rsi[self.bar_index]}")
                return False
        except Exception as e:
            raise Exception(f"Strategy class evaluate error -> {e}")