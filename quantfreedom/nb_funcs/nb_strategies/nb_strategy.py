import numpy as np
from numba import njit
from quantfreedom.nb_funcs.nb_indicators.nb_indicators import nb_rsi_tv

from typing import Callable, NamedTuple

from quantfreedom.enums import CandleBodyType, LoggerFuncType, StringerFuncType


class IndicatorSettings(NamedTuple):
    rsi_is_below: np.array
    rsi_period: np.array


class IndicatorSettings(NamedTuple):
    rsi_is_below: float
    rsi_period: int


ind_set_arrays = IndicatorSettings(
    rsi_is_below=np.array([40, 60, 80]),
    rsi_period=np.array([14, 20]),
)


def strat_create_ind_cart_product(
    ind_set_arrays: IndicatorSettings,
):
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

    return IndicatorSettings(
        rsi_is_below=out.T[0],
        rsi_period=out.T[1].astype(np.int_),
    )


ind_set_arrays = strat_create_ind_cart_product(ind_set_arrays=ind_set_arrays)


@njit(cache=True)
def nb_strat_bt_create_ind(
    bar_index: int,
    candles: np.array,
    candle_group_size: int,
    indicator_settings_tuple: IndicatorSettings,
    logger: Callable,
):
    start = max(bar_index - candle_group_size, 0)
    try:
        rsi = nb_rsi_tv(
            source=candles[start : bar_index + 1, CandleBodyType.Close],
            length=indicator_settings_tuple.rsi_period,
        )
        rsi = np.around(rsi, 3)
        logger("nb_strategy.py - nb_strat_bt_create_ind() - Created RSI")
        return rsi
    except Exception:
        logger("nb_strategy.py - nb_strat_bt_create_ind() - Exception creating RSI")
        raise Exception


@njit(cache=True)
def nb_strat_liv_create_ind(
    bar_index: int,
    candle_group_size: int,
    candles: int,
    indicator_settings_tuple: IndicatorSettings,
    logger: Callable,
):
    try:
        rsi = nb_rsi_tv(
            source=candles[:, CandleBodyType.Close],
            length=indicator_settings_tuple.rsi_period,
        )
        rsi = np.around(rsi, 3)
        logger("nb_strategy.py - nb_strat_liv_create_ind() - Created RSI")
        return rsi
    except Exception:
        logger("nb_strategy.py - nb_strat_liv_create_ind() - Exception creating rsi")
        raise Exception


@njit(cache=True)
def nb_strat_get_total_ind_settings():
    return ind_set_arrays[0].size


@njit(cache=True)
def nb_strat_get_current_ind_settings(
    ind_set_index: int,
    logger: Callable,
):
    indicator_settings_tuple = IndicatorSettings(
        rsi_is_below=ind_set_arrays.rsi_is_below[ind_set_index],
        rsi_period=ind_set_arrays.rsi_period[ind_set_index],
    )
    logger("nb_strategy.py - nb_get_current_ind_settings() - Created indicator settings")
    return indicator_settings_tuple


@njit(cache=True)
def nb_strat_get_ind_set_str(
    indicator_settings_tuple: IndicatorSettings,
    stringer: list,
):
    msg = (
        "nb_strategy.py - nb_strat_get_ind_set_str() - "
        + "RSI Period= "
        + str(indicator_settings_tuple.rsi_period)
        + " RSI is below= "
        + stringer[StringerFuncType.float_to_str](indicator_settings_tuple.rsi_is_below)
    )
    return msg


@njit(cache=True)
def nb_strat_long_evaluate(
    bar_index: int,
    candles: np.array,
    candle_group_size: int,
    indicator_settings_tuple: IndicatorSettings,
    logger: Callable,
    nb_strat_ind_creator: Callable,
    stringer: list,
):
    rsi = nb_strat_ind_creator(
        bar_index=bar_index,
        candle_group_size=candle_group_size,
        candles=candles,
        indicator_settings_tuple=indicator_settings_tuple,
        logger=logger,
    )
    try:
        current_rsi = rsi[-1]
        rsi_is_below = indicator_settings_tuple.rsi_is_below

        if current_rsi < rsi_is_below:
            logger("\n\n")
            logger(
                "nb_strategy.py - nb_evaluate() - Entry time!!! "
                + "current rsi= "
                + stringer[StringerFuncType.float_to_str](current_rsi)
                + " < rsi_is_below= "
                + stringer[StringerFuncType.float_to_str](rsi_is_below)
            )

            return True
        else:
            logger(
                "nb_strategy.py - nb_evaluate() - No entry "
                + "current rsi= "
                + stringer[StringerFuncType.float_to_str](current_rsi)
            )
            return False
    except Exception:
        raise Exception("nb_strategy.py - nb_evaluate() - Exception evalutating strat")
