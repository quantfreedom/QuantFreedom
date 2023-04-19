import numpy as np

from numba import njit
from quantfreedom._typing import PossibleArray, Array1d, RecordArray
from quantfreedom.nb.execute_funcs import process_order_nb, check_sl_tp_nb
from quantfreedom.nb.helper_funcs import (
    static_var_checker_nb,
    create_1d_arrays_nb,
    check_1d_arrays_nb,
    fill_strategy_result_records_nb,
    fill_settings_result_records_nb,
    get_to_the_upside_nb,
)
from quantfreedom.enums.enums import (
    or_dt,
    strat_df_array_dt,
    strat_records_dt,
    settings_array_dt,
    AccountState,
    EntryOrder,
    OrderResult,
    StopsOrder,
    StaticVariables,
    Arrays1dTuple,
    PriceTuple,
)


@njit(cache=True)
def sim_test_thing_nb(
    entries,
    price_data,
    static_variables_tuple: StaticVariables,
    broadcast_arrays: Arrays1dTuple,
) -> tuple[Array1d, RecordArray]:
    total_bars = entries.shape[0]
    order_records = np.empty(total_bars * 2, dtype=or_dt)
    order_records_id = np.array([0])

    prices_start = 0
    for settings_counter in range(entries.shape[1]):
        open_prices = price_data[:, prices_start]
        high_prices = price_data[:, prices_start + 1]
        low_prices = price_data[:, prices_start + 2]
        close_prices = price_data[:, prices_start + 3]
        prices_start += 4

        curr_entries = entries[:, settings_counter]
    # order settings loops
    entry_order = EntryOrder(
        leverage=broadcast_arrays.leverage[settings_counter],
        max_equity_risk_pct=broadcast_arrays.max_equity_risk_pct[settings_counter],
        max_equity_risk_value=broadcast_arrays.max_equity_risk_value[settings_counter],
        order_type=static_variables_tuple.order_type,
        risk_rewards=broadcast_arrays.risk_rewards[settings_counter],
        size_pct=broadcast_arrays.size_pct[settings_counter],
        size_value=broadcast_arrays.size_value[settings_counter],
        sl_based_on_add_pct=broadcast_arrays.sl_based_on_add_pct[settings_counter],
        sl_based_on=broadcast_arrays.sl_based_on[settings_counter],
        sl_pcts=broadcast_arrays.sl_pcts[settings_counter],
        tp_pcts=broadcast_arrays.tp_pcts[settings_counter],
        tsl_pcts_init=broadcast_arrays.tsl_pcts_init[settings_counter],
    )
    stops_order = StopsOrder(
        sl_to_be=static_variables_tuple.sl_to_be,
        sl_to_be_based_on=broadcast_arrays.sl_to_be_based_on[settings_counter],
        sl_to_be_then_trail=static_variables_tuple.sl_to_be_then_trail,
        sl_to_be_trail_by_when_pct_from_avg_entry=broadcast_arrays.sl_to_be_trail_by_when_pct_from_avg_entry[
            settings_counter
        ],
        sl_to_be_when_pct_from_avg_entry=broadcast_arrays.sl_to_be_when_pct_from_avg_entry[
            settings_counter
        ],
        sl_to_be_zero_or_entry=broadcast_arrays.sl_to_be_zero_or_entry[
            settings_counter
        ],
        tsl_based_on=broadcast_arrays.tsl_based_on[settings_counter],
        tsl_trail_by_pct=broadcast_arrays.tsl_trail_by_pct[settings_counter],
        tsl_true_or_false=static_variables_tuple.tsl_true_or_false,
        tsl_when_pct_from_avg_entry=broadcast_arrays.tsl_when_pct_from_avg_entry[
            settings_counter
        ],
    )
    # Account State Reset
    account_state = AccountState(
        available_balance=static_variables_tuple.equity,
        cash_borrowed=0.0,
        cash_used=0.0,
        equity=static_variables_tuple.equity,
    )

    # Order Result Reset
    order_result = OrderResult(
        average_entry=0.0,
        fees_paid=0.0,
        leverage=0.0,
        liq_price=np.nan,
        moved_sl_to_be=False,
        order_status=0,
        order_status_info=0,
        order_type=entry_order.order_type,
        pct_chg_trade=0.0,
        position=0.0,
        price=0.0,
        realized_pnl=0.0,
        size_value=0.0,
        sl_pcts=0.0,
        sl_prices=0.0,
        tp_pcts=0.0,
        tp_prices=0.0,
        tsl_pcts_init=0.0,
        tsl_prices=0.0,
    )

    # entries loop
    for bar in range(total_bars):
        if account_state.available_balance < 5:
            break

        if curr_entries[bar]:
            # Process Order nb
            prices = PriceTuple(
                open=open_prices[bar],
                high=high_prices[bar],
                low=low_prices[bar],
                close=close_prices[bar],
            )
            account_state, order_result = process_order_nb(
                account_state=account_state,
                bar=bar,
                entries_col=settings_counter,
                entry_order=entry_order,
                order_records_id=order_records_id,
                order_records=order_records[order_records_id[0]],
                order_result=order_result,
                order_type=entry_order.order_type,
                prices=prices,
                order_settings_counter=settings_counter,
                static_variables_tuple=static_variables_tuple,
                symbol_counter=settings_counter,
            )
        if order_result.position > 0:
            # Check Stops
            order_result = check_sl_tp_nb(
                open_price=open_prices[bar],
                high_price=high_prices[bar],
                low_price=low_prices[bar],
                close_price=close_prices[bar],
                fee_pct=static_variables_tuple.fee_pct,
                entry_type=entry_order.order_type,
                order_result=order_result,
                stops_order=stops_order,
                account_state=account_state,
                order_records=order_records[order_records_id[0]],
                order_records_id=order_records_id,
                bar=bar,
                settings_counter=settings_counter,
            )
            # process stops
            if not np.isnan(order_result.size_value):
                account_state, order_result = process_order_nb(
                    entry_order=entry_order,
                    order_type=order_result.order_type,
                    prices=prices,
                    account_state=account_state,
                    order_result=order_result,
                    static_variables_tuple=static_variables_tuple,
                    bar=bar,
                    entries_col=settings_counter,
                    symbol_counter=settings_counter,
                    order_settings_counter=settings_counter,
                    order_records=order_records[order_records_id[0]],
                    order_records_id=order_records_id,
                )

    return order_records[: order_records_id[-1]]
