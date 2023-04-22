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
def backtest_df_only_nb(
    num_of_symbols: int,
    total_indicator_settings: int,
    total_order_settings: int,
    total_bars: int,
    # entry info
    og_equity: float,
    entries: PossibleArray,
    price_data: PossibleArray,
    # filters
    gains_pct_filter: float,
    total_trade_filter: int,
    # Tuples
    static_variables_tuple: StaticVariables,
    cart_array_tuple: Arrays1dTuple,
) -> Array1d[Array1d, Array1d]:
    # Creating strat records
    array_size = int(
        num_of_symbols
        * total_indicator_settings
        * total_order_settings
        / static_variables_tuple.divide_records_array_size_by
    )

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )
    settings_result_records = np.empty(
        array_size,
        dtype=settings_array_dt,
    )
    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 3), dtype=strat_records_dt)
    strat_records_filled = np.array([0])

    prices_start = 0
    entries_per_symbol = int(entries.shape[1] / num_of_symbols)
    entries_start = 0
    entries_end = entries_per_symbol
    entries_col = 0

    for symbol_counter in range(num_of_symbols):
        open_prices = price_data[:, prices_start]
        high_prices = price_data[:, prices_start + 1]
        low_prices = price_data[:, prices_start + 2]
        close_prices = price_data[:, prices_start + 3]

        prices_start +=4
        
        symbol_entries = entries[:, entries_start:entries_end]
        entries_start = entries_end
        entries_end += entries_per_symbol

        # ind set loop
        for indicator_settings_counter in range(entries_per_symbol):
            current_indicator_entries = symbol_entries[:, indicator_settings_counter]

            for order_settings_counter in range(total_order_settings):
                entry_order = EntryOrder(
                    leverage=cart_array_tuple.leverage[order_settings_counter],
                    max_equity_risk_pct=cart_array_tuple.max_equity_risk_pct[
                        order_settings_counter
                    ],
                    max_equity_risk_value=cart_array_tuple.max_equity_risk_value[
                        order_settings_counter
                    ],
                    order_type=static_variables_tuple.order_type,
                    risk_rewards=cart_array_tuple.risk_rewards[order_settings_counter],
                    size_pct=cart_array_tuple.size_pct[order_settings_counter],
                    size_value=cart_array_tuple.size_value[order_settings_counter],
                    sl_based_on_add_pct=cart_array_tuple.sl_based_on_add_pct[
                        order_settings_counter
                    ],
                    sl_based_on=cart_array_tuple.sl_based_on[order_settings_counter],
                    sl_pcts=cart_array_tuple.sl_pcts[order_settings_counter],
                    tp_pcts=cart_array_tuple.tp_pcts[order_settings_counter],
                    tsl_pcts_init=cart_array_tuple.tsl_pcts_init[
                        order_settings_counter
                    ],
                )
                stops_order = StopsOrder(
                    sl_to_be=static_variables_tuple.sl_to_be,
                    sl_to_be_based_on=cart_array_tuple.sl_to_be_based_on[
                        order_settings_counter
                    ],
                    sl_to_be_then_trail=static_variables_tuple.sl_to_be_then_trail,
                    sl_to_be_trail_by_when_pct_from_avg_entry=cart_array_tuple.sl_to_be_trail_by_when_pct_from_avg_entry[
                        order_settings_counter
                    ],
                    sl_to_be_when_pct_from_avg_entry=cart_array_tuple.sl_to_be_when_pct_from_avg_entry[
                        order_settings_counter
                    ],
                    sl_to_be_zero_or_entry=cart_array_tuple.sl_to_be_zero_or_entry[
                        order_settings_counter
                    ],
                    tsl_based_on=cart_array_tuple.tsl_based_on[order_settings_counter],
                    tsl_trail_by_pct=cart_array_tuple.tsl_trail_by_pct[
                        order_settings_counter
                    ],
                    tsl_true_or_false=static_variables_tuple.tsl_true_or_false,
                    tsl_when_pct_from_avg_entry=cart_array_tuple.tsl_when_pct_from_avg_entry[
                        order_settings_counter
                    ],
                )
                # Account State Reset
                account_state = AccountState(
                    available_balance=og_equity,
                    cash_borrowed=0.0,
                    cash_used=0.0,
                    equity=og_equity,
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
                strat_records_filled[0] = 0

                # entries loop
                for bar in range(total_bars):
                    prices = PriceTuple(
                        open=open_prices[bar],
                        high=high_prices[bar],
                        low=low_prices[bar],
                        close=close_prices[bar],
                    )
                    if account_state.available_balance < 5:
                        break

                    if current_indicator_entries[bar]:
                        # Process Order nb
                        account_state, order_result = process_order_nb(
                            account_state=account_state,
                            bar=bar,
                            entries_col=entries_col,
                            entry_order=entry_order,
                            order_result=order_result,
                            order_settings_counter=order_settings_counter,
                            order_type=entry_order.order_type,
                            prices=prices,
                            static_variables_tuple=static_variables_tuple,
                            strat_records_filled=strat_records_filled,
                            strat_records=strat_records[strat_records_filled[0]],
                            symbol_counter=symbol_counter,
                        )
                    if order_result.position > 0:
                        # Check Stops
                        order_result = check_sl_tp_nb(
                            account_state=account_state,
                            bar=bar,
                            close_price=close_prices[bar],
                            entry_type=entry_order.order_type,
                            fee_pct=static_variables_tuple.fee_pct,
                            high_price=high_prices[bar],
                            low_price=low_prices[bar],
                            open_price=open_prices[bar],
                            order_result=order_result,
                            order_settings_counter=order_settings_counter,
                            stops_order=stops_order,
                        )
                        # process stops
                        if not np.isnan(order_result.size_value):
                            account_state, order_result = process_order_nb(
                                account_state=account_state,
                                bar=bar,
                                entries_col=entries_col,
                                entry_order=entry_order,
                                order_result=order_result,
                                order_settings_counter=order_settings_counter,
                                order_type=order_result.order_type,
                                prices=prices,
                                static_variables_tuple=static_variables_tuple,
                                strat_records_filled=strat_records_filled,
                                strat_records=strat_records[strat_records_filled[0]],
                                symbol_counter=symbol_counter,
                            )

                # Checking if gains
                gains_pct = ((account_state.equity - og_equity) / og_equity) * 100
                if gains_pct > gains_pct_filter:
                    temp_strat_records = strat_records[0 : strat_records_filled[0]]
                    wins_and_losses_array = temp_strat_records["real_pnl"][
                        ~np.isnan(temp_strat_records["real_pnl"])
                    ]

                    # Checking total trade filter
                    if wins_and_losses_array.size > total_trade_filter:
                        wins_and_losses_array_no_be = wins_and_losses_array[
                            wins_and_losses_array != 0
                        ]
                        to_the_upside = get_to_the_upside_nb(
                            gains_pct=gains_pct,
                            wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                        )

                        # Checking to the upside filter
                        if to_the_upside > static_variables_tuple.upside_filter:
                            fill_strategy_result_records_nb(
                                gains_pct=gains_pct,
                                strategy_result_records=strategy_result_records[
                                    result_records_filled
                                ],
                                temp_strat_records=temp_strat_records,
                                to_the_upside=to_the_upside,
                                total_trades=wins_and_losses_array.size,
                                wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                            )

                            fill_settings_result_records_nb(
                                entries_col=entries_col,
                                entry_order=entry_order,
                                settings_result_records=settings_result_records[
                                    result_records_filled
                                ],
                                stops_order=stops_order,
                                symbol_counter=symbol_counter,
                            )
                            result_records_filled += 1
            entries_col += 1
    return (
        strategy_result_records[:result_records_filled],
        settings_result_records[:result_records_filled],
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
                    order_settings_counter=settings_counter,
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