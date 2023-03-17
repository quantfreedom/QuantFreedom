import numpy as np
from numba import njit

from quantfreedom._typing import (
    RecordArray,
    ArrayLike,
    Array1d,
    Array2d
    )
from quantfreedom.backtester.enums import (
    AccountState,
    EntryOrder,
    OrderResult,
    RecordCounters,
    )


@njit(cache=True)
def fill_order_records_nb(
    bar: int,  # time stamp
    price: float,
    indicator_settings_counter: int,
    order_records: RecordArray,
    order_settings_counter: int,

    account_state: AccountState,
    entry_order: EntryOrder,
    order_result: OrderResult,
    record_counters: RecordCounters,
):

    order_records['equity'] = account_state.equity
    order_records['fees'] = order_result.fees_paid
    order_records['order_id'] = record_counters.order_count_id
    order_records['bar'] = bar
    order_records['ind_set'] = indicator_settings_counter
    order_records['max_eq_risk_pct'] = entry_order.max_equity_risk_pct
    order_records['or_set'] = order_settings_counter
    order_records['price'] = price
    order_records['real_pnl'] = round(order_result.realized_pnl, 4)
    order_records['rr'] = entry_order.risk_rewards
    order_records['order_type'] = order_result.order_type
    order_records['size_value'] = order_result.size_value
    order_records['sl_pct'] = order_result.sl_pcts


@njit(cache=True)
def fill_log_records_nb(
    bar: int,
    log_records: RecordArray, 
    price: float,
    
    order_result: OrderResult,
    record_counters: RecordCounters,
):

    log_records['avg_entry'] = order_result.average_entry
    log_records['bar'] = bar  # time stamp
    log_records['log_id'] = record_counters.log_count_id
    log_records['order_id'] = record_counters.order_count_id
    log_records['price'] = price
    log_records['order_type'] = order_result.order_type
    log_records['sl_prices'] = order_result.sl_prices
    log_records['tp_prices'] = order_result.tp_prices
    log_records['tsl_prices'] = order_result.tsl_prices
    log_records['real_pnl'] = round(order_result.realized_pnl, 4)


@njit(cache=True)
def to_1d_array_nb(
    var: ArrayLike
) -> Array1d:
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
    var: ArrayLike,
    expand_axis: int = 1
) -> Array2d:
    if var.ndim == 0:
        return np.expand_dims(np.expand_dims(var, axis=0), axis=0)
    if var.ndim == 1:
        return np.expand_dims(var, axis=expand_axis)
    if var.ndim == 2:
        return var
    raise ValueError("to 2d array problem")
