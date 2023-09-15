from typing import Optional
import numpy as np
from numba import njit

from quantfreedom.class_practice.enums import (
    AccountState,
    BacktestSettings,
    DecreasePosition,
    ExchangeSettings,
    MoveStopLoss,
    OrderResult,
    OrderSettingsArrays,
    OrderSettings,
    RejectedOrderError,
    OrderStatus,
)
from quantfreedom.class_practice.long_short_orders import Order
from quantfreedom.enums.enums import (
    order_settings_array_dt,
    strat_df_array_dt,
    strat_records_dt,
)


@njit(cache=True)
def get_order_settings(
    settings_idx: int,
    os_cart_arrays: OrderSettingsArrays,
) -> OrderSettings:
    return OrderSettings(
        risk_account_pct_size=os_cart_arrays.risk_account_pct_size[settings_idx],
        sl_based_on_add_pct=os_cart_arrays.sl_based_on_add_pct[settings_idx],
        sl_based_on_lookback=os_cart_arrays.sl_based_on_lookback[settings_idx],
        risk_reward=os_cart_arrays.risk_reward[settings_idx],
        leverage_type=os_cart_arrays.leverage_type[settings_idx],
        sl_candle_body_type=os_cart_arrays.sl_candle_body_type[settings_idx],
        increase_position_type=os_cart_arrays.increase_position_type[settings_idx],
        stop_loss_type=os_cart_arrays.stop_loss_type[settings_idx],
        take_profit_type=os_cart_arrays.take_profit_type[settings_idx],
        max_equity_risk_pct=os_cart_arrays.max_equity_risk_pct[settings_idx],
        order_type=os_cart_arrays.order_type[settings_idx],
        sl_to_be_based_on_candle_body_type=os_cart_arrays.sl_to_be_based_on_candle_body_type[
            settings_idx
        ],
        sl_to_be_when_pct_from_candle_body=os_cart_arrays.sl_to_be_when_pct_from_candle_body[
            settings_idx
        ],
        sl_to_be_zero_or_entry=os_cart_arrays.sl_to_be_zero_or_entry[settings_idx],
        trail_sl_based_on_candle_body_type=os_cart_arrays.trail_sl_based_on_candle_body_type[
            settings_idx
        ],
        trail_sl_when_pct_from_candle_body=os_cart_arrays.trail_sl_when_pct_from_candle_body[
            settings_idx
        ],
        trail_sl_by_pct=os_cart_arrays.trail_sl_by_pct[settings_idx],
        static_leverage=os_cart_arrays.static_leverage[settings_idx],
        tp_fee_type=os_cart_arrays.tp_fee_type[settings_idx],
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
    entries: np.array,
    price_data: np.array,
    exit_signals: Optional[np.array] = None,
):
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
        print("\nNew Symbol")
        symbol_price_data = price_data[:, prices_start : prices_start + 4]

        prices_start += 4

        symbol_entries = entries[:, entries_start:entries_end]
        entries_start = entries_end
        entries_end += entries_per_symbol

        # ind set loop
        for indicator_settings_counter in range(entries_per_symbol):
            print("\nNew Indicator Setting")
            current_indicator_entries = symbol_entries[:, indicator_settings_counter]
            current_exit_signals = exit_signals[:, indicator_settings_counter]

            for order_settings_idx in range(total_order_settings):
                print("\nNew Order Setting")
                order_settings = get_order_settings(order_settings_idx, os_cart_arrays)
                # Account State Reset
                account_state = AccountState(
                    available_balance=account_state.equity,
                    cash_borrowed=0.0,
                    cash_used=0.0,
                    equity=account_state.equity,
                )

                # Order Result Reset
                order_result = OrderResult(
                    average_entry=0.0,
                    fees_paid=0.0,
                    leverage=1.0,
                    liq_price=0.0,
                    order_status=0,
                    possible_loss=0.0,
                    entry_size=0.0,
                    entry_price=0.0,
                    exit_price=0.0,
                    position_size=0.0,
                    realized_pnl=0.0,
                    sl_pct=0.0,
                    sl_price=0.0,
                    tp_pct=0.0,
                    tp_price=0.0,
                )
                strat_records_filled[0] = 0

                order = Order.instantiate(
                    account_state=account_state,
                    order_settings=order_settings,
                    exchange_settings=exchange_settings,
                    order_result=order_result,
                    order_type=order_settings.order_type,
                    symbol_price_data=symbol_price_data,
                )

                # entries loop
                for bar_index in range(total_bars):
                    if current_indicator_entries[
                        bar_index
                    ]:  # add in that we are also not at max entry amount
                        print(f"Order - Try to Enter Trade - bar_index= {bar_index}")
                        try:
                            order.calculate_stop_loss(bar_index=bar_index)
                            order.calculate_increase_posotion(
                                entry_price=symbol_price_data[
                                    bar_index, 0
                                ]  # entry price is open because we are getting the signal from the close of the previous candle
                            )
                            order.calculate_leverage()
                            order.calculate_take_profit()
                            order.fill_order_result_successful_entry()
                        except RejectedOrderError as e:
                            print(f"Skipping iteration -> {repr(e)}")
                            # order.fill_order_result_rejected_entry()

                    if order.position_size > 0:
                        try:
                            # need to figure out a way that if any of these are hit i get kicked out and then return the order result
                            # need to add in filling in the strat records
                            # do all of this through printing before you add any real code or you will hate your life
                            order.check_stop_loss_hit(
                                current_candle=symbol_price_data[bar_index, :]
                            )
                            order.check_liq_hit(
                                current_candle=symbol_price_data[bar_index, :]
                            )
                            order.check_take_profit_hit(
                                exit_signal=current_exit_signals[bar_index],
                                current_candle=symbol_price_data[bar_index, :],
                            )
                            # need to figure out a way to say if one of these three are hit then kick me out and go to decrease the position size
                            order.check_move_stop_loss_to_be(
                                bar_index=bar_index, symbol_price_data=symbol_price_data
                            )
                            order.check_move_trailing_stop_loss(
                                bar_index=bar_index, symbol_price_data=symbol_price_data
                            )
                        except RejectedOrderError as e:
                            print(f"Skipping iteration -> {repr(e.order_status)}")
                            # order.fill_order_result_rejected_exit()
                        except DecreasePosition as e:
                            print(
                                f"Order - Decrease Position - order_status= {OrderStatus._fields[e.order_status]} exit_price= {e.exit_price}"
                            )
                            order.decrease_position(
                                order_status=e.order_status,
                                exit_price=e.exit_price,
                                exit_fee_pct=e.exit_fee_pct,
                            )
                        except MoveStopLoss as e:
                            print(f"Decrease Position -> {repr(e.order_status)}")

                    print("\nChecking Next Bar for entry or exit")

                # Checking if gains
            #     gains_pct = (
            #         (order.equity - account_state.equity)
            #         / account_state.equity
            #     ) * 100
            #     if gains_pct > backtest_settings.gains_pct_filter:
            #         temp_strat_records = strat_records[0 : strat_records_filled[0]]
            #         wins_and_losses_array = temp_strat_records["real_pnl"][
            #             ~np.isnan(temp_strat_records["real_pnl"])
            #         ]

            #         # Checking total trade filter
            #         if (
            #             wins_and_losses_array.size
            #             > backtest_settings.total_trade_filter
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
