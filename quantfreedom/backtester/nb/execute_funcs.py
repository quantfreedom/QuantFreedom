"""
Testing the tester
"""

import numpy as np
from numba import njit

from quantfreedom.backtester.nb.helper_funcs import fill_order_records_nb

from quantfreedom.backtester.nb.buy_funcs import long_increase_nb, long_decrease_nb
from quantfreedom._typing import (
    RecordArray,
    Array1d,
)
from quantfreedom.backtester.enums.enums import (
    OrderType,
    SL_BE_or_Trail_BasedOn,
    OrderStatus,

    AccountState,
    EntryOrder,
    OrderResult,
    StopsOrder,
    StaticVariables,
)


@ njit(cache=True)
def check_sl_tp_nb(
    high_price: float,
    low_price: float,
    open_price: float,
    close_price: float,

    fee_pct: float,

    order_result: OrderResult,
    stops_order: StopsOrder,
):
    """
    This checks if your stop or take profit was hit.

    Args:
        high_price: The high_price of the candle
        low_price: The low_price of the candle
        order_result: See [Order Result][backtester.enums.enums.ResultEverything].

    !!! note
        Right now it only fully closes the position. But that will be changing soon once multiple stops is implimented.

    First it checks the order type and then it checks if the stop losses were hit and then checks to see if take profit was hit last.
    It defaults to checking tp last so it has a negative bias.
    """
    moved_sl_to_be_new = order_result.moved_sl_to_be
    moved_tsl_new = order_result.moved_tsl
    order_type_new = order_result.order_type
    price_new = order_result.price
    size_value_new = np.inf
    sl_prices_new = order_result.sl_prices
    tsl_prices_new = order_result.tsl_prices

    average_entry = order_result.average_entry

    # checking if we are in a long
    if order_type_new == OrderType.LongEntry:
        # Regular Stop Loss
        if low_price <= sl_prices_new:
            price_new = sl_prices_new
            order_type_new = OrderType.LongSL
        # Trailing Stop Loss
        elif low_price <= tsl_prices_new:
            price_new = tsl_prices_new
            order_type_new = OrderType.LongTSL
        # Liquidation
        elif low_price <= order_result.liq_price:
            price_new = order_result.liq_price
            order_type_new = OrderType.LongLiq
        # Take Profit
        elif high_price >= order_result.tp_prices:
            price_new = order_result.tp_prices
            order_type_new = OrderType.LongTP

        # Stop Loss to break even
        elif not moved_sl_to_be_new and stops_order.sl_to_be:
            if stops_order.sl_to_be_based_on == SL_BE_or_Trail_BasedOn.low_price:
                be_price = low_price
            elif stops_order.sl_to_be_based_on == SL_BE_or_Trail_BasedOn.close_price:
                be_price = close_price
            elif stops_order.sl_to_be_based_on == SL_BE_or_Trail_BasedOn.open_price:
                be_price = open_price
            elif stops_order.sl_to_be_based_on == SL_BE_or_Trail_BasedOn.high_price:
                be_price = high_price

            if (be_price - average_entry) / average_entry > stops_order.sl_to_be_when_pct_from_avg_entry:
                if stops_order.sl_to_be_zero_or_entry == 0:
                    sl_prices_new = (fee_pct * average_entry +
                                     average_entry) / (1 - fee_pct)
                else:
                    sl_prices_new = average_entry
                moved_sl_to_be_new = True
            order_type_new = OrderType.MovedSLtoBE
            price_new = np.nan
            size_value_new = np.nan

        # Trailing Stop Loss
        elif stops_order.tsl_true_or_false:
            if stops_order.tsl_based_on == SL_BE_or_Trail_BasedOn.low_price:
                trailed_sl_price = low_price
            elif stops_order.tsl_based_on == SL_BE_or_Trail_BasedOn.high_price:
                trailed_sl_price = high_price
            elif stops_order.tsl_based_on == SL_BE_or_Trail_BasedOn.open_price:
                trailed_sl_price = open_price
            elif stops_order.tsl_based_on == SL_BE_or_Trail_BasedOn.close_price:
                trailed_sl_price = close_price

            # not going to adjust every candle
            if (trailed_sl_price - average_entry) / average_entry > stops_order.tsl_when_pct_from_avg_entry:
                temp_tsl_price = trailed_sl_price - \
                    trailed_sl_price * stops_order.tsl_trail_by_pct
                if temp_tsl_price > trailed_sl_price:
                    tsl_prices_new = temp_tsl_price
                    moved_tsl_new = True
                    order_type_new = OrderType.MovedTSL
            price_new = np.nan
            size_value_new = np.nan
        else:
            price_new = np.nan
            size_value_new = np.nan

    return OrderResult(
        average_entry=order_result.average_entry,
        fees_paid=order_result.fees_paid,
        leverage=order_result.leverage,
        liq_price=order_result.liq_price,
        moved_sl_to_be=moved_sl_to_be_new,
        moved_tsl=moved_tsl_new,
        order_status=order_result.order_status,
        order_status_info=order_result.order_status_info,
        order_type=order_type_new,
        pct_chg_trade=order_result.pct_chg_trade,
        position=order_result.position,
        price=price_new,
        realized_pnl=order_result.realized_pnl,
        size_value=size_value_new,
        sl_pcts=order_result.sl_pcts,
        sl_prices=sl_prices_new,
        tp_pcts=order_result.tp_pcts,
        tp_prices=order_result.tp_prices,
        tsl_pcts=order_result.tsl_pcts,
        tsl_prices=tsl_prices_new,
    )


@ njit(cache=True)
def process_order_nb(
    price: float,
    bar: int,
    order_type: int,

    indicator_settings_counter: int,
    order_settings_counter: int,
    order_records: RecordArray,
    order_count_id: Array1d,
    or_filled_temp: Array1d,

    account_state: AccountState,
    entry_order: EntryOrder,
    order_result: OrderResult,
    static_variables: StaticVariables,

):

    if order_type == OrderType.LongEntry:
        account_state_new, order_result_new = long_increase_nb(
            price=price,
            entry_order=entry_order,
            order_result=order_result,
            account_state=account_state,
            static_variables=static_variables,
        )
    elif OrderType.LongLiq <= order_type <= OrderType.LongTSL:
        account_state_new, order_result_new = long_decrease_nb(
            order_result=order_result,
            account_state=account_state,
            fee_pct=static_variables.fee_pct,
        )

    if order_result_new.order_status == OrderStatus.Filled:
        fill_order_records_nb(
            bar=bar,

            indicator_settings_counter=indicator_settings_counter,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_count_id=order_count_id,
            or_filled_temp=or_filled_temp,

            account_state=account_state_new,
            order_result=order_result_new,
        )

    return account_state_new, order_result_new


@ njit(cache=True)
def process_stops_nb(
    price: float,
    bar: int,

    indicator_settings_counter: int,
    order_settings_counter: int,
    order_records: RecordArray,
    order_count_id: Array1d,
    or_filled_temp: Array1d,

    account_state: AccountState,
    order_result: OrderResult,
    static_variables: StaticVariables,

):

    if OrderType.LongLiq <= order_result.order_type <= OrderType.LongTSL:

        account_state_new, order_result_new = long_decrease_nb(
            order_result=order_result,
            account_state=account_state,
            fee_pct=static_variables.fee_pct,
        )

    if order_result_new.order_status == OrderStatus.Filled:
        fill_order_records_nb(
            bar=bar,

            indicator_settings_counter=indicator_settings_counter,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_count_id=order_count_id,
            or_filled_temp=or_filled_temp,

            account_state=account_state_new,
            order_result=order_result_new,
        )

    return account_state_new, order_result_new
