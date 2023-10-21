import numpy as np
import talib
from numba.experimental import jitclass
from nb_quantfreedom.indicators.indicators import IndicatorsNB

from nb_quantfreedom.nb_custom_logger import CustomLoggerNB
from typing import NamedTuple

from nb_quantfreedom.nb_enums import CandleBodyType


class IndicatorSettingsArrays(NamedTuple):
    rsi_is_below: np.array
    rsi_length: np.array


class IndicatorSettings(NamedTuple):
    rsi_is_below: float
    rsi_length: int


ind_set_arrays = IndicatorSettingsArrays(
    rsi_is_below=np.array([50, 80]),
    rsi_length=np.array([14, 30]),
)


def nb_create_ind_cart_product(ind_set_arrays: IndicatorSettingsArrays):
    n = 1
    for x in ind_set_arrays:
        n *= x.size
    out = np.empty((n, len(ind_set_arrays)))

    for i in range(len(ind_set_arrays)):
        m = int(n / ind_set_arrays[i].size)
        out[:n, i] = np.repeat(ind_set_arrays[i], m)
        n //= ind_set_arrays[i].size

    n = ind_set_arrays[-1].size
    for k in range(len(ind_set_arrays) - 2, -1, -1):
        n *= ind_set_arrays[k].size
        m = int(n / ind_set_arrays[k].size)
        for j in range(1, ind_set_arrays[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    return IndicatorSettingsArrays(
        rsi_is_below=out.T[0],
        rsi_length=out.T[1].astype(np.int_),
    )


ind_set_arrays = nb_create_ind_cart_product(ind_set_arrays=ind_set_arrays)


class nb_CreateInd:
    def __init__(self) -> None:
        pass

    def create_indicator(
        self,
        bar_index,
        starting_bar,
        candles,
        indicator_settings: IndicatorSettings,
        logger: CustomLoggerNB,
    ):
        pass


@jitclass
class nb_BacktestInd(nb_CreateInd):
    def create_indicator(
        self,
        bar_index,
        starting_bar,
        candles,
        indicator_settings: IndicatorSettings,
        logger: CustomLoggerNB,
    ):
        start = max(bar_index - starting_bar, 0)
        try:
            rsi = IndicatorsNB().calc_rsi(prices=candles[:, CandleBodyType.Close], period=indicator_settings.rsi_length)
            logger.log_debug("Created rsi")
            return rsi
        except Exception:
            raise Exception("Exception creating rsi -> {e}")


@jitclass
class nb_TradingInd(nb_CreateInd):
    def create_indicator(
        self,
        bar_index,
        starting_bar,
        candles,
        indicator_settings: IndicatorSettings,
        logger: CustomLoggerNB,
    ):
        try:
            rsi = IndicatorsNB().calc_rsi(prices=candles[:, CandleBodyType.Close], period=indicator_settings.rsi_length)
            logger.log_debug("Created rsi")
            return rsi
        except Exception:
            raise Exception("Exception creating rsi -> {e}")


class StrategyClass:
    def __init__(self) -> None:
        pass


@jitclass
class nb_Strategy(StrategyClass):
    def get_total_ind_settings(self):
        return ind_set_arrays[0].size

    def nb_get_current_ind_settings(
        self,
        ind_set_index: int,
        logger: CustomLoggerNB,
    ):
        indicator_settings = IndicatorSettings(
            rsi_is_below=ind_set_arrays.rsi_is_below[ind_set_index],
            rsi_length=ind_set_arrays.rsi_length[ind_set_index],
        )
        logger.log_info("Created indicator settings")
        return indicator_settings

    def evaluate(
        self,
        bar_index,
        starting_bar,
        candles,
        indicator_settings: IndicatorSettings,
        ind_creator: nb_CreateInd,
        logger: CustomLoggerNB,
    ):
        return True
        rsi = ind_creator.create_indicator(
            bar_index=bar_index,
            starting_bar=starting_bar,
            candles=candles,
            indicator_settings=indicator_settings,
            logger=logger,
        )
        try:
            current_rsi = rsi[-1]
            rsi_is_below = indicator_settings.rsi_is_below

            if current_rsi < rsi_is_below:
                logger.log_info("\n\n")
                logger.log_info("Entry time!!! rsi {current_rsi} is below {rsi_is_below}")
                return True
            else:
                logger.log_info("No entry rsi {current_rsi}")
                return False
        except Exception:
            raise Exception("Evaluate strat error -> {e}")
