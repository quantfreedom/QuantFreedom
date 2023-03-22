import numpy as np
from numba import njit

from quantfreedom._typing import (
    RecordArray,
    Array1d,
    )
from quantfreedom.backtester.enums import (
    AccountState,
    OrderResult,
    )


@njit(cache=True)
def fill_order_records_nb(
    bar: int,  # time stamp
    order_records: RecordArray,
    settings_counter: int,
    order_records_id: Array1d,

    account_state: AccountState,
    order_result: OrderResult,
)-> tuple[RecordArray]:

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
    
    order_records_id[0] +=1

@njit(cache=True)
def fill_strat_records_nb(
    indicator_settings_counter: int,
    order_settings_counter: int,
    
    strat_records: RecordArray,
    strat_records_filled: Array1d,

    equity: float,
    pnl: float,
)-> tuple[RecordArray]:

    strat_records['equity'] = equity
    strat_records['ind_set'] = indicator_settings_counter
    strat_records['or_set'] = order_settings_counter
    strat_records['real_pnl'] = round(pnl, 4)
    
    strat_records_filled[0] += 1



