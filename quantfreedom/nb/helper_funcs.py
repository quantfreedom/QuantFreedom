import numpy as np
from numba import njit

from quantfreedom.poly.enums import OrderSettingsArrays


@njit(cache=True)
def create_os_cart_product_nb(
    order_settings_arrays: OrderSettingsArrays,
):
    # cart array loop
    n = 1
    for x in order_settings_arrays:
        n *= x.size
    out = np.empty((n, len(order_settings_arrays)))

    for i in range(len(order_settings_arrays)):
        m = int(n / order_settings_arrays[i].size)
        out[:n, i] = np.repeat(order_settings_arrays[i], m)
        n //= order_settings_arrays[i].size

    n = order_settings_arrays[-1].size
    for k in range(len(order_settings_arrays) - 2, -1, -1):
        n *= order_settings_arrays[k].size
        m = int(n / order_settings_arrays[k].size)
        for j in range(1, order_settings_arrays[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    return OrderSettingsArrays(
        risk_account_pct_size=out.T[0],
        sl_based_on_add_pct=out.T[1],
        sl_based_on_lookback=out.T[2],
        risk_reward=out.T[3],
        leverage_type=out.T[4],
        candle_body=out.T[5],
        entry_size_type=out.T[6],
        stop_loss_type=out.T[7],
        take_profit_type=out.T[8],
    )


@njit(cache=True)
def boradcast_to_1d_arrays_nb(
    order_settings_arrays: OrderSettingsArrays,
    entries: Array2d,
):
    x = 0
    biggest = 1
    while x <= 6:
        if order_settings_arrays[x].size > 1:
            biggest = order_settings_arrays[x].size
            x += 1
            break
        x += 1

    while x < 7:
        if (
            order_settings_arrays[x].size > 1
            and order_settings_arrays[x].size != biggest
        ):
            raise ValueError("Size mismatch")
        x += 1
    if biggest > 6:
        raise ValueError("Total amount of tests must be <= 6")

    leverage_broadcast_array = np.broadcast_to(order_settings_arrays[0], biggest)
    max_equity_risk_pct_broadcast_array = np.broadcast_to(
        order_settings_arrays[1], biggest
    )
    max_equity_risk_value_broadcast_array = np.broadcast_to(
        order_settings_arrays[2], biggest
    )
    risk_reward_broadcast_array = np.broadcast_to(order_settings_arrays[3], biggest)
    size_pct_broadcast_array = np.broadcast_to(order_settings_arrays[4], biggest)
    size_value_broadcast_array = np.broadcast_to(order_settings_arrays[5], biggest)
    sl_based_on_broadcast_array = np.broadcast_to(order_settings_arrays[6], biggest)
    sl_based_on_add_pct_broadcast_array = np.broadcast_to(
        order_settings_arrays[7], biggest
    )
    sl_based_on_lookback_broadcast_array = np.broadcast_to(
        order_settings_arrays[8], biggest
    )
    sl_pct_broadcast_array = np.broadcast_to(order_settings_arrays[9], biggest)
    sl_to_be_based_on_broadcast_array = np.broadcast_to(
        order_settings_arrays[10], biggest
    )
    sl_to_be_when_pct_from_avg_entry_broadcast_array = np.broadcast_to(
        order_settings_arrays[11], biggest
    )
    sl_to_be_zero_or_entry_broadcast_array = np.broadcast_to(
        order_settings_arrays[12], biggest
    )
    tp_pct_broadcast_array = np.broadcast_to(order_settings_arrays[13], biggest)
    trail_sl_based_on_broadcast_array = np.broadcast_to(
        order_settings_arrays[14], biggest
    )
    trail_sl_by_pct_broadcast_array = np.broadcast_to(
        order_settings_arrays[15], biggest
    )
    trail_sl_when_pct_from_avg_entry_broadcast_array = np.broadcast_to(
        order_settings_arrays[16], biggest
    )

    if entries.shape[1] == 1:
        entries = np.broadcast_to(entries, (entries.shape[0], biggest))
    elif entries.shape[1] != biggest:
        raise ValueError("Something is wrong with entries")

    return entries, OrderSettingsArrays(
        leverage=leverage_broadcast_array,
        max_equity_risk_pct=max_equity_risk_pct_broadcast_array,
        max_equity_risk_value=max_equity_risk_value_broadcast_array,
        risk_reward=risk_reward_broadcast_array,
        size_pct=size_pct_broadcast_array,
        size_value=size_value_broadcast_array,
        sl_based_on=sl_based_on_broadcast_array,
        sl_based_on_add_pct=sl_based_on_add_pct_broadcast_array,
        sl_based_on_lookback=sl_based_on_lookback_broadcast_array,
        sl_pct=sl_pct_broadcast_array,
        sl_to_be_based_on=sl_to_be_based_on_broadcast_array,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_broadcast_array,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_broadcast_array,
        tp_pct=tp_pct_broadcast_array,
        trail_sl_based_on=trail_sl_based_on_broadcast_array,
        trail_sl_by_pct=trail_sl_by_pct_broadcast_array,
        trail_sl_when_pct_from_avg_entry=trail_sl_when_pct_from_avg_entry_broadcast_array,
    )


@njit(cache=True)
def get_to_the_upside_nb(
    gains_pct: float,
    wins_and_losses_array_no_be: Array1d,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

    xm = x.mean()
    ym = y.mean()

    y_ym = y - ym
    y_ym_s = y_ym**2

    x_xm = x - xm
    x_xm_s = x_xm**2

    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
    b0 = ym - b1 * xm

    y_pred = b0 + b1 * x

    yp_ym = y_pred - ym

    yp_ym_s = yp_ym**2

    to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        to_the_upside = -to_the_upside
    return to_the_upside


@njit(cache=True)
def fill_order_records_nb(
    bar: int,  # time stamp
    order_records: RecordArray,
    order_settings_counter: int,
    order_records_id: Array1d,
    account_state: AccountState,
    order_result: OrderResult,
) -> RecordArray:
    order_records["avg_entry"] = order_result.average_entry
    order_records["bar"] = bar
    order_records["equity"] = account_state.equity
    order_records["fees_paid"] = order_result.fees_paid
    order_records["order_set_id"] = order_settings_counter
    order_records["order_id"] = order_records_id[0]
    order_records["order_type"] = order_result.order_type
    order_records["price"] = order_result.price
    order_records["real_pnl"] = round(order_result.realized_pnl, 4)
    order_records["size_value"] = order_result.size_value
    order_records["sl_price"] = order_result.sl_price
    order_records["tp_price"] = order_result.tp_price

    order_records_id[0] += 1


@njit(cache=True)
def fill_strat_records_nb(
    entries_col: int,
    equity: float,
    order_settings_counter: int,
    pnl: float,
    strat_records_filled: Array1d,
    strat_records: RecordArray,
    symbol_counter: int,
) -> RecordArray:
    strat_records["equity"] = equity
    strat_records["entries_col"] = entries_col
    strat_records["or_set"] = order_settings_counter
    strat_records["symbol"] = symbol_counter
    strat_records["real_pnl"] = round(pnl, 4)

    strat_records_filled[0] += 1


@njit(cache=True)
def fill_strategy_result_records_nb(
    gains_pct: float,
    strategy_result_records: RecordArray,
    temp_strat_records: Array1d,
    to_the_upside: float,
    total_trades: int,
    wins_and_losses_array_no_be: Array1d,
) -> RecordArray:
    # win rate calc
    win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
    win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)

    total_pnl = temp_strat_records["real_pnl"][
        ~np.isnan(temp_strat_records["real_pnl"])
    ].sum()

    # strat array
    strategy_result_records["symbol"] = temp_strat_records["symbol"][0]
    strategy_result_records["entries_col"] = temp_strat_records["entries_col"][0]
    strategy_result_records["or_set"] = temp_strat_records["or_set"][0]
    strategy_result_records["total_trades"] = total_trades
    strategy_result_records["gains_pct"] = gains_pct
    strategy_result_records["win_rate"] = win_rate
    strategy_result_records["to_the_upside"] = to_the_upside
    strategy_result_records["total_pnl"] = total_pnl
    strategy_result_records["ending_eq"] = temp_strat_records["equity"][-1]


@njit(cache=True)
def fill_order_settings_result_records_nb(
    entries_col: int,
    order_settings_tuple: OrderSettings,
    order_settings_result_records: RecordArray,
    symbol_counter: int,
) -> RecordArray:
    order_settings_result_records["symbol"] = symbol_counter
    order_settings_result_records["entries_col"] = entries_col
    order_settings_result_records["leverage"] = order_settings_tuple.leverage
    order_settings_result_records["max_equity_risk_pct"] = (
        order_settings_tuple.max_equity_risk_pct * 100
    )
    order_settings_result_records[
        "max_equity_risk_value"
    ] = order_settings_tuple.max_equity_risk_value
    order_settings_result_records["risk_reward"] = order_settings_tuple.risk_reward
    order_settings_result_records["size_pct"] = order_settings_tuple.size_pct * 100
    order_settings_result_records["size_value"] = order_settings_tuple.size_value
    order_settings_result_records["sl_based_on"] = order_settings_tuple.sl_based_on
    order_settings_result_records["sl_based_on_add_pct"] = (
        order_settings_tuple.sl_based_on_add_pct * 100
    )
    order_settings_result_records[
        "sl_based_on_lookback"
    ] = order_settings_tuple.sl_based_on_lookback
    order_settings_result_records["sl_pct"] = order_settings_tuple.sl_pct * 100
    order_settings_result_records[
        "sl_to_be_based_on"
    ] = order_settings_tuple.sl_to_be_based_on
    order_settings_result_records["sl_to_be_when_pct_from_avg_entry"] = (
        order_settings_tuple.sl_to_be_when_pct_from_avg_entry * 100
    )
    order_settings_result_records[
        "sl_to_be_zero_or_entry"
    ] = order_settings_tuple.sl_to_be_zero_or_entry
    order_settings_result_records["tp_pct"] = order_settings_tuple.tp_pct * 100
    order_settings_result_records[
        "trail_sl_based_on"
    ] = order_settings_tuple.trail_sl_based_on
    order_settings_result_records["trail_sl_by_pct"] = (
        order_settings_tuple.trail_sl_by_pct * 100
    )
    order_settings_result_records["trail_sl_when_pct_from_avg_entry"] = (
        order_settings_tuple.trail_sl_when_pct_from_avg_entry * 100
    )


@njit(cache=True)
def to_1d_array_nb(var: PossibleArray) -> Array1d:
    """Resize array to one dimension."""
    if var.ndim == 0:
        return np.expand_dims(var, axis=0)
    if var.ndim == 1:
        return var
    if var.ndim == 2 and var.shape[1] == 1:
        return var[:, 0]
    raise ValueError("to 1d array problem")


@njit(cache=True)
def to_2d_array_nb(var: PossibleArray, expand_axis: int = 1) -> Array2d:
    if var.ndim == 0:
        return np.expand_dims(np.expand_dims(var, axis=0), axis=0)
    if var.ndim == 1:
        return np.expand_dims(var, axis=expand_axis)
    if var.ndim == 2:
        return var
    raise ValueError("to 2d array problem")
