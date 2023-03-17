"""
Testing the tester
"""

import numpy as np
from numba import njit

from quantfreedom.backtester.nb.buy_funcs import long_increase_nb
from quantfreedom.backtester.nb.helper_funcs import fill_order_records_nb
from quantfreedom._typing import (
    RecordArray,
    Array1d,
)
from quantfreedom.backtester.enums.enums import (
    OrderType,
    SL_BE_or_Trail_BasedOn,
    SizeType,
    OrderStatus,

    AccountState,
    EntryOrder,
    OrderResult,
    RejectedOrderError,
    StaticVariables,
)


@ njit(cache=True)
def check_sl_tp_nb(
    average_entry: float,
    high_price: float,
    low_price: float,
    open_price: float,
    close_price: float,
    fee_pct: float,
    order_type: int,
    sl_prices: float,
    tsl_prices: float,
    liq_price: float,
    tp_prices: float,

    moved_sl_to_be: bool,
    sl_to_be: bool,
    sl_to_be_based_on: float,
    sl_to_be_when_pct_from_avg_entry: float,
    sl_to_be_zero_or_entry: float,

    moved_tsl: bool,
    tsl_true_or_false: bool,
    tsl_based_on: float,
    tsl_trail_by: float,
    tsl_when_pct_from_avg_entry: float,

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
    size_value = np.inf

    # checking if we are in a long
    if order_type == OrderType.LongEntry:
        # Regular Stop Loss
        if low_price <= sl_prices:
            price = sl_prices
            order_type = OrderType.LongSL
        # Trailing Stop Loss
        elif low_price <= tsl_prices:
            price = tsl_prices
            order_type = OrderType.LongTSL
        # Liquidation
        elif low_price <= liq_price:
            price = liq_price
            order_type = OrderType.LongLiq
        # Take Profit
        elif high_price >= tp_prices:
            price = tp_prices
            order_type = OrderType.LongTP

        # Stop Loss to break even
        elif not moved_sl_to_be and sl_to_be:
            if sl_to_be_based_on == SL_BE_or_Trail_BasedOn.low_price:
                sl_to_be_based_on = low_price
            elif sl_to_be_based_on == SL_BE_or_Trail_BasedOn.high_price:
                sl_to_be_based_on = high_price
            elif sl_to_be_based_on == SL_BE_or_Trail_BasedOn.open_price:
                sl_to_be_based_on = open_price
            elif sl_to_be_based_on == SL_BE_or_Trail_BasedOn.close_price:
                sl_to_be_based_on = close_price

            if (sl_to_be_based_on - average_entry) / average_entry > sl_to_be_when_pct_from_avg_entry:
                if sl_to_be_zero_or_entry == 0:
                    sl_prices = (
                        fee_pct * average_entry + average_entry
                    ) / (1 - fee_pct)
                else:
                    sl_prices = average_entry
                moved_sl_to_be = True
                record_log_sl_moved = True
            order_type = OrderType.MovedSLtoBE
            price = np.nan
            size_value = np.nan

        # Trailing Stop Loss
        elif tsl_true_or_false:
            if tsl_based_on == SL_BE_or_Trail_BasedOn.low_price:
                tsl_based_on = low_price
            elif tsl_based_on == SL_BE_or_Trail_BasedOn.high_price:
                tsl_based_on = high_price
            elif tsl_based_on == SL_BE_or_Trail_BasedOn.open_price:
                tsl_based_on = open_price
            elif tsl_based_on == SL_BE_or_Trail_BasedOn.close_price:
                tsl_based_on = close_price

            # not going to adjust every candle
            if (tsl_based_on - average_entry) / average_entry > tsl_when_pct_from_avg_entry:
                temp_tsl_price = tsl_based_on - tsl_based_on * tsl_trail_by
                if temp_tsl_price > tsl_prices:
                    tsl_prices = temp_tsl_price
                    moved_tsl = True
                    record_log_sl_moved = True
                    order_type = OrderType.MovedTSL
            price = np.nan
            size_value = np.nan
        else:
            price = np.nan
            size_value = np.nan

    # Checking if we are a short entry
    elif order_type == OrderType.ShortEntry:
        # Stop Loss
        if high_price >= sl_prices:
            price = sl_prices
            order_type = OrderType.ShortSL
        # Trailing Stop Loss
        elif high_price >= tsl_prices:
            price = tsl_prices
            order_type = OrderType.ShortTSL
        # Liquidation
        elif high_price >= liq_price:
            price = liq_price
            order_type = OrderType.ShortLiq
        # Take Profit
        elif low_price <= tp_prices:
            price = tp_prices
            order_type = OrderType.ShortTP
        else:
            order_type = OrderType.ShortEntry
            price = np.nan
            size_value = np.nan
    else:
        raise RejectedOrderError(
            "Check SL TP: Something is wrong checking sl tsl tp")

    return \
        moved_sl_to_be, \
        moved_tsl, \
        order_type, \
        price, \
        size_value, \
        sl_prices, \
        tsl_prices


@ njit(cache=True)
def process_order_nb(
    price: float,
    bar: int,

    indicator_settings_counter: int,
    order_settings_counter: int,
    order_records: RecordArray,
    order_count_id: Array1d,
    or_filled_end: Array1d,


    account_state: AccountState,
    entry_order: EntryOrder,
    order_result: OrderResult,
    static_variables: StaticVariables,

):

    if entry_order.order_type == OrderType.LongEntry:

        account_state_new, order_result_new = long_increase_nb(
            price=price,
            entry_order=entry_order,
            order_result=order_result,
            account_state=account_state,
            static_variables=static_variables,
        )

    if order_result.order_status == OrderStatus.Filled:
        fill_order_records_nb(
            bar=bar,
            price=price,

            indicator_settings_counter=indicator_settings_counter,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_count_id=order_count_id,
            or_filled_end=or_filled_end,


            account_state=account_state_new,
            order_result=order_result_new,
        )

    return account_state_new, order_result_new


@ njit(cache=True)
def process_stops_nb(
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    equity: float,
    fee_pct: float,
    liq_price: int,
    max_equity_risk_pct: float,
    order_type: int,
    position: float,
    price: float,
    risk_rewards: float,
    size_value: float,
    sl_pcts: float,
    sl_prices: float,
    tp_prices: float,
    tsl_prices: float,

    bar: int,
    indicator_settings_counter: int,
    order_settings_counter: int,

    order_count_id: int,
    or_filled_end: int,
    order_records: RecordArray,
):

    order_count_id_new = order_count_id
    order_records_filled_new = or_filled_end

    if OrderType.LongLiq <= order_type <= OrderType.LongTSL:
        available_balance_new, \
            cash_borrowed_new, \
            cash_used_new, \
            equity_new, \
            fees_paid, \
            liq_price, \
            order_status_info, \
            order_status, \
            position_new, \
            realized_pnl, \
            size_value, \
            = long_decrease_nb(
                available_balance=available_balance,
                average_entry=average_entry,
                cash_borrowed=cash_borrowed,
                cash_used=cash_used,
                equity=equity,
                fee_pct=fee_pct,
                liq_price=liq_price,
                position=position,
                price=price,
                size_value=size_value,
            )

    # Start the order filling process
    if order_status == OrderStatus.Filled:
        fill_order_records_nb(
            bar=bar,
            indicator_settings_counter=indicator_settings_counter,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_type=order_type,
            price=price,
            realized_pnl=realized_pnl,
            risk_rewards=risk_rewards,
            size_value=size_value,
            sl_pcts=sl_pcts,
        )
        order_count_id_new += 1
        order_records_filled_new += 1

    return available_balance_new, \
        cash_borrowed_new, \
        cash_used_new, \
        equity_new, \
        fees_paid, \
        liq_price, \
        order_count_id_new, \
        order_records_filled_new, \
        order_status_info, \
        order_status, \
        position_new, \
        realized_pnl
