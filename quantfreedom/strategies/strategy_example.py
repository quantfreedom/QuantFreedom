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
    rsi_length: np.array
    rsi_is_below: np.array


class StrategyExample(Strategy):
    set_indicator_settings = None
    num_candles = None
    create_indicator = None

    def __init__(
        self,
        rsi_length: [np.array, list],
        rsi_is_below: [np.array, list],
        #
        # My stuff up top
        #
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

        self.candles = candles
        self.indicator_settings_arrays = IndicatorSettingsArrays(
            rsi_length=np.asarray(rsi_length),
            rsi_is_below=np.asarray(rsi_is_below),
        )

        self.__set_ind_cart_product()

        if candle_processing_mode == CandleProcessingType.Backtest:
            self.create_indicator = self.__set_bar_index
            self.current_exit_signals = np.full_like(candles["close"], np.nan)
            self.set_indicator_settings = self.__set_ids_and_indicator

        elif candle_processing_mode == CandleProcessingType.RealBacktest:
            self.bar_index = -1
            self.create_indicator = self.__set_indicator_real_backtest
            self.current_exit_signals = np.full_like(candles["close"], np.nan)
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

    def __set_bar_index(self, bar_index, **vargs):
        self.bar_index = bar_index
        info_logger.debug(f"Set bar index in strat")

    def __set_ids_and_indicator(self, indicator_settings_index: int):
        self.rsi_length = self.indicator_cart_product.rsi_length[indicator_settings_index]
        self.rsi_is_below = self.indicator_cart_product.rsi_is_below[indicator_settings_index]
        info_logger.info(f"Indicator Settings: rsi_length={self.rsi_length} rsi_is_below={self.rsi_is_below}")
        try:
            self.rsi = np.around(talib.RSI(self.candles["close"], self.rsi_length), 2)
            info_logger.debug("Created rsi entry")
        except Exception as e:
            raise Exception(f"Exception creating rsi -> {e}")

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################        Real Backtesting          ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_indicator_real_backtest(self, bar_index, starting_bar):
        start = max(bar_index - starting_bar, 0)
        try:
            self.rsi = np.around(talib.RSI(self.candles["close"][start : bar_index + 1], self.rsi_length), 2)
            info_logger.debug("Created rsi entry")
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
            self.rsi = np.around(talib.RSI(candles["close"], self.rsi_length), 2)
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
        self.rsi_length = self.indicator_cart_product.rsi_length[indicator_settings_index]
        self.rsi_is_below = self.indicator_cart_product.rsi_is_below[indicator_settings_index]
        info_logger.info(f"Indicator Settings: rsi_length={self.rsi_length} rsi_is_below={self.rsi_is_below}")

    def evaluate(self):
        try:
            current_rsi = self.rsi[self.bar_index]
            if current_rsi < self.rsi_is_below:
                info_logger.info(f"\n\n")
                info_logger.info(f"Entry time!!! rsi {current_rsi} is below {self.rsi_is_below}")
                return True
            else:
                info_logger.info(f"No entry rsi {current_rsi}")
                return False
        except Exception as e:
            raise Exception(f"Strategy class evaluate error -> {e}")

    def __set_ind_cart_product(self):
        n = 1
        for x in self.indicator_settings_arrays:
            n *= x.size
        out = np.empty((n, len(self.indicator_settings_arrays)))

        for i in range(len(self.indicator_settings_arrays)):
            m = int(n / self.indicator_settings_arrays[i].size)
            out[:n, i] = np.repeat(self.indicator_settings_arrays[i], m)
            n //= self.indicator_settings_arrays[i].size

        n = self.indicator_settings_arrays[-1].size
        for k in range(len(self.indicator_settings_arrays) - 2, -1, -1):
            n *= self.indicator_settings_arrays[k].size
            m = int(n / self.indicator_settings_arrays[k].size)
            for j in range(1, self.indicator_settings_arrays[k].size):
                out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

        self.indicator_cart_product = IndicatorSettingsArrays(
            rsi_length=out.T[0].astype(np.int_),
            rsi_is_below=out.T[1].astype(np.int_),
        )
