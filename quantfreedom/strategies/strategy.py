import numpy as np
from numba import njit
from quantfreedom.indicators.indicators import qf_calc_rsi

from typing import NamedTuple

from quantfreedom.enums import CandleBodyType, LoggerFuncType, StringerFuncType


class IndicatorSettingsArrays(NamedTuple):
    rsi_is_below: np.array
    rsi_period: np.array


class IndicatorSettings(NamedTuple):
    rsi_is_below: float
    rsi_period: int


ind_set_arrays = IndicatorSettingsArrays(
    rsi_is_below=np.array([70, 50, 30]),
    rsi_period=np.array([14, 20]),
)


def create_ind_cart_product(ind_set_arrays: IndicatorSettingsArrays):
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
        rsi_period=out.T[1].astype(np.int_),
    )


ind_set_arrays = create_ind_cart_product(ind_set_arrays=ind_set_arrays)


@njit(cache=True)
def strat_bt_create_ind(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    logger,
):
    start = max(bar_index - starting_bar, 0)
    try:
        rsi = qf_calc_rsi(
            prices=candles[start : bar_index + 1, CandleBodyType.Close],
            period=indicator_settings.rsi_period,
        )
        rsi = np.around(rsi, 2)
        logger[LoggerFuncType.Info](".strategy.py - strat_bt_create_ind() - Created RSI")
        return rsi
    except Exception:
        logger[LoggerFuncType.Info](".strategy.py - strat_bt_create_ind() - Exception creating RSI")
        raise Exception


@njit(cache=True)
def strat_liv_create_ind(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    logger,
):
    try:
        rsi = qf_calc_rsi(
            prices=candles[:, CandleBodyType.Close],
            period=indicator_settings.rsi_period,
        )
        rsi = np.around(rsi, 2)
        logger[LoggerFuncType.Info](".strategy.py - strat_liv_create_ind() - Created RSI")
        return rsi
    except Exception:
        logger[LoggerFuncType.Info](".strategy.py - strat_liv_create_ind() - Exception creating rsi")
        raise Exception


@njit(cache=True)
def strat_get_total_ind_settings():
    return ind_set_arrays[0].size


@njit(cache=True)
def strat_get_current_ind_settings(
    ind_set_index: int,
    logger,
):
    indicator_settings = IndicatorSettings(
        rsi_is_below=ind_set_arrays.rsi_is_below[ind_set_index],
        rsi_period=ind_set_arrays.rsi_period[ind_set_index],
    )
    logger[LoggerFuncType.Info](".strategy.py - get_current_ind_settings() - Created indicator settings")
    return indicator_settings


@njit(cache=True)
def strat_get_ind_set_str(
    indicator_settings: IndicatorSettings,
    stringer,
):
    msg = (
        ".strategy.py - strat_get_ind_set_str() - "
        + "RSI Period= "
        + str(indicator_settings.rsi_period)
        + " RSI is below= "
        + stringer[StringerFuncType.float_to_str](indicator_settings.rsi_is_below)
    )
    return msg


@njit(cache=True)
def strat_evaluate(
    bar_index,
    starting_bar,
    candles,
    indicator_settings: IndicatorSettings,
    ind_creator,
    logger,
    stringer,
):
    rsi = ind_creator(
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
            logger[LoggerFuncType.Info]("\n\n")
            logger[LoggerFuncType.Info](
                ".strategy.py - evaluate() - Entry time!!! "
                + "current rsi= "
                + stringer[StringerFuncType.float_to_str](current_rsi)
                + " < rsi_is_below= "
                + stringer[StringerFuncType.float_to_str](rsi_is_below)
            )

            return True
        else:
            logger[LoggerFuncType.Info](
                ".strategy.py - evaluate() - No entry "
                + "current rsi= "
                + stringer[StringerFuncType.float_to_str](current_rsi)
            )
            return False
    except Exception:
        raise Exception(".strategy.py - evaluate() - Exception evalutating strat")
