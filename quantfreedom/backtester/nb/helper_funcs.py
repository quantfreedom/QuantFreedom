import numpy as np
from numba import njit

from quantfreedom._typing import (
    RecordArray,
    PossibleArray,
    Array1d,
    Array2d
    )
from quantfreedom.backtester.enums import (
    AccountState,
    OrderResult,
    )


@njit(cache=True)
def fill_order_records_nb(
    bar: int,  # time stamp
    indicator_settings_counter: int,
    order_records: RecordArray,
    order_settings_counter: int,
    order_count_id: Array1d,
    or_filled_temp: Array1d,

    account_state: AccountState,
    order_result: OrderResult,
):

    order_records['avg_entry'] = order_result.average_entry
    order_records['bar'] = bar
    order_records['equity'] = account_state.equity
    order_records['fees_paid'] = order_result.fees_paid
    order_records['ind_set'] = indicator_settings_counter
    order_records['or_set'] = order_settings_counter
    order_records['order_id'] = order_count_id
    order_records['order_type'] = order_result.order_type
    order_records['price'] = order_result.price
    order_records['real_pnl'] = round(order_result.realized_pnl, 4)
    order_records['size_value'] = order_result.size_value
    order_records['sl_prices'] = order_result.sl_prices
    order_records['tp_prices'] = order_result.tp_prices
    order_records['tsl_prices'] = order_result.tsl_prices
    
    order_count_id[0] +=1
    or_filled_temp[0] += 1


