"""
Testing the tester
"""

import numpy as np
from numba import njit

from quantfreedom._typing import *
from quantfreedom.testing_stuff.base_testing import *
from quantfreedom.testing_stuff.buy_testing import *
from quantfreedom.testing_stuff.enums_testing import *
from quantfreedom.testing_stuff.helper_funcs_testing import *
from quantfreedom.testing_stuff.simulate_testing import *


@njit(cache=True)
def check_sl_tp_nb_testing(
    account_state: AccountState,
    bar: int,
    order_result: OrderResult,
    order_settings_counter: int,
    order_settings_tuple: OrderSettings,
    prices_tuple: PriceTuple,
    static_variables_tuple: StaticVariables,
    order_records_id: Optional[Array1d] = None,
    order_records: Optional[RecordArray] = None,
):
    # Setting Vars
    moved_sl_to_be_new = order_result.moved_sl_to_be
    order_type_new = static_variables_tuple.order_type
    price_new = np.nan
    size_value_new = np.nan
    sl_price_new = order_result.sl_price

    # checking if we are in a long
    if static_variables_tuple.order_type == OrderType.LongEntry:
        # Regular Stop Loss
        if prices_tuple.low <= sl_price_new:
            price_new = sl_price_new
            order_type_new = (
                OrderType.LongSL
                if np.isnan(order_settings_tuple.trail_sl_by_pct)
                else OrderType.LongTSL
            )
        # Liquidation
        elif prices_tuple.low <= order_result.liq_price:
            price_new = order_result.liq_price
            order_type_new = OrderType.LongLiq
        # Take Profit
        elif prices_tuple.high >= order_result.tp_price:
            price_new = order_result.tp_price
            order_type_new = OrderType.LongTP

        # Stop Loss to break even
        if not moved_sl_to_be_new and not np.isnan(
            order_settings_tuple.sl_to_be_based_on
        ):
            if order_settings_tuple.sl_to_be_based_on == CandleBody.low:
                sl_be_based_on = prices_tuple.low
            elif order_settings_tuple.sl_to_be_based_on == CandleBody.close:
                sl_be_based_on = prices_tuple.close
            elif order_settings_tuple.sl_to_be_based_on == CandleBody.open:
                sl_be_based_on = prices_tuple.open
            elif order_settings_tuple.sl_to_be_based_on == CandleBody.high:
                sl_be_based_on = prices_tuple.high

            if (
                (sl_be_based_on - order_result.average_entry)
                / order_result.average_entry
                > order_settings_tuple.sl_to_be_when_pct_from_avg_entry
            ):
                if order_settings_tuple.sl_to_be_zero_or_entry == 0:
                    # this formula only works with a 1 because it represents a size val of 1
                    # if i were to use any other value for size i would have to use the solving for tp code
                    sl_price_new = (
                        static_variables_tuple.fee_pct * order_result.average_entry
                        + order_result.average_entry
                    ) / (1 - static_variables_tuple.fee_pct)
                else:
                    sl_price_new = order_result.average_entry
                moved_sl_to_be_new = True
                order_type_new = OrderType.MovedSLtoBE
                record_sl_move = True
            price_new = np.nan
            size_value_new = np.nan

        # Trailing Stop Loss
        if not np.isnan(order_settings_tuple.trail_sl_based_on):
            if order_settings_tuple.trail_sl_based_on == CandleBody.low:
                trail_based_on = prices_tuple.low
            elif order_settings_tuple.trail_sl_based_on == CandleBody.high:
                trail_based_on = prices_tuple.high
            elif order_settings_tuple.trail_sl_based_on == CandleBody.open:
                trail_based_on = prices_tuple.open
            elif order_settings_tuple.trail_sl_based_on == CandleBody.close:
                trail_based_on = prices_tuple.close

            # not going to adjust every candle
            x = (
                (trail_based_on - order_result.average_entry)
                / order_result.average_entry
                > order_settings_tuple.trail_sl_when_pct_from_avg_entry
            )
            if x:
                temp_sl_price = (
                    trail_based_on
                    - trail_based_on * order_settings_tuple.trail_sl_by_pct
                )
                if temp_sl_price > sl_price_new:
                    sl_price_new = temp_sl_price
                    moved_tsl = True
                    order_type_new = OrderType.MovedTSL
            price_new = np.nan
            size_value_new = np.nan
        else:
            price_new = np.nan
            size_value_new = np.nan

    # # checking if we are in a short
    # elif order_type_new == OrderType.ShortEntry:
    #     # Regular Stop Loss
    #     if prices_tuple.high >= sl_price_new:
    #         price_new = sl_price_new
    #         order_type_new = (
    #             OrderType.ShortSL
    #             if np.isnan(order_settings_tuple.trail_sl_by_pct)
    #             else OrderType.ShortTSL
    #         )
    #     # Liquidation
    #     elif prices_tuple.high >= order_result.liq_price:
    #         price_new = order_result.liq_price
    #         order_type_new = OrderType.ShortLiq
    #     # Take Profit
    #     elif prices_tuple.low <= order_result.tp_price:
    #         price_new = order_result.tp_price
    #         order_type_new = OrderType.ShortTP

    #     # Stop Loss to break even
    #     elif not moved_sl_to_be_new and order_settings_tuple.sl_to_be:
    #         if order_settings_tuple.sl_to_be_based_on == CandleBody.low:
    #             sl_be_based_on = prices_tuple.low
    #         elif order_settings_tuple.sl_to_be_based_on == CandleBody.close:
    #             sl_be_based_on = prices_tuple.close
    #         elif order_settings_tuple.sl_to_be_based_on == CandleBody.open:
    #             sl_be_based_on = prices_tuple.open
    #         elif order_settings_tuple.sl_to_be_based_on == CandleBody.high:
    #             sl_be_based_on = prices_tuple.high

    #         if (
    #             (order_result.average_entry - sl_be_based_on)
    #             / order_result.average_entry
    #             > order_settings_tuple.sl_to_be_when_pct_from_avg_entry
    #         ):
    #             if order_settings_tuple.sl_to_be_zero_or_entry == 0:
    #                 # this formula only works with a 1 because it represents a size val of 1
    #                 # if i were to use any other value for size i would have to use the solving for tp code
    #                 sl_price_new = (
    #                     order_result.average_entry
    #                     - static_variables_tuple.fee_pct * order_result.average_entry
    #                 ) / (1 + static_variables_tuple.fee_pct)
    #             else:
    #                 sl_price_new = order_result.average_entry
    #             moved_sl_to_be_new = True
    #             order_type_new = OrderType.MovedSLtoBE
    #             record_sl_move = True
    #         price_new = np.nan
    #         size_value_new = np.nan

    #     # Trailing Stop Loss
    #     elif order_settings_tuple.tsl_true_or_false:
    #         if order_settings_tuple.tsl_based_on == CandleBody.high:
    #             trail_based_on = prices_tuple.high
    #         elif order_settings_tuple.tsl_based_on == CandleBody.close:
    #             trail_based_on = prices_tuple.close
    #         elif order_settings_tuple.tsl_based_on == CandleBody.open:
    #             trail_based_on = prices_tuple.open
    #         elif order_settings_tuple.tsl_based_on == CandleBody.low:
    #             trail_based_on = prices_tuple.low

    #         # not going to adjust every candle
    #         x = (
    #             (order_result.average_entry - trail_based_on)
    #             / order_result.average_entry
    #             > order_settings_tuple.tsl_when_pct_from_avg_entry
    #         )
    #         if x:
    #             temp_sl_price = (
    #                 trail_based_on
    #                 + trail_based_on * order_settings_tuple.tsl_trail_by_pct
    #             )
    #             if temp_sl_price < sl_price_new:
    #                 sl_price_new = temp_sl_price
    #                 moved_tsl = True
    #                 order_type_new = OrderType.MovedTSL
    #         price_new = np.nan
    #         size_value_new = np.nan
    #     else:
    #         price_new = np.nan
    #         size_value_new = np.nan

    order_result_new = OrderResult(
        average_entry=order_result.average_entry,
        fees_paid=order_result.fees_paid,
        leverage=order_result.leverage,
        liq_price=order_result.liq_price,
        moved_sl_to_be=moved_sl_to_be_new,
        order_status=order_result.order_status,
        order_status_info=order_result.order_status_info,
        order_type=order_type_new,
        pct_chg_trade=order_result.pct_chg_trade,
        position=order_result.position,
        price=price_new,
        realized_pnl=order_result.realized_pnl,
        size_value=size_value_new,
        sl_pct=order_result.sl_pct,
        sl_price=sl_price_new,
        tp_pct=order_result.tp_pct,
        tp_price=order_result.tp_price,
    )

    if order_records is not None and (record_sl_move or moved_tsl):
        fill_order_records_nb_testing(
            bar=bar,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_records_id=order_records_id,
            account_state=account_state,
            order_result=order_result_new,
        )

    return order_result_new


@njit(cache=True)
def process_order_nb_testing(
    account_state: AccountState,
    bar: int,
    entries_col: int,
    order_result: OrderResult,
    order_settings_counter: int,
    order_settings: OrderSettings,
    prices: PriceTuple,
    static_variables_tuple: StaticVariables,
    symbol_counter: int,
    order_records: Optional[RecordArray] = None,
    order_records_id: Optional[Array1d] = None,
    strat_records: Optional[RecordArray] = None,
    strat_records_filled: Optional[Array1d] = None,
):
    fill_strat = False
    if static_variables_tuple.order_type == OrderType.LongEntry:
        account_state_new, order_result_new = long_increase_nb_testing(
            prices=prices,
            order_settings=order_settings,
            order_result=order_result,
            account_state=account_state,
            static_variables_tuple=static_variables_tuple,
        )
    # elif order_type == OrderType.ShortEntry:
    #     account_state_new, order_result_new = short_increase_nb(
    #         price=prices,
    #         entry_order=entry_order,
    #         order_result=order_result,
    #         account_state=account_state,
    #         static_variables_tuple=static_variables_tuple,
    #     )
    elif OrderType.LongLiq <= static_variables_tuple.order_type <= OrderType.LongTSL:
        account_state_new, order_result_new = long_decrease_nb_testing(
            order_result=order_result,
            account_state=account_state,
            fee_pct=static_variables_tuple.fee_pct,
        )
        fill_strat = True
    # elif OrderType.ShortLiq <= order_type <= OrderType.ShortTSL:
    #     account_state_new, order_result_new = short_decrease_nb(
    #         order_result=order_result,
    #         account_state=account_state,
    #         fee_pct=static_variables_tuple.fee_pct,
    #     )
    #     fill_strat = True

    if order_result_new.order_status == OrderStatus.Filled:
        if fill_strat and strat_records is not None:
            fill_strat_records_nb_testing(
                entries_col=entries_col,
                order_settings_counter=order_settings_counter,
                symbol_counter=symbol_counter,
                strat_records=strat_records,
                strat_records_filled=strat_records_filled,
                equity=account_state_new.equity,
                pnl=order_result_new.realized_pnl,
            )

        elif order_records is not None:
            fill_order_records_nb_testing(
                bar=bar,
                order_records=order_records,
                order_settings_counter=order_settings_counter,
                order_records_id=order_records_id,
                account_state=account_state_new,
                order_result=order_result_new,
            )

    return account_state_new, order_result_new
