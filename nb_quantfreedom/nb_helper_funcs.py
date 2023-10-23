import plotly.graph_objects as go
import numpy as np
import logging
import pandas as pd

# from nb_quantfreedom.nb_custom_logger import CustomLoggerNB
from nb_quantfreedom.nb_enums import DynamicOrderSettings, DynamicOrderSettingsArrays
from numba import njit

import numpy as np
import numba
from numba import types, njit
from numba.cpython.unicode import _empty_string, _set_code_point, PY_UNICODE_1BYTE_KIND
from numba.extending import overload_method

DIGITS_START = 48
DIGITS_END = 58
DASH = 45
DOT = 46
PLUS = 43
E_CHAR = 101


@njit()
def nb_min_max_price_getter(
    self,
    logger_debug: numba.types.FunctionType,
    bar_index: int,
    candles: np.array,
    candle_body_type: int,
    lookback: int,
) -> float:
    price = candles[lookback : bar_index + 1 :, candle_body_type].min()
    logger_debug(
        "nb_class_helpers.py - nb_GetMinPrice - nb_min_max_price_getter() -"
        + " candle_body_type= "
        + logger.candle_body_str(candle_body_type)
        + " price= "
        + logger.float_to_str(price)
    )
    return price


@njit(cache=True)
def get_to_the_upside_nb(
    gains_pct: float,
    wins_and_losses_array_no_be: np.array,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

    xm = x.mean()
    ym = y.mean()

    y_ym = y - ym
    if y_ym.all() == 0:
        y_ym = np.array([1.0])
    y_ym_s = np.power(y_ym, 2)

    x_xm = x - xm
    if x_xm.all() == 0:
        x_xm = np.array([1.0])
    x_xm_s = np.power(x_xm, 2)

    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
    b0 = ym - b1 * xm

    y_pred = b0 + b1 * x

    yp_ym = y_pred - ym

    yp_ym_s = np.power(yp_ym, 2)

    to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        to_the_upside = -to_the_upside
    return round(to_the_upside, 3)


def nb_dos_cart_product(dos_arrays: DynamicOrderSettingsArrays):
    # cart array loop
    n = 1
    for x in dos_arrays:
        n *= x.size
    out = np.empty((n, len(dos_arrays)))

    for i in range(len(dos_arrays)):
        m = int(n / dos_arrays[i].size)
        out[:n, i] = np.repeat(dos_arrays[i], m)
        n //= dos_arrays[i].size

    n = dos_arrays[-1].size
    for k in range(len(dos_arrays) - 2, -1, -1):
        n *= dos_arrays[k].size
        m = int(n / dos_arrays[k].size)
        for j in range(1, dos_arrays[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    return DynamicOrderSettingsArrays(
        entry_size_asset=out.T[0],
        max_equity_risk_pct=out.T[1] / 100,
        max_trades=out.T[2].astype(np.int_),
        num_candles=out.T[3].astype(np.int_),
        risk_account_pct_size=out.T[4] / 100,
        risk_reward=out.T[5],
        sl_based_on_add_pct=out.T[6] / 100,
        sl_based_on_lookback=out.T[7].astype(np.int_),
        sl_bcb_type=out.T[8].astype(np.int_),
        sl_to_be_cb_type=out.T[9].astype(np.int_),
        sl_to_be_when_pct=out.T[10] / 100,
        sl_to_be_ze_type=out.T[11].astype(np.int_),
        static_leverage=out.T[12],
        trail_sl_bcb_type=out.T[13].astype(np.int_),
        trail_sl_by_pct=out.T[14] / 100,
        trail_sl_when_pct=out.T[15] / 100,
    )


@njit(cache=True)
def nb_get_dos(
    dos_cart_arrays: DynamicOrderSettingsArrays,
    dos_index: int,
):
    return DynamicOrderSettings(
        entry_size_asset=dos_cart_arrays.entry_size_asset[dos_index],
        max_equity_risk_pct=dos_cart_arrays.max_equity_risk_pct[dos_index],
        max_trades=dos_cart_arrays.max_trades[dos_index],
        num_candles=dos_cart_arrays.num_candles[dos_index],
        risk_account_pct_size=dos_cart_arrays.risk_account_pct_size[dos_index],
        risk_reward=dos_cart_arrays.risk_reward[dos_index],
        sl_based_on_add_pct=dos_cart_arrays.sl_based_on_add_pct[dos_index],
        sl_based_on_lookback=dos_cart_arrays.sl_based_on_lookback[dos_index],
        sl_bcb_type=dos_cart_arrays.sl_bcb_type[dos_index],
        sl_to_be_cb_type=dos_cart_arrays.sl_to_be_cb_type[dos_index],
        sl_to_be_when_pct=dos_cart_arrays.sl_to_be_when_pct[dos_index],
        sl_to_be_ze_type=dos_cart_arrays.sl_to_be_ze_type[dos_index],
        static_leverage=dos_cart_arrays.static_leverage[dos_index],
        trail_sl_bcb_type=dos_cart_arrays.trail_sl_bcb_type[dos_index],
        trail_sl_by_pct=dos_cart_arrays.trail_sl_by_pct[dos_index],
        trail_sl_when_pct=dos_cart_arrays.trail_sl_when_pct[dos_index],
    )


@njit(cache=True)
def nb_round_size_by_tick_step(user_num: float, exchange_num: float) -> float:
    return round(user_num, exchange_num)


@njit(cache=True)
def get_n_digits(x):
    l1, l2 = 0, -1
    _x = x
    while _x > 0:
        _x = _x // 10
        l1 += 1

    _x = x % 10
    while _x > 1e-10:
        _x = (_x * 10) % 10
        l2 += 1
        if l2 >= 16:
            break
    return l1, l2


@njit(cache=True)
def nb_float_to_str(x: float):
    if x == np.inf:
        return "inf"
    elif x == -np.inf:
        return "-inf"
    elif x == 0:
        return "0.0"

    isneg = int(x < 0.0)
    x = np.abs(x)

    if x != 0.0:
        # There is probably a more efficient way to do this
        e = np.floor(np.log10(x))
        if 10**e - x > 0:
            e -= 1
    else:
        e = 0

    is_exp, is_neg_exp = e >= 16, e <= -16

    exp_chars = 0
    if is_exp or is_neg_exp:
        exp_chars = 4
        if e >= 100 or e <= -100:
            exp_chars = 5

    if is_exp:
        offset_x = np.around(x * (10.0 ** -(e)), 15)
        l1, l2 = get_n_digits(offset_x)
    elif is_neg_exp:
        offset_x = np.around(x * (10 ** -(e)), 15)
        l1, l2 = get_n_digits(offset_x)
    else:
        offset_x = x
        l1, l2 = get_n_digits(x)
        l2 = max(1, 3)  # Will have at least .0

    use_dec = l2 > 0

    # print("<<", e, offset_x, l2)

    l = l1 + l2 + use_dec
    length = l + isneg + exp_chars
    s = _empty_string(PY_UNICODE_1BYTE_KIND, length)
    if isneg:
        _set_code_point(s, 0, DASH)

    _x = offset_x
    for i in range(l1):
        digit = int(_x % 10)
        _set_code_point(s, (isneg + l1) - i - 1, digit + DIGITS_START)
        _x = _x // 10

    if use_dec:
        _set_code_point(s, l1 + isneg, DOT)

    _x = offset_x % 10
    for i in range(l2):
        _x = (_x * 10) % 10
        digit = int(_x)

        _set_code_point(s, (isneg + l1) + i + use_dec, digit + DIGITS_START)

    if is_exp or is_neg_exp:
        i = isneg + l1 + use_dec + l2
        _set_code_point(s, i, E_CHAR)
        if is_exp:
            _set_code_point(s, i + 1, PLUS)
        if is_neg_exp:
            _set_code_point(s, i + 1, DASH)

        i = length - 1
        exp = np.abs(e)
        while exp > 0:
            digit = exp % 10
            _set_code_point(s, i, digit + DIGITS_START)
            exp = exp // 10
            i -= 1

    return s
