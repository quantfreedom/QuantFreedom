import numpy as np
from numba import njit

from quantfreedom._typing import PossibleArray, Array1d
from quantfreedom.enums.enums import (
    order_settings_array_dt,
    strat_df_array_dt,
    strat_records_dt,
)
from quantfreedom.poly.enums import (
    BacktestSettings,
    ExchangeSettings,
    OrderResult,
    OrderSettingsArrays,
    OrderSettings,
    AccountState,
    RejectedOrderError
)
from quantfreedom.poly.long_short_orders import Order


@njit(cache=True)
def get_order_settings(
    settings_idx: int, os_cart_arrays: OrderSettingsArrays
) -> OrderSettings:
    return OrderSettings(
        risk_account_pct_size=os_cart_arrays.risk_account_pct_size[settings_idx],
        sl_based_on_add_pct=os_cart_arrays.sl_based_on_add_pct[settings_idx],
        sl_based_on_lookback=os_cart_arrays.sl_based_on_lookback[settings_idx],
        risk_reward=os_cart_arrays.risk_reward[settings_idx],
        leverage_type=os_cart_arrays.leverage_type[settings_idx],
        candle_body=os_cart_arrays.candle_body[settings_idx],
        entry_size_type=os_cart_arrays.entry_size_type[settings_idx],
        stop_loss_type=os_cart_arrays.stop_loss_type[settings_idx],
        take_profit_type=os_cart_arrays.take_profit_type[settings_idx],
        max_equity_risk_pct=os_cart_arrays.max_equity_risk_pct[settings_idx],
    )


@njit(cache=True)
def backtest_df_only_nb(
    account_state: AccountState,
    os_cart_arrays: OrderSettings,
    exchange_settings: ExchangeSettings,
    backtest_settings: BacktestSettings,
    num_of_symbols: int,
    total_indicator_settings: int,
    total_order_settings: int,
    total_bars: int,
    entries: PossibleArray,
    price_data: PossibleArray,
) -> Array1d[Array1d, Array1d]:
    og_account_state = account_state
    # Creating strat records
    array_size = int(
        num_of_symbols
        * total_indicator_settings
        * total_order_settings
        / backtest_settings.divide_records_array_size_by
    )

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )
    order_settings_result_records = np.empty(
        array_size,
        dtype=order_settings_array_dt,
    )
    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 3), dtype=strat_records_dt)
    strat_records_filled = np.array([0])

    prices_start = 0
    entries_per_symbol = int(entries.shape[1] / num_of_symbols)
    entries_start = 0
    entries_end = entries_per_symbol
    entries_col = 0
    prices = 0

    for symbol_counter in range(num_of_symbols):
        symbol_price_data = price_data[:, prices_start : prices_start + 4]

        prices_start += 4

        symbol_entries = entries[:, entries_start:entries_end]
        entries_start = entries_end
        entries_end += entries_per_symbol

        # ind set loop
        for indicator_settings_counter in range(entries_per_symbol):
            current_indicator_entries = symbol_entries[:, indicator_settings_counter]

            for order_settings_idx in range(total_order_settings):
                order_settings = get_order_settings(order_settings_idx, os_cart_arrays)
                # Account State Reset
                account_state = AccountState(
                    available_balance=og_account_state.equity,
                    cash_borrowed=0.0,
                    cash_used=0.0,
                    equity=og_account_state.equity,
                )

                # Order Result Reset
                order_result = OrderResult(
                    average_entry=0.,
                    fees_paid=np.nan,
                    leverage=1.,
                    liq_price=np.nan,
                    order_status=0,
                    order_status_info=0,
                    possible_loss=0.,
                    pct_chg_trade=np.nan,
                    entry_size=0.,
                    entry_price=0.,
                    position_size=0.,
                    realized_pnl=np.nan,
                    sl_pct=np.nan,
                    sl_price=np.nan,
                    tp_pct=np.nan,
                    tp_price=np.nan,
                )
                strat_records_filled[0] = 0

                order = Order.instantiate(
                    backtest_settings.order_type,
                    sl_type=order_settings.stop_loss_type,
                    candle_body=order_settings.candle_body,
                    leverage_type=order_settings.leverage_type,
                    entry_size_type=order_settings.entry_size_type,
                    tp_type=order_settings.take_profit_type,
                    account_state=account_state,
                    order_settings=order_settings,
                    exchange_settings=exchange_settings,
                    order_result=order_result,
                )

                # entries loop
                for bar_index in range(total_bars):
                    if current_indicator_entries[
                        bar_index
                    ]:  # add in that we are also not at max entry amount
                        try:
                            order.calc_stop_loss(
                                symbol_price_data=symbol_price_data,
                                bar_index=bar_index,
                            )
                            order.calc_entry_size(
                                entry_price=symbol_price_data[bar_index, 3],
                            )
                            order.calc_leverage()
                            order.calc_take_profit()
                            
                            # all went ok, we are ready to update order_result with the new calculated values
                            order.fill_order_result_entry()
                            print(order.order_result)
                            print("test")
                        except RejectedOrderError as e:
                            print(f'Skipping iteration -> {repr(e)}')
                            order.fill_ignored_order_result_entry(e.order_status)
                        order.fill_order_recrods
                        

                # Checking if gains
            #     gains_pct = (
            #         (account_state.equity - static_variables_tuple.equity)
            #         / static_variables_tuple.equity
            #     ) * 100
            #     if gains_pct > static_variables_tuple.gains_pct_filter:
            #         temp_strat_records = strat_records[0 : strat_records_filled[0]]
            #         wins_and_losses_array = temp_strat_records["real_pnl"][
            #             ~np.isnan(temp_strat_records["real_pnl"])
            #         ]

            #         # Checking total trade filter
            #         if (
            #             wins_and_losses_array.size
            #             > static_variables_tuple.total_trade_filter
            #         ):
            #             wins_and_losses_array_no_be = wins_and_losses_array[
            #                 wins_and_losses_array != 0
            #             ]
            #             to_the_upside = get_to_the_upside_nb(
            #                 gains_pct=gains_pct,
            #                 wins_and_losses_array_no_be=wins_and_losses_array_no_be,
            #             )

            #             # Checking to the upside filter
            #             if to_the_upside > static_variables_tuple.upside_filter:
            #                 fill_strategy_result_records_nb(
            #                     gains_pct=gains_pct,
            #                     strategy_result_records=strategy_result_records[
            #                         result_records_filled
            #                     ],
            #                     temp_strat_records=temp_strat_records,
            #                     to_the_upside=to_the_upside,
            #                     total_trades=wins_and_losses_array.size,
            #                     wins_and_losses_array_no_be=wins_and_losses_array_no_be,
            #                 )

            #                 fill_order_settings_result_records_nb(
            #                     entries_col=entries_col,
            #                     order_settings_result_records=order_settings_result_records[
            #                         result_records_filled
            #                     ],
            #                     symbol_counter=symbol_counter,
            #                     order_settings_tuple=order_settings,
            #                 )
            #                 result_records_filled += 1
            # entries_col += 1
    return (
        strategy_result_records[:result_records_filled],
        order_settings_result_records[:result_records_filled],
    )
