import numpy as np
from numba import njit

from quantfreedom._typing import (
    RecordArray,
    Array1d,
    Array2d,
    PossibleArray,
)

from quantfreedom.backtester.enums import (
    AccountState,
    OrderResult,
    OrderType,
    StaticVariables,
)


@njit(cache=True)
def static_var_checker(
    equity: float,
    fee_pct: float,
    mmr: float,
    lev_mode: int,
    order_type: int,
    size_type: int,
    max_lev: float,
    max_order_size_pct: float,
    min_order_size_pct: float,
    max_order_size_value: float,
    min_order_size_value: float,
    sl_to_be: bool,
    sl_to_be_then_trail: bool,
    tsl_true_or_false: bool,
    gains_pct_filter: float,
    total_trade_filter: int,
) -> tuple[StaticVariables]:
    if equity < 0 or not np.isfinite(equity):
        raise ValueError("YOU HAVE NO MONEY!!!! You Broke!!!!")

    if fee_pct < 0 or not np.isfinite(fee_pct):
        raise ValueError("fee_pct must be finite")

    if mmr < 0 or not np.isfinite(mmr):
        raise ValueError("mmr must be finite")

    if not np.isfinite(max_lev) or 1 > max_lev > 100:
        raise ValueError(
            "max lev has to be between 1 and 100")

    if not np.isfinite(min_order_size_pct) or .01 > min_order_size_pct > 100:
        raise ValueError(
            "min_order_size_pct  has to be between .01 and 100")

    if not np.isfinite(max_order_size_pct) or min_order_size_pct > max_order_size_pct > 100:
        raise ValueError(
            "max_order_size_pct has to be between min_order_size_pct and 100")

    if not np.isfinite(min_order_size_value) or min_order_size_value < 1:
        raise ValueError(
            "min_order_size_value has to be between .01 and 1 min inf")

    if np.isnan(max_order_size_value) or max_order_size_value < min_order_size_value:
        raise ValueError(
            "max_order_size_value has to be > min_order_size_value")

    if gains_pct_filter == np.inf:
        raise ValueError(
            "gains_pct_filter can't be inf")

    if total_trade_filter < 0 or not np.isfinite(total_trade_filter):
        raise ValueError(
            "total_trade_filter needs to be greater than 0")

    if sl_to_be == True and tsl_true_or_false == True:
        raise ValueError(
            "You can't have sl_to_be and tsl_true_or_false both be true")

    if sl_to_be != True and sl_to_be != False:
        raise ValueError(
            "sl_to_be needs to be true or false")

    if sl_to_be_then_trail != True and sl_to_be_then_trail != False:
        raise ValueError(
            "sl_to_be_then_trail needs to be true or false")

    if tsl_true_or_false != True and tsl_true_or_false != False:
        raise ValueError(
            "tsl_true_or_false needs to be true or false")

    # simple check if order size type is valid
    if 0 > order_type > len(OrderType) or not np.isfinite(order_type):
        raise ValueError("order_type is invalid")

    # Static variables creation
    fee_pct /= 100
    mmr /= 100
    max_order_size_pct /= 100
    min_order_size_pct /= 100

    return StaticVariables(
        fee_pct=fee_pct,
        lev_mode=lev_mode,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_pct=min_order_size_pct,
        min_order_size_value=min_order_size_value,
        mmr=mmr,
        size_type=size_type,
    )


@njit(cache=True)
def fill_order_records_nb(
    bar: int,  # time stamp
    order_records: RecordArray,
    settings_counter: int,
    order_records_id: Array1d,

    account_state: AccountState,
    order_result: OrderResult,
) -> tuple[RecordArray]:

    order_records['avg_entry'] = order_result.average_entry
    order_records['bar'] = bar
    order_records['equity'] = account_state.equity
    order_records['fees_paid'] = order_result.fees_paid
    order_records['settings_id'] = settings_counter
    order_records['order_id'] = order_records_id[0]
    order_records['order_type'] = order_result.order_type
    order_records['price'] = order_result.price
    order_records['real_pnl'] = round(order_result.realized_pnl, 4)
    order_records['size_value'] = order_result.size_value
    order_records['sl_prices'] = order_result.sl_prices
    order_records['tp_prices'] = order_result.tp_prices
    order_records['tsl_prices'] = order_result.tsl_prices

    order_records_id[0] += 1


@njit(cache=True)
def fill_strat_records_nb(
    indicator_settings_counter: int,
    order_settings_counter: int,

    strat_records: RecordArray,
    strat_records_filled: Array1d,

    equity: float,
    pnl: float,
) -> tuple[RecordArray]:

    strat_records['equity'] = equity
    strat_records['ind_set'] = indicator_settings_counter
    strat_records['or_set'] = order_settings_counter
    strat_records['real_pnl'] = round(pnl, 4)

    strat_records_filled[0] += 1


@njit(cache=True)
def to_1d_array_nb(
    var: PossibleArray
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
    var: PossibleArray,
    expand_axis: int = 1
) -> Array2d:
    if var.ndim == 0:
        return np.expand_dims(np.expand_dims(var, axis=0), axis=0)
    if var.ndim == 1:
        return np.expand_dims(var, axis=expand_axis)
    if var.ndim == 2:
        return var
    raise ValueError("to 2d array problem")
