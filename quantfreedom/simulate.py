from typing import Optional
import numpy as np

from quantfreedom.enums import *
from quantfreedom.long_short_orders import Order
from quantfreedom.nb.helper_funcs import get_to_the_upside_nb


def get_order_settings(
    settings_idx: int,
    os_cart_arrays: OrderSettingsArrays,
) -> OrderSettings:
    return OrderSettings(
        increase_position_type=os_cart_arrays.increase_position_type[settings_idx],
        leverage_type=os_cart_arrays.leverage_type[settings_idx],
        max_equity_risk_pct=os_cart_arrays.max_equity_risk_pct[settings_idx],
        order_type=os_cart_arrays.order_type[settings_idx],
        risk_account_pct_size=os_cart_arrays.risk_account_pct_size[settings_idx],
        risk_reward=os_cart_arrays.risk_reward[settings_idx],
        sl_based_on_add_pct=os_cart_arrays.sl_based_on_add_pct[settings_idx],
        sl_based_on_lookback=os_cart_arrays.sl_based_on_lookback[settings_idx],
        sl_candle_body_type=os_cart_arrays.sl_candle_body_type[settings_idx],
        sl_to_be_based_on_candle_body_type=os_cart_arrays.sl_to_be_based_on_candle_body_type[settings_idx],
        sl_to_be_when_pct_from_candle_body=os_cart_arrays.sl_to_be_when_pct_from_candle_body[settings_idx],
        sl_to_be_zero_or_entry_type=os_cart_arrays.sl_to_be_zero_or_entry_type[settings_idx],
        static_leverage=os_cart_arrays.static_leverage[settings_idx],
        stop_loss_type=os_cart_arrays.stop_loss_type[settings_idx],
        take_profit_type=os_cart_arrays.take_profit_type[settings_idx],
        tp_fee_type=os_cart_arrays.tp_fee_type[settings_idx],
        trail_sl_based_on_candle_body_type=os_cart_arrays.trail_sl_based_on_candle_body_type[settings_idx],
        trail_sl_by_pct=os_cart_arrays.trail_sl_by_pct[settings_idx],
        trail_sl_when_pct_from_candle_body=os_cart_arrays.trail_sl_when_pct_from_candle_body[settings_idx],
    )


def backtest_df_only_nb(
    account_state: AccountState,
    os_cart_arrays: OrderSettings,
    exchange_settings: ExchangeSettings,
    backtest_settings: BacktestSettings,
    total_indicator_settings: int,
    total_order_settings: int,
    total_bars: int,
    entries: np.array,
    price_data: np.array,
    exit_signals: Optional[np.array] = None,
):
    # Creating strat records
    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )

    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 2), dtype=strat_records_dt)

    num_entries = entries.shape[1]

    for indicator_settings_index in range(num_entries):
        current_indicator_entries = entries[:, indicator_settings_index]
        current_exit_signals = exit_signals[:, indicator_settings_index]

        for order_settings_index in range(total_order_settings):
            order_settings = get_order_settings(order_settings_index, os_cart_arrays)
            # Account State Reset
            account_state = AccountState(
                available_balance=account_state.equity,
                cash_borrowed=0.0,
                cash_used=0.0,
                equity=account_state.equity,
            )

            order = Order.instantiate(
                account_state=account_state,
                order_settings=order_settings,
                exchange_settings=exchange_settings,
                order_type=order_settings.order_type,
                strat_records=strat_records,
            )

            # entries loop
            for bar_index in range(total_bars):
                if current_indicator_entries[bar_index]:  # add in that we are also not at max entry amount
                    try:
                        order.calculate_stop_loss(
                            bar_index=bar_index,
                            price_data=price_data,
                        )
                        order.calculate_increase_posotion(
                            entry_price=price_data[
                                bar_index, 0
                            ]  # entry price is open because we are getting the signal from the close of the previous candle
                        )
                        order.calculate_leverage()
                        order.calculate_take_profit()

                    except RejectedOrderError as e:
                        pass
                if order.position_size > 0:
                    try:
                        order.check_stop_loss_hit(current_candle=price_data[bar_index, :])
                        order.check_liq_hit(current_candle=price_data[bar_index, :])
                        order.check_take_profit_hit(
                            current_candle=price_data[bar_index, :],
                            exit_signal=current_exit_signals[bar_index],
                        )
                        order.check_move_stop_loss_to_be(bar_index=bar_index, price_data=price_data)
                        order.check_move_trailing_stop_loss(bar_index=bar_index, price_data=price_data)
                    except RejectedOrderError as e:
                        pass
                    except DecreasePosition as e:
                        order.decrease_position(
                            order_status=e.order_status,
                            exit_price=e.exit_price,
                            exit_fee_pct=e.exit_fee_pct,
                            bar_index=bar_index,
                            indicator_settings_index=indicator_settings_index,
                            order_settings_index=order_settings_index,
                        )
                    except MoveStopLoss as e:
                        order.move_stop_loss(
                            sl_price=e.sl_price,
                            order_status=e.order_status,
                            bar_index=bar_index,
                            order_settings_index=order_settings_index,
                            indicator_settings_index=indicator_settings_index,
                        )
            # Checking if gains
            gains_pct = ((order.equity - account_state.equity) / account_state.equity) * 100
            if gains_pct > backtest_settings.gains_pct_filter:
                temp_strat_records = order.strat_records[: order.strat_records_filled]
                pnl_array = temp_strat_records["real_pnl"]
                wins_and_losses_array = pnl_array[~np.isnan(temp_strat_records["real_pnl"])]

                # Checking total trade filter
                if wins_and_losses_array.size > backtest_settings.total_trade_filter:
                    wins_and_losses_array_no_be = wins_and_losses_array[wins_and_losses_array != 0]
                    to_the_upside = get_to_the_upside_nb(
                        gains_pct=gains_pct,
                        wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                    )

                    # Checking to the upside filter
                    if to_the_upside > backtest_settings.upside_filter:
                        win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
                        win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)
                        total_pnl = pnl_array.sum()

                        # strat array
                        strategy_result_records[result_records_filled]["ind_set_idx"] = indicator_settings_index
                        strategy_result_records[result_records_filled]["or_set_idx"] = order_settings_index
                        strategy_result_records[result_records_filled]["total_trades"] = wins_and_losses_array.size
                        strategy_result_records[result_records_filled]["gains_pct"] = gains_pct
                        strategy_result_records[result_records_filled]["win_rate"] = win_rate
                        strategy_result_records[result_records_filled]["to_the_upside"] = to_the_upside
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["ending_eq"] = order.equity

                        result_records_filled += 1

    return strategy_result_records[:result_records_filled]


def sim_6_nb(
    account_state: AccountState,
    entries: np.array,
    exchange_settings: ExchangeSettings,
    indicator_indexes: np.array,
    os_cart_arrays: OrderSettings,
    or_settings_indexes: np.array,
    price_data: np.array,
    strat_indexes_len: int,
    exit_signals: np.array,
):
    total_bars = price_data.shape[0]
    order_records = np.empty(total_bars * strat_indexes_len, dtype=or_dt)
    total_order_records_filled = 0

    for i in range(strat_indexes_len):
        indicator_settings_index = indicator_indexes[i]
        order_settings_index = or_settings_indexes[i]
        current_indicator_entries = entries[:, indicator_settings_index]
        current_exit_signals = exit_signals[:, indicator_settings_index]
        order_settings = get_order_settings(order_settings_index, os_cart_arrays)

        account_state = AccountState(
            available_balance=account_state.equity,
            cash_borrowed=0.0,
            cash_used=0.0,
            equity=account_state.equity,
        )

        order = Order.instantiate(
            account_state=account_state,
            order_settings=order_settings,
            exchange_settings=exchange_settings,
            order_type=order_settings.order_type,
            order_records=order_records,
            total_order_records_filled=total_order_records_filled,
        )

        for bar_index in range(total_bars):
            if current_indicator_entries[bar_index]:  # add in that we are also not at max entry amount
                try:
                    order.calculate_stop_loss(bar_index=bar_index, price_data=price_data)
                    order.calculate_increase_posotion(
                        entry_price=price_data[
                            bar_index, 0
                        ]  # entry price is open because we are getting the signal from the close of the previous candle
                    )
                    order.calculate_leverage()
                    order.calculate_take_profit()
                    order.or_filler(
                        order_result=OrderResult(
                            indicator_settings_index=indicator_settings_index,
                            order_settings_index=order_settings_index,
                            bar_index=bar_index,
                            available_balance=order.available_balance,
                            cash_borrowed=order.cash_borrowed,
                            cash_used=order.cash_used,
                            average_entry=order.average_entry,
                            leverage=order.leverage,
                            liq_price=order.liq_price,
                            order_status=order.order_status,
                            possible_loss=order.possible_loss,
                            entry_size=order.entry_size,
                            entry_price=order.entry_price,
                            position_size=order.position_size,
                            sl_pct=order.sl_pct,
                            sl_price=order.sl_price,
                            tp_pct=order.tp_pct,
                            tp_price=order.tp_price,
                        )
                    )
                except RejectedOrderError as e:
                    pass
            if order.position_size > 0:
                try:
                    order.check_stop_loss_hit(current_candle=price_data[bar_index, :])
                    order.check_liq_hit(current_candle=price_data[bar_index, :])
                    order.check_take_profit_hit(
                        current_candle=price_data[bar_index, :],
                        exit_signal=current_exit_signals[bar_index],
                    )
                    order.check_move_stop_loss_to_be(bar_index=bar_index, price_data=price_data)
                    order.check_move_trailing_stop_loss(bar_index=bar_index, price_data=price_data)
                except RejectedOrderError as e:
                    pass
                except DecreasePosition as e:
                    order.decrease_position(
                        order_status=e.order_status,
                        exit_price=e.exit_price,
                        exit_fee_pct=e.exit_fee_pct,
                        bar_index=bar_index,
                        indicator_settings_index=indicator_settings_index,
                        order_settings_index=order_settings_index,
                    )
                except MoveStopLoss as e:
                    order.move_stop_loss(
                        sl_price=e.sl_price,
                        order_status=e.order_status,
                        bar_index=bar_index,
                        order_settings_index=order_settings_index,
                        indicator_settings_index=indicator_settings_index,
                    )
        order_records = order.order_records
        total_order_records_filled = order.total_order_records_filled

    return order_records[:total_order_records_filled]
