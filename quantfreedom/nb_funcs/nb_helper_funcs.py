import numpy as np
from numba import njit
import pandas as pd

from quantfreedom.enums import AccountState, DynamicOrderSettings, DynamicOrderSettingsArrays, OrderResult
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

    qf_score = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        qf_score = -(qf_score)
    return round(qf_score, 3)


@njit(cache=True)
def nb_get_dos(
    dos_cart_arrays: DynamicOrderSettingsArrays,
    dos_index: int,
):
    return DynamicOrderSettings(
        max_equity_risk_pct=dos_cart_arrays.max_equity_risk_pct[dos_index],
        max_trades=dos_cart_arrays.max_trades[dos_index],
        risk_account_pct_size=dos_cart_arrays.risk_account_pct_size[dos_index],
        risk_reward=dos_cart_arrays.risk_reward[dos_index],
        sl_based_on_add_pct=dos_cart_arrays.sl_based_on_add_pct[dos_index],
        sl_based_on_lookback=dos_cart_arrays.sl_based_on_lookback[dos_index],
        sl_bcb_type=dos_cart_arrays.sl_bcb_type[dos_index],
        sl_to_be_cb_type=dos_cart_arrays.sl_to_be_cb_type[dos_index],
        sl_to_be_when_pct=dos_cart_arrays.sl_to_be_when_pct[dos_index],
        trail_sl_bcb_type=dos_cart_arrays.trail_sl_bcb_type[dos_index],
        trail_sl_by_pct=dos_cart_arrays.trail_sl_by_pct[dos_index],
        trail_sl_when_pct=dos_cart_arrays.trail_sl_when_pct[dos_index],
    )


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


@njit(cache=True)
def nb_fill_order_records(
    account_state: AccountState,
    or_index: int,
    order_records: np.array,
    order_result: OrderResult,
):
    order_records["ind_set_idx"] = account_state.ind_set_index
    order_records["or_set_idx"] = account_state.dos_index
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
    order_records["possible_loss"] = account_state.possible_loss
    order_records["total_trades"] = account_state.total_trades
    order_records["entry_size_asset"] = order_result.entry_size_asset
    order_records["entry_size_usd"] = order_result.entry_size_usd
    order_records["entry_price"] = order_result.entry_price
    order_records["exit_price"] = order_result.exit_price
    order_records["position_size_asset"] = order_result.position_size_asset
    order_records["position_size_usd"] = order_result.position_size_usd
    order_records["realized_pnl"] = account_state.realized_pnl
    order_records["sl_pct"] = round(order_result.sl_pct * 100, 3)
    order_records["sl_price"] = order_result.sl_price
    order_records["tp_pct"] = round(order_result.tp_pct * 100, 3)
    order_records["tp_price"] = order_result.tp_price
    return or_index + 1


def order_records_to_df(order_records: np.array):
    order_records_df = pd.DataFrame(order_records)
    order_records_df.insert(4, "datetime", pd.to_datetime(order_records_df.timestamp, unit="ms"))
    order_records_df.replace(
        {
            "order_status": {
                0: "HitMaxTrades",
                1: "EntryFilled",
                2: "StopLossFilled",
                3: "TakeProfitFilled",
                4: "LiquidationFilled",
                5: "MovedSLToBE",
                6: "MovedTSL",
                7: "MaxEquityRisk",
                8: "RiskToBig",
                9: "CashUsedExceed",
                10: "EntrySizeTooSmall",
                11: "EntrySizeTooBig",
                12: "PossibleLossTooBig",
                13: "Nothing",
            }
        },
        inplace=True,
    )
    order_records_df[
        [
            "equity",
            "available_balance",
            "cash_borrowed",
            "cash_used",
            "average_entry",
            "fees_paid",
            "leverage",
            "liq_price",
            "possible_loss",
            "entry_size_asset",
            "entry_size_usd",
            "entry_price",
            "exit_price",
            "position_size_asset",
            "position_size_usd",
            "realized_pnl",
            "sl_pct",
            "sl_price",
            "tp_pct",
            "tp_price",
        ]
    ] = order_records_df[
        [
            "equity",
            "available_balance",
            "cash_borrowed",
            "cash_used",
            "average_entry",
            "fees_paid",
            "leverage",
            "liq_price",
            "possible_loss",
            "entry_size_asset",
            "entry_size_usd",
            "entry_price",
            "exit_price",
            "position_size_asset",
            "position_size_usd",
            "realized_pnl",
            "sl_pct",
            "sl_price",
            "tp_pct",
            "tp_price",
        ]
    ].replace(
        {0: np.nan}
    )
    return order_records_df


def get_data_for_plotting(order_records_df: pd.DataFrame, candles: np.array):
    data = {
        "candles": candles.tolist(),
    }
    timestamp_list = candles[:, 0].tolist()

    temp_entries_df = order_records_df[
        ["order_status", "timestamp", "average_entry", "entry_price", "liq_price", "sl_price", "tp_price"]
    ]
    entries_df = temp_entries_df[temp_entries_df["order_status"] == "EntryFilled"]
    entries_list_df = entries_df.values[:, 1:].tolist()

    entries_list = np.vstack(candles[:, 0]).tolist()
    sl_list = np.vstack(candles[:, 0]).tolist()
    tp_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == entries_list_df[0][0]:
            current_entry = entries_list_df[0]
            entries_list[idx] = [current_entry[0], current_entry[2]]
            sl_list[idx] = [current_entry[0], current_entry[4]]
            tp_list[idx] = [current_entry[0], current_entry[5]]
            del entries_list_df[0]
            if len(entries_list_df) == 0:
                break
    data["entries"] = entries_list
    data["sl_prices"] = sl_list
    data["tp_prices"] = tp_list

    temp_sl_filled_df = order_records_df[["order_status", "timestamp", "exit_price"]]
    sl_filled_df = temp_sl_filled_df[temp_sl_filled_df["order_status"] == "StopLossFilled"]
    sl_filled_list_df = sl_filled_df.values[:, 1:].tolist()
    filled_sl_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == sl_filled_list_df[0][0]:
            filled_sl_list[idx] = sl_filled_list_df[0]
            del sl_filled_list_df[0]
            if len(sl_filled_list_df) == 0:
                break
    data["sl_filled"] = filled_sl_list

    temp_tp_filled_df = order_records_df[["order_status", "timestamp", "exit_price"]]
    tp_filled_df = temp_tp_filled_df[temp_tp_filled_df["order_status"] == "TakeProfitFilled"]
    tp_filled_list_df = tp_filled_df.values[:, 1:].tolist()
    filled_tp_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == tp_filled_list_df[0][0]:
            filled_tp_list[idx] = tp_filled_list_df[0]
            del tp_filled_list_df[0]
            if len(tp_filled_list_df) == 0:
                break
    data["tp_filled"] = filled_tp_list

    temp_tp_filled_df = order_records_df[["order_status", "timestamp", "sl_price"]]
    moved_sl_df = temp_tp_filled_df[
        (temp_tp_filled_df["order_status"] == "MovedTSL") | (temp_tp_filled_df["order_status"] == "MovedSLToBE")
    ]
    moved_sl_list_df = moved_sl_df.values[:, 1:].tolist()
    moved_sl_list = np.vstack(candles[:, 0]).tolist()
    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == moved_sl_list_df[0][0]:
            moved_sl_list[idx] = moved_sl_list_df[0]
            del moved_sl_list_df[0]
            if len(moved_sl_list_df) == 0:
                break
    data["moved_sl"] = moved_sl_list

    return data


def get_data_for_plotting(order_records_df: pd.DataFrame, candles: np.array):
    data = {
        "candles": candles.tolist(),
    }
    timestamp_list = candles[:, 0].tolist()

    temp_entries_df = order_records_df[
        ["order_status", "timestamp", "average_entry", "entry_price", "liq_price", "sl_price", "tp_price"]
    ]
    entries_df = temp_entries_df[temp_entries_df["order_status"] == "EntryFilled"]
    entries_list_df = entries_df.values[:, 1:].tolist()

    entries_list = np.vstack(candles[:, 0]).tolist()
    sl_list = np.vstack(candles[:, 0]).tolist()
    tp_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == entries_list_df[0][0]:
            current_entry = entries_list_df[0]
            entries_list[idx] = [current_entry[0], current_entry[2]]
            sl_list[idx] = [current_entry[0], current_entry[4]]
            tp_list[idx] = [current_entry[0], current_entry[5]]
            del entries_list_df[0]
            if len(entries_list_df) == 0:
                break
    data["entries"] = entries_list
    data["sl_prices"] = sl_list
    data["tp_prices"] = tp_list

    filled_sl_list = np.vstack(candles[:, 0]).tolist()
    try:
        temp_sl_filled_df = order_records_df[["order_status", "timestamp", "exit_price"]]
        sl_filled_df = temp_sl_filled_df[temp_sl_filled_df["order_status"] == "StopLossFilled"]
        sl_filled_list_df = sl_filled_df.values[:, 1:].tolist()

        for idx, timestamp in enumerate(timestamp_list):
            if timestamp == sl_filled_list_df[0][0]:
                filled_sl_list[idx] = sl_filled_list_df[0]
                del sl_filled_list_df[0]
                if len(sl_filled_list_df) == 0:
                    break
    except:
        pass

    data["sl_filled"] = filled_sl_list

    filled_tp_list = np.vstack(candles[:, 0]).tolist()
    try:
        temp_tp_filled_df = order_records_df[["order_status", "timestamp", "exit_price"]]
        tp_filled_df = temp_tp_filled_df[temp_tp_filled_df["order_status"] == "TakeProfitFilled"]
        tp_filled_list_df = tp_filled_df.values[:, 1:].tolist()

        for idx, timestamp in enumerate(timestamp_list):
            if timestamp == tp_filled_list_df[0][0]:
                filled_tp_list[idx] = tp_filled_list_df[0]
                del tp_filled_list_df[0]
                if len(tp_filled_list_df) == 0:
                    break
    except:
        pass
    data["tp_filled"] = filled_tp_list

    moved_sl_list = np.vstack(candles[:, 0]).tolist()
    try:
        temp_tp_filled_df = order_records_df[["order_status", "timestamp", "sl_price"]]
        moved_sl_df = temp_tp_filled_df[
            (temp_tp_filled_df["order_status"] == "MovedTSL") | (temp_tp_filled_df["order_status"] == "MovedSLToBE")
        ]
        moved_sl_list_df = moved_sl_df.values[:, 1:].tolist()
        for idx, timestamp in enumerate(timestamp_list):
            if timestamp == moved_sl_list_df[0][0]:
                moved_sl_list[idx] = moved_sl_list_df[0]
                del moved_sl_list_df[0]
                if len(moved_sl_list_df) == 0:
                    break
    except:
        pass
    data["moved_sl"] = moved_sl_list

    return data


def order_records_to_df(order_records: np.array):
    order_records_df = pd.DataFrame(order_records)
    order_records_df.insert(4, "datetime", pd.to_datetime(order_records_df.timestamp, unit="ms"))
    order_records_df.replace(
        {
            "order_status": {
                0: "HitMaxTrades",
                1: "EntryFilled",
                2: "StopLossFilled",
                3: "TakeProfitFilled",
                4: "LiquidationFilled",
                5: "MovedSLToBE",
                6: "MovedTSL",
                7: "MaxEquityRisk",
                8: "RiskToBig",
                9: "CashUsedExceed",
                10: "EntrySizeTooSmall",
                11: "EntrySizeTooBig",
                12: "PossibleLossTooBig",
                13: "Nothing",
            }
        },
        inplace=True,
    )
    order_records_df[
        [
            "equity",
            "available_balance",
            "cash_borrowed",
            "cash_used",
            "average_entry",
            "fees_paid",
            "leverage",
            "liq_price",
            "possible_loss",
            "entry_size_asset",
            "entry_size_usd",
            "entry_price",
            "exit_price",
            "position_size_asset",
            "position_size_usd",
            "realized_pnl",
            "sl_pct",
            "sl_price",
            "tp_pct",
            "tp_price",
        ]
    ] = order_records_df[
        [
            "equity",
            "available_balance",
            "cash_borrowed",
            "cash_used",
            "average_entry",
            "fees_paid",
            "leverage",
            "liq_price",
            "possible_loss",
            "entry_size_asset",
            "entry_size_usd",
            "entry_price",
            "exit_price",
            "position_size_asset",
            "position_size_usd",
            "realized_pnl",
            "sl_pct",
            "sl_price",
            "tp_pct",
            "tp_price",
        ]
    ].replace(
        {0: np.nan}
    )
    return order_records_df
