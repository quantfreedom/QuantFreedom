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
    prices: PossibleArray,
    # filters
    gains_pct_filter: float,
    total_trade_filter: int,
    # Tuples
    static_variables_tuple: StaticVariables,
    cart_array_tuple: Arrays1dTuple,
) -> Array1d[Array1d, Array1d]:
    # Creating strat records
    strategy_result_records = np.empty(
        int(num_of_symbols * total_indicator_settings * total_order_settings / 3),
        dtype=strat_df_array_dt,
    )
    settings_result_records = np.empty(
        int(num_of_symbols * total_indicator_settings * total_order_settings / 3),
        dtype=settings_array_dt,
    )
    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 3), dtype=strat_records_dt)
    strat_records_filled = np.array([0])

    prices_start = 0
    prices_end = 4
    entries_per_symbol = int(entries.shape[1] / num_of_symbols)
    entries_start = 0
    entries_end = entries_per_symbol
    entries_col = 0

    for symbol_counter in range(num_of_symbols):
        open_prices = prices[:, prices_start:prices_end][:, 0]
        high_prices = prices[:, prices_start:prices_end][:, 1]
        low_prices = prices[:, prices_start:prices_end][:, 2]
        close_prices = prices[:, prices_start:prices_end][:, 3]

        prices_start = prices_end
        prices_end += 4

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
                    if account_state.available_balance < 5:
                        break

                    if current_indicator_entries[bar]:
                        # Process Order nb
                        account_state, order_result = process_order_nb(
                            price=open_prices[bar],
                            order_type=entry_order.order_type,
                            account_state=account_state,
                            entry_order=entry_order,
                            order_result=order_result,
                            static_variables_tuple=static_variables_tuple,
                            bar=bar,
                            entries_col=entries_col,
                            order_settings_counter=order_settings_counter,
                            symbol_counter=symbol_counter,
                            strat_records=strat_records[strat_records_filled[0]],
                            strat_records_filled=strat_records_filled,
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
                            bar=bar,
                            order_settings_counter=order_settings_counter,
                        )
                        # process stops
                        if not np.isnan(order_result.size_value):
                            account_state, order_result = process_order_nb(
                                entry_order=entry_order,
                                order_type=order_result.order_type,
                                price=open_prices[bar],
                                account_state=account_state,
                                order_result=order_result,
                                static_variables_tuple=static_variables_tuple,
                                bar=bar,
                                entries_col=entries_col,
                                order_settings_counter=order_settings_counter,
                                symbol_counter=symbol_counter,
                                strat_records=strat_records[strat_records_filled[0]],
                                strat_records_filled=strat_records_filled,
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
                        fill_strategy_result_records_nb(
                            gains_pct=gains_pct,
                            strategy_result_records=strategy_result_records[
                                result_records_filled
                            ],
                            temp_strat_records=temp_strat_records,
                            wins_and_losses_array=wins_and_losses_array,
                        )

                        fill_settings_result_records_nb(
                            entry_order=entry_order,
                            symbol_counter=symbol_counter,
                            entries_col=entries_col,
                            settings_result_records=settings_result_records[
                                result_records_filled
                            ],
                            stops_order=stops_order,
                        )
                        result_records_filled += 1
            entries_col += 1
    return (
        strategy_result_records[:result_records_filled],
        settings_result_records[:result_records_filled],
    )


@njit(cache=True)
def simulate_up_to_6_nb(
    # entry info
    entries: PossibleArray,
    prices: PossibleArray,
    # required account info
    equity: float,
    fee_pct: float,
    mmr: float,
    # required order
    lev_mode: int,
    order_type: int,
    size_type: int,
    # Order Params
    leverage: PossibleArray = np.nan,
    max_equity_risk_pct: PossibleArray = np.nan,
    max_equity_risk_value: PossibleArray = np.nan,
    max_lev: float = 100.0,
    max_order_size_pct: float = 100.0,
    min_order_size_pct: float = 0.01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.0,
    size_pct: PossibleArray = np.nan,
    size_value: PossibleArray = np.nan,
    # Stop Losses
    sl_pcts: PossibleArray = np.nan,
    sl_to_be: bool = False,
    sl_to_be_based_on: PossibleArray = np.nan,
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan,
    sl_to_be_zero_or_entry: PossibleArray = np.nan,
    sl_to_be_then_trail: bool = False,
    sl_to_be_trail_by_when_pct_from_avg_entry: PossibleArray = np.nan,
    # Trailing Stop Loss Params
    tsl_pcts_init: PossibleArray = np.nan,
    tsl_true_or_false: bool = False,
    tsl_based_on: PossibleArray = np.nan,
    tsl_trail_by_pct: PossibleArray = np.nan,
    tsl_when_pct_from_avg_entry: PossibleArray = np.nan,
    # Take Profit Params
    risk_rewards: PossibleArray = np.nan,
    tp_pcts: PossibleArray = np.nan,
) -> tuple[Array1d, RecordArray]:
    open_prices = prices[:, 0]
    high_prices = prices[:, 1]
    low_prices = prices[:, 2]
    close_prices = prices[:, 3]

    # Static checks
    static_variables_tuple = static_var_checker_nb(
        equity=equity,
        fee_pct=fee_pct,
        mmr=mmr,
        lev_mode=lev_mode,
        order_type=order_type,
        size_type=size_type,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        min_order_size_pct=min_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_value=min_order_size_value,
        sl_to_be=sl_to_be,
        sl_to_be_then_trail=sl_to_be_then_trail,
        tsl_true_or_false=tsl_true_or_false,
        gains_pct_filter=-np.inf,
        total_trade_filter=0,
    )

    og_equity = equity

    # Create 1d Arrays
    arrays_1d_tuple = create_1d_arrays_nb(
        leverage=leverage,
        max_equity_risk_pct=max_equity_risk_pct,
        max_equity_risk_value=max_equity_risk_value,
        risk_rewards=risk_rewards,
        size_pct=size_pct,
        size_value=size_value,
        sl_pcts=sl_pcts,
        sl_to_be_based_on=sl_to_be_based_on,
        sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry,
        tp_pcts=tp_pcts,
        tsl_based_on=tsl_based_on,
        tsl_pcts_init=tsl_pcts_init,
        tsl_trail_by_pct=tsl_trail_by_pct,
        tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry,
    )

    # Checking all new arrays
    check_1d_arrays_nb(
        static_variables_tuple=static_variables_tuple,
        arrays_1d_tuple=arrays_1d_tuple,
    )

    x = 0
    biggest = 1
    while x < 7:
        if arrays_1d_tuple[x].size > 1:
            biggest = arrays_1d_tuple[x].size
            x += 1
            break
        x += 1

    while x < 7:
        if arrays_1d_tuple[x].size > 1 and arrays_1d_tuple[x].size != biggest:
            raise ValueError("Size mismatch")
        x += 1
    if biggest > 6:
        raise ValueError("Total amount of tests must be <= 6")

    # Setting variable arrys from cart arrays
    leverage_broadcast_array = np.broadcast_to(arrays_1d_tuple[0], biggest)
    max_equity_risk_pct_broadcast_array = np.broadcast_to(arrays_1d_tuple[1], biggest)
    max_equity_risk_value_broadcast_array = np.broadcast_to(arrays_1d_tuple[2], biggest)
    risk_rewards_broadcast_array = np.broadcast_to(arrays_1d_tuple[3], biggest)
    size_pct_broadcast_array = np.broadcast_to(arrays_1d_tuple[4], biggest)
    size_value_broadcast_array = np.broadcast_to(arrays_1d_tuple[5], biggest)
    sl_pcts_broadcast_array = np.broadcast_to(arrays_1d_tuple[6], biggest)
    sl_to_be_based_on_broadcast_array = np.broadcast_to(arrays_1d_tuple[7], biggest)
    sl_to_be_trail_by_when_pct_from_avg_entry_broadcast_array = np.broadcast_to(
        arrays_1d_tuple[8], biggest
    )
    sl_to_be_when_pct_from_avg_entry_broadcast_array = np.broadcast_to(
        arrays_1d_tuple[9], biggest
    )
    sl_to_be_zero_or_entry_broadcast_array = np.broadcast_to(
        arrays_1d_tuple[10], biggest
    )
    tp_pcts_broadcast_array = np.broadcast_to(arrays_1d_tuple[11], biggest)
    tsl_based_on_broadcast_array = np.broadcast_to(arrays_1d_tuple[12], biggest)
    tsl_pcts_init_broadcast_array = np.broadcast_to(arrays_1d_tuple[13], biggest)
    tsl_trail_by_pct_broadcast_array = np.broadcast_to(arrays_1d_tuple[14], biggest)
    tsl_when_pct_from_avg_entry_broadcast_array = np.broadcast_to(
        arrays_1d_tuple[15], biggest
    )

    if entries.shape[1] == 1:
        entries = np.broadcast_to(entries, (entries.shape[0], biggest))
    elif entries.shape[1] != biggest:
        raise ValueError("Something is wrong with entries")

    total_bars = open_prices.shape[0]

    arrays_1d_tuple = 0

    # Record Arrays
    # final_array = np.empty(biggest, dtype=final_array_dt)
    # final_array_counter = 0

    order_records = np.empty(total_bars * 2, dtype=or_dt)
    order_records_id = np.array([0])
    # or_filled_start = 0

    # order settings loops
    for settings_counter in range(biggest):
        entry_order = EntryOrder(
            leverage=leverage_broadcast_array[settings_counter],
            max_equity_risk_pct=max_equity_risk_pct_broadcast_array[settings_counter],
            max_equity_risk_value=max_equity_risk_value_broadcast_array[
                settings_counter
            ],
            order_type=order_type,
            risk_rewards=risk_rewards_broadcast_array[settings_counter],
            size_pct=size_pct_broadcast_array[settings_counter],
            size_value=size_value_broadcast_array[settings_counter],
            sl_pcts=sl_pcts_broadcast_array[settings_counter],
            tp_pcts=tp_pcts_broadcast_array[settings_counter],
            tsl_pcts_init=tsl_pcts_init_broadcast_array[settings_counter],
        )
        stops_order = StopsOrder(
            sl_to_be=sl_to_be,
            sl_to_be_based_on=sl_to_be_based_on_broadcast_array[settings_counter],
            sl_to_be_then_trail=sl_to_be_then_trail,
            sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_broadcast_array[
                settings_counter
            ],
            sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_broadcast_array[
                settings_counter
            ],
            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_broadcast_array[
                settings_counter
            ],
            tsl_based_on=tsl_based_on_broadcast_array[settings_counter],
            tsl_trail_by_pct=tsl_trail_by_pct_broadcast_array[settings_counter],
            tsl_true_or_false=tsl_true_or_false,
            tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_broadcast_array[
                settings_counter
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

        current_indicator_entries = entries[:, settings_counter]

        # entries loop
        for bar in range(total_bars):
            if account_state.available_balance < 5:
                break

            if current_indicator_entries[bar]:
                # Process Order nb
                account_state, order_result = process_order_nb(
                    price=open_prices[bar],
                    order_type=entry_order.order_type,
                    account_state=account_state,
                    entry_order=entry_order,
                    order_result=order_result,
                    static_variables_tuple=static_variables_tuple,
                    bar=bar,
                    entries_col=settings_counter,
                    symbol_counter=settings_counter,
                    order_settings_counter=settings_counter,
                    order_records=order_records[order_records_id[0]],
                    order_records_id=order_records_id,
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
                        price=open_prices[bar],
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

        # temp_order_records = order_records[or_filled_start : order_records_id[0]]
        # or_filled_start = order_records_id[0]
        # gains_pct = ((account_state.equity - og_equity) / og_equity) * 100

        # w_l = temp_order_records["real_pnl"][~np.isnan(temp_order_records["real_pnl"])]

        # w_l_no_be = w_l[w_l != 0]  # filter out all BE trades

        # # win rate calc
        # win_loss = np.where(w_l_no_be < 0, 0, 1)
        # win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)

        # total_pnl = temp_order_records["real_pnl"][
        #     ~np.isnan(temp_order_records["real_pnl"])
        # ].sum()

        # # to_the_upside calculation
        # x = np.arange(1, len(w_l_no_be) + 1)
        # y = w_l_no_be.cumsum()

        # xm = x.mean()
        # ym = y.mean()

        # y_ym = y - ym
        # y_ym_s = y_ym**2

        # x_xm = x - xm
        # x_xm_s = x_xm**2

        # b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
        # b0 = ym - b1 * xm

        # y_pred = b0 + b1 * x

        # yp_ym = y_pred - ym

        # yp_ym_s = yp_ym**2
        # to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

        # # df array
        # final_array["total_trades"][final_array_counter] = w_l.size
        # final_array["gains_pct"][final_array_counter] = gains_pct
        # final_array["win_rate"][final_array_counter] = win_rate
        # final_array["to_the_upside"][final_array_counter] = to_the_upside
        # final_array["total_pnl"][final_array_counter] = total_pnl
        # final_array["ending_eq"][final_array_counter] = temp_order_records["equity"][-1]
        # final_array["settings_id"][final_array_counter] = final_array_counter
        # final_array["leverage"][final_array_counter] = leverage_broadcast_array[
        #     final_array_counter
        # ]
        # final_array["max_equity_risk_pct"][final_array_counter] = (
        #     max_equity_risk_pct_broadcast_array[final_array_counter] * 100
        # )
        # final_array["max_equity_risk_value"][
        #     final_array_counter
        # ] = max_equity_risk_value_broadcast_array[final_array_counter]
        # final_array["risk_rewards"][final_array_counter] = risk_rewards_broadcast_array[
        #     final_array_counter
        # ]
        # final_array["size_pct"][final_array_counter] = (
        #     size_pct_broadcast_array[final_array_counter] * 100
        # )
        # final_array["size_value"][final_array_counter] = size_value_broadcast_array[
        #     final_array_counter
        # ]
        # final_array["sl_pcts"][final_array_counter] = (
        #     sl_pcts_broadcast_array[final_array_counter] * 100
        # )
        # final_array["sl_to_be_based_on"][
        #     final_array_counter
        # ] = sl_to_be_based_on_broadcast_array[final_array_counter]
        # final_array["sl_to_be_trail_by_when_pct_from_avg_entry"][
        #     final_array_counter
        # ] = (
        #     sl_to_be_trail_by_when_pct_from_avg_entry_broadcast_array[
        #         final_array_counter
        #     ]
        #     * 100
        # )
        # final_array["sl_to_be_when_pct_from_avg_entry"][final_array_counter] = (
        #     sl_to_be_when_pct_from_avg_entry_broadcast_array[final_array_counter] * 100
        # )
        # final_array["sl_to_be_zero_or_entry"][
        #     final_array_counter
        # ] = sl_to_be_zero_or_entry_broadcast_array[final_array_counter]
        # final_array["tp_pcts"][final_array_counter] = (
        #     tp_pcts_broadcast_array[final_array_counter] * 100
        # )
        # final_array["tsl_based_on"][final_array_counter] = tsl_based_on_broadcast_array[
        #     final_array_counter
        # ]
        # final_array["tsl_pcts_init"][final_array_counter] = (
        #     tsl_pcts_init_broadcast_array[final_array_counter] * 100
        # )
        # final_array["tsl_trail_by_pct"][final_array_counter] = (
        #     tsl_trail_by_pct_broadcast_array[final_array_counter] * 100
        # )
        # final_array["tsl_when_pct_from_avg_entry"][final_array_counter] = (
        #     tsl_when_pct_from_avg_entry_broadcast_array[final_array_counter] * 100
        # )

        # final_array_counter += 1

    # return final_array, order_records[: order_records_id[-1]]
    return order_records[: order_records_id[-1]]
