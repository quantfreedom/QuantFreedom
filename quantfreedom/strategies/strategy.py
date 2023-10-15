import os
import numpy as np

from quantfreedom.enums import CandleProcessingType
from quantfreedom.custom_logger import CustomLogger


DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FORMATTER = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(message)s"


# class IndicatorSettingsArrays(NamedTuple):
#     rsi_length: np.array = np.array([14, 20])
#     rsi_is_below: np.array = np.array([200, 75])


# indicator_settings_array = IndicatorSettingsArrays()


# def create_ind_cart_product():
#     n = 1
#     for x in indicator_settings_array:
#         n *= x.size
#     out = np.empty((n, len(indicator_settings_array)))

#     for i in range(len(indicator_settings_array)):
#         m = int(n / indicator_settings_array[i].size)
#         out[:n, i] = np.repeat(indicator_settings_array[i], m)
#         n //= indicator_settings_array[i].size

#     n = indicator_settings_array[-1].size
#     for k in range(len(indicator_settings_array) - 2, -1, -1):
#         n *= indicator_settings_array[k].size
#         m = int(n / indicator_settings_array[k].size)
#         for j in range(1, indicator_settings_array[k].size):
#             out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

#     return IndicatorSettingsArrays(
#         rsi_length=out.T[0],
#         rsi_is_below=out.T[1],
#     )


class Strategy:
    set_indicator_settings = None
    create_indicator = None
    indicator_cart_product = None
    current_exit_signals = None

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
        self.candles = candles
        self.candle_processing_mode = candle_processing_mode
        CustomLogger(
            log_debug=log_debug,
            disable_logging=disable_logging,
            custom_path=custom_path,
            formatter=formatter,
            create_trades_logger=create_trades_logger,
        )

        # self.indicator_settings_arrays = create_ind_cart_product()

        # if candle_processing_mode == CandleProcessingType.Backtest:
        #     self.closing_prices = candles[:, 3]
        #     self.create_indicator = self.__set_bar_index
        #     self.current_exit_signals = np.full_like(self.closing_prices, np.nan)
        #     self.set_indicator_settings = self.__set_ids_and_indicator

        # elif candle_processing_mode == CandleProcessingType.RealBacktest:
        #     self.bar_index = -1
        #     self.closing_prices = candles[:, 3]
        #     self.create_indicator = self.__set_indicator_candle_by_candle
        #     self.current_exit_signals = np.full_like(self.closing_prices, np.nan)
        #     self.set_indicator_settings = self.__set_ind_set

        # elif candle_processing_mode == CandleProcessingType.LiveTrading:
        #     self.bar_index = -1
        #     self.__set_ind_set(indicator_settings_index=indicator_settings_index)

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ################### Regular Backtest Functions Start ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_bar_index(self, bar_index, strat_num_candles):
        # self.bar_index = bar_index
        pass

    def __set_ids_and_indicator(self, indicator_settings_index: int):
        # self.rsi_length = int(self.indicator_settings_arrays.rsi_length[indicator_settings_index])
        # self.rsi_is_below = int(self.indicator_settings_arrays.rsi_is_below[indicator_settings_index])
        # info_logger.info(f"Indicator Settings: rsi_length={self.rsi_length} rsi_is_below={self.rsi_is_below}")
        # try:
        #     self.rsi = (
        #         pta.rsi(
        #             close=pd.Series(self.closing_prices),
        #             length=self.rsi_length,
        #         )
        #         .round(decimals=2)
        #         .shift(1, fill_value=np.nan)
        #         .values
        #     )
        # except Exception as e:
        #     raise Exception(f"Exception creating rsi -> {e}")
        pass

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ################### Candle by Candle Backtest Start  ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_indicator_candle_by_candle(self, bar_index, starting_bar):
        # bar_start = max(strat_num_candles + bar_index, 0)
        # closing_series = pd.Series(self.closing_prices[bar_start : bar_index + 1])
        # try:
        #     self.rsi = (
        #         pta.rsi(
        #             close=closing_series,
        #             length=self.rsi_length,
        #         )
        #         .round(decimals=2)
        #         .shift(1, fill_value=np.nan)
        #         .values
        #     )
        # except Exception as e:
        #     raise Exception(f"Exception creating rsi -> {e}")
        pass

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################      Live Trading Start          ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def set_indicator_live_trading(self, candles):
        # try:
        #     self.rsi = pta.rsi(close=pd.Series(candles[:, 3]), length=self.rsi_length).round(decimals=2).values
        #     info_logger.debug("Created rsi entry")
        # except Exception as e:
        #     raise Exception(f"Exception creating rsi -> {e}")
        pass

    #########################################################################
    #########################################################################
    ###################                                  ####################
    ###################     Strategy Functions Start     ####################
    ###################                                  ####################
    #########################################################################
    #########################################################################

    def __set_ind_set(self, indicator_settings_index):
        # self.rsi_length = int(self.indicator_settings_arrays.rsi_length[indicator_settings_index])
        # self.rsi_is_below = int(self.indicator_settings_arrays.rsi_is_below[indicator_settings_index])
        # info_logger.info(f"Indicator Settings: rsi_length={self.rsi_length} rsi_is_below={self.rsi_is_below}")
        pass

    def evaluate(self):
        # try:
        #     if self.rsi[self.bar_index] < self.rsi_is_below:
        #         info_logger.info(f"\n\n")
        #         info_logger.info(f"Entry time!!! rsi {self.rsi[self.bar_index]} is below {self.rsi_is_below}")
        #         return True
        #     else:
        #         info_logger.info(f"No entry rsi {self.rsi[self.bar_index]}")
        #         return False
        # except Exception as e:
        #     raise Exception(f"Strategy class evaluate error -> {e}")
        pass

    def get_strategy_plot_filename(self, **vargs):
        pass

    def create_ind_cart_product_nb(self, indicator_settings_array):
        # cart array loop
        # n = 1
        # for x in indicator_settings_array:
        #     n *= x.size
        # out = np.empty((n, len(indicator_settings_array)))

        # for i in range(len(indicator_settings_array)):
        #     m = int(n / indicator_settings_array[i].size)
        #     out[:n, i] = np.repeat(indicator_settings_array[i], m)
        #     n //= indicator_settings_array[i].size

        # n = indicator_settings_array[-1].size
        # for k in range(len(indicator_settings_array) - 2, -1, -1):
        #     n *= indicator_settings_array[k].size
        #     m = int(n / indicator_settings_array[k].size)
        #     for j in range(1, indicator_settings_array[k].size):
        #         out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

        # return IndicatorSettingsArrays(
        #     rsi_length=out.T[0],
        #     rsi_is_below=out.T[1],
        # )
        pass
