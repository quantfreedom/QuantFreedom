import numpy as np
from numba import njit
import pandas as pd

from quantfreedom.core.enums import (
    AccountState,
    DynamicOrderSettings,
    DynamicOrderSettings,
    FootprintCandlesTuple,
    OrderResult,
    OrderStatus,
)
from numba.cpython.unicode import _empty_string, _set_code_point, PY_UNICODE_1BYTE_KIND

DIGITS_START = 48
DIGITS_END = 58
DASH = 45
DOT = 46
PLUS = 43
E_CHAR = 101


@njit(cache=True)
def nb_get_qf_score(
    gains_pct: float,
    wins_and_losses_array_no_be: np.ndarray,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

    xm = x.mean()
    ym = y.mean()

    y_ym = y - ym
    if (y_ym == 0).all():
        y_ym = np.array([1.0])
    y_ym_s = np.power(y_ym, 2)

    x_xm = x - xm
    if (x_xm == 0).all():
        x_xm = np.array([1.0])
    x_xm_s = np.power(x_xm, 2)

    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
    b0 = ym - b1 * xm

    y_pred = b0 + b1 * x

    yp_ym = y_pred - ym

    yp_ym_s = np.power(yp_ym, 2)

    qf_score = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        qf_score = -(qf_score)
    return round(qf_score, 2)


@njit(cache=True)
def nb_get_dos(
    dos_tuple: DynamicOrderSettings,
    set_idx: int,
):
    return DynamicOrderSettings(
        max_equity_risk_pct=dos_tuple.max_equity_risk_pct[set_idx],
        max_trades=dos_tuple.max_trades[set_idx],
        account_pct_risk_per_trade=dos_tuple.account_pct_risk_per_trade[set_idx],
        risk_reward=dos_tuple.risk_reward[set_idx],
        sl_based_on_add_pct=dos_tuple.sl_based_on_add_pct[set_idx],
        sl_based_on_lookback=dos_tuple.sl_based_on_lookback[set_idx],
        sl_bcb_type=dos_tuple.sl_bcb_type[set_idx],
        sl_to_be_cb_type=dos_tuple.sl_to_be_cb_type[set_idx],
        sl_to_be_when_pct=dos_tuple.sl_to_be_when_pct[set_idx],
        trail_sl_bcb_type=dos_tuple.trail_sl_bcb_type[set_idx],
        trail_sl_by_pct=dos_tuple.trail_sl_by_pct[set_idx],
        trail_sl_when_pct=dos_tuple.trail_sl_when_pct[set_idx],
    )


@njit(cache=True)
def nb_create_ao(
    starting_equity: float,
):
    account_state = AccountState(
        # where we are at
        set_idx=-1,
        bar_index=-1,
        timestamp=-1,
        # account info
        available_balance=starting_equity,
        cash_borrowed=0.0,
        cash_used=0.0,
        equity=starting_equity,
        fees_paid=0.0,
        total_possible_loss=0,
        realized_pnl=0.0,
        total_trades=0,
    )
    order_result = OrderResult(
        average_entry=0.0,
        can_move_sl_to_be=False,
        entry_price=0.0,
        entry_size_asset=0.0,
        entry_size_usd=0.0,
        exit_price=0.0,
        leverage=1.0,
        liq_price=0.0,
        order_status=OrderStatus.Nothing,
        position_size_asset=0.0,
        position_size_usd=0.0,
        sl_pct=0.0,
        sl_price=0.0,
        tp_pct=0.0,
        tp_price=0.0,
    )
    return account_state, order_result


@njit(cache=True)
def nb_round_size_by_tick_step(
    exchange_num: float,
    user_num: float,
) -> float:
    return round(user_num, exchange_num)


@njit(cache=True)
def nb_get_n_digits(x):
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


# @njit(cache=True)
# def nb_float_to_str(x: float):
#     return str(x)


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
        l1, l2 = nb_get_n_digits(offset_x)
    elif is_neg_exp:
        offset_x = np.around(x * (10 ** -(e)), 15)
        l1, l2 = nb_get_n_digits(offset_x)
    else:
        offset_x = x
        l1, l2 = nb_get_n_digits(x)
        l2 = max(1, 2)  # Will have at least .0

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


@njit(cache=True)
def nb_fill_order_records(
    account_state: AccountState,
    or_index: int,
    order_records: np.ndarray,
    order_result: OrderResult,
):
    order_records["ind_set_idx"] = account_state.set_idx
    order_records["or_set_idx"] = account_state.set_idx
    order_records["bar_idx"] = account_state.bar_index
    order_records["timestamp"] = account_state.timestamp

    order_records["equity"] = account_state.equity
    order_records["available_balance"] = account_state.available_balance
    order_records["cash_borrowed"] = account_state.cash_borrowed
    order_records["cash_used"] = account_state.cash_used

    order_records["average_entry"] = order_result.average_entry
    order_records["fees_paid"] = account_state.fees_paid
    order_records["leverage"] = order_result.leverage
    order_records["liq_price"] = order_result.liq_price
    order_records["order_status"] = order_result.order_status
    order_records["total_possible_loss"] = account_state.total_possible_loss
    order_records["total_trades"] = account_state.total_trades
    order_records["entry_size_asset"] = order_result.entry_size_asset
    order_records["entry_size_usd"] = order_result.entry_size_usd
    order_records["entry_price"] = order_result.entry_price
    order_records["exit_price"] = order_result.exit_price
    order_records["position_size_asset"] = order_result.position_size_asset
    order_records["position_size_usd"] = order_result.position_size_usd
    order_records["realized_pnl"] = account_state.realized_pnl
    order_records["sl_pct"] = round(order_result.sl_pct * 100, 2)
    order_records["sl_price"] = order_result.sl_price
    order_records["tp_pct"] = round(order_result.tp_pct * 100, 2)
    order_records["tp_price"] = order_result.tp_price
    return or_index + 1
