import numpy as np
from numba import njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.enums import OrderType

@njit(cache=True)
def tester_thing(
    num: float,
):
    return num

@njit(cache=True)
def order_not_filled_nb(
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    leverage: float,
    liq_price: float,
    order_status: int,
    order_status_info: int,
    position: float,
    sl_pcts: float,
    sl_prices: float,
    tp_pcts: float,
    tp_prices: float,
    tsl_pcts: float,
    tsl_prices: float,
):
    """
    If for whatever reason your order isn't filled this is where it goes. It first calculates any stop prices then sends
    back the reason why your order wasn't filled.

    Args:
        order: See [Order][backtester.enums.enums.OrderEverything].
        status: See [status][backtester.enums.enums.OrderStatusT].
        status_info: See [status_info][backtester.enums.enums.OrderStatusInfoT].
    """

    return available_balance,\
        average_entry,\
        cash_borrowed,\
        cash_used,\
        leverage,\
        liq_price,\
        order_status,\
        order_status_info,\
        position,\
        sl_pcts,\
        sl_prices,\
        tp_pcts,\
        tp_prices,\
        tsl_pcts,\
        tsl_prices

# fill order records


@njit(cache=True)
def fill_order_records_nb(
    average_entry: float,
    bar: int,  # time stamp
    col: int,
    equity: float,
    fees_paid: float,
    indicator_settings_counter: int,
    max_equity_risk_pct: float,
    order_count_id: int,
    order_records: tp.RecordArray,
    order_settings_counter: int,
    order_type: int,
    price: float,
    realized_pnl: float,
    risk_rewards: float,
    size_value: float,
    sl_pcts: float,
):
    # long entry
    if order_type == OrderType.LongEntry:
        side = 0
        coin_size = size_value / price

    # long stops
    elif OrderType.LongLiq <= order_type <= OrderType.LongTSL:
        side = 1
        coin_size = size_value / average_entry

    # Short entry
    elif order_type == OrderType.ShortEntry:
        side = 1
        coin_size = size_value / price

    # Short stops
    elif OrderType.ShortLiq <= order_type <= OrderType.ShortTSL:
        side = 0
        coin_size = size_value / average_entry

    order_records['col'] = col
    order_records['equity'] = equity
    order_records['fees'] = fees_paid
    order_records['id'] = order_count_id
    order_records['idx'] = bar  # time stamp
    order_records['ind_set'] = indicator_settings_counter
    order_records['max_eq_risk_pct'] = max_equity_risk_pct
    order_records['or_set'] = order_settings_counter
    order_records['price'] = price
    order_records['real_pnl'] = round(realized_pnl, 4)
    order_records['rr'] = risk_rewards
    order_records['side'] = side
    order_records['size'] = coin_size
    order_records['size_usd'] = size_value
    order_records['sl_pct'] = sl_pcts


@njit(cache=True)
def fill_log_records_nb(
    average_entry: float,
    bar: int,  # time stamp
    col: int,
    log_count_id: int,
    log_records: tp.RecordArray,
    order_count_id: int,
    order_type: int,
    price: float,
    realized_pnl: float,
    sl_prices: float,
    tsl_prices: float,
    tp_prices: float,
) -> None:
    """
    Filling the log records.

    Args:
        log_records: See [log Numpy Data Type][backtester.enums.enums.log_dt].
        bar: The current bar you are at in the loop of the coin (col).
        col: col usually represents the number of which coin you are in. \
        So lets say you are testing BTC and ETH, BTC would be col 0 and ETH would be col 1.
        group: If you group up your coins or anything else this will keep track of the group you are in.
        log_count_id: The id of the log count.
        order_count_id: The id of the order count.
        order_result: See [Order][backtester.enums.enums.ResultEverything].
        account_state: See [Account_State][backtester.enums.enums.AccountAndTradeState].
        new_account_state: See [Account_State][backtester.enums.enums.AccountAndTradeState].

    !!! note
        if you want to create your own sections within the array to store then you need to add them here, then
        go over to the log data type and add the same thing there.

    """

    log_records['avg_entry'] = average_entry
    log_records['bar'] = bar  # time stamp
    log_records['col'] = col
    log_records['id_log'] = log_count_id
    log_records['id_order'] = order_count_id
    log_records['order_price'] = price
    log_records['order_type'] = order_type
    log_records['sl_prices'] = sl_prices
    log_records['tp_prices'] = tp_prices
    log_records['tsl_prices'] = tsl_prices
    log_records['real_pnl'] = round(realized_pnl, 4) if not np.isnan(
        realized_pnl) else realized_pnl


@njit(cache=True)
def to_1d_array_nb(
    var: tp.ArrayLike
) -> tp.ArrayLike:
    """Resize array to one dimension."""
    if var.ndim == 0:
        return np.expand_dims(var, axis=0)
    if var.ndim == 1:
        return var
    if var.ndim == 2 and var.shape[1] == 1:
        return var[:, 0]
    raise ValueError("to 1d array problem")


@njit(cache=True)
def to_2d_array_nb(
    var: tp.ArrayLike,
    expand_axis: int = 1
) -> tp.Array1d:
    if var.ndim == 0:
        return np.expand_dims(np.expand_dims(var, axis=0), axis=0)
    if var.ndim == 1:
        return np.expand_dims(var, axis=expand_axis)
    if var.ndim == 2:
        return var
    raise ValueError("to 2d array problem")
