import numpy as np
import logging
from quantfreedom.enums import *
from quantfreedom.helper_funcs import get_order_setting, get_to_the_upside_nb
from quantfreedom.order_handler.order_handler import Order
from quantfreedom.strategy import Strategy

info_logger = logging.getLogger("info")


def backtest_df_only_classes(
    starting_equity: float,
    os_cart_arrays: OrderSettings,
    exchange_settings: ExchangeSettings,
    backtest_settings: BacktestSettings,
    strategy: Strategy,
    total_indicator_settings: int,
    total_order_settings: int,
    total_bars: int,
    candles: np.array,
):
    # Creating strat records
    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )

    result_records_filled = 0

    strat_records = np.empty(int(total_bars / 2), dtype=strat_records_dt)

    for indicator_settings_index in range(total_indicator_settings):
        info_logger.debug(f"Indicator settings index = {indicator_settings_index}")
        strategy.set_indicator_settings(indicator_settings_index=indicator_settings_index)

        for order_settings_index in range(total_order_settings):
            info_logger.debug(f"Order settings index = {order_settings_index}")
            order_settings = get_order_setting(
                order_settings_index=order_settings_index,
                os_cart_arrays=os_cart_arrays,
            )

            strategy.num_candles = int(-(order_settings.num_candles - 1))
            order = Order.instantiate(
                equity=starting_equity,
                order_settings=order_settings,
                exchange_settings=exchange_settings,
                long_or_short=order_settings.long_or_short,
                strat_records=strat_records,
            )
            info_logger.debug(f"Created Order class")

            # entries loop
            for bar_index in range(int(order_settings.num_candles - 1), total_bars):
                strategy.create_indicator(bar_index)
                if strategy.evaluate():  # add in that we are also not at max entry amount
                    info_logger.debug(
                        f"ind_idx={indicator_settings_index} os_idx={order_settings_index} b_idx={bar_index}"
                    )
                    try:
                        order.calculate_stop_loss(
                            bar_index=bar_index,
                            candles=candles,
                        )
                        order.calculate_increase_posotion(
                            entry_price=candles[
                                bar_index, 0
                            ]  # entry price is open because we are getting the signal from the close of the previous candle
                        )
                        order.calculate_leverage()
                        order.calculate_take_profit()

                    except RejectedOrder as e:
                        info_logger.warning(f"RejectedOrder -> {e.msg}")
                        pass
                    except Exception as e:
                        info_logger.error(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
                if order.position_size_usd > 0:
                    try:
                        order.check_stop_loss_hit(current_candle=candles[bar_index, :])
                        order.check_liq_hit(current_candle=candles[bar_index, :])
                        order.check_take_profit_hit(
                            current_candle=candles[bar_index, :],
                            exit_signal=strategy.current_exit_signals[bar_index],
                        )
                        order.check_move_stop_loss_to_be(bar_index=bar_index, candles=candles)
                        order.check_move_trailing_stop_loss(bar_index=bar_index, candles=candles)
                    except RejectedOrder as e:
                        info_logger.warning(f"RejectedOrder -> {e.msg}")
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
                    except Exception as e:
                        info_logger.error(f"Exception placing order -> {e}")
                        raise Exception(f"Exception placing order -> {e}")
            # Checking if gains
            gains_pct = round(((order.equity - starting_equity) / starting_equity) * 100, 2)
            info_logger.debug(f"Starting eq={starting_equity} Ending eq={order.equity} gains pct={gains_pct}")
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
        info_logger.info(f"Starting New Loop\n\n")
    return strategy_result_records[:result_records_filled]


def sim_6_nb(
    entries: np.array,
    exchange_settings: ExchangeSettings,
    indicator_indexes: np.array,
    os_cart_arrays: OrderSettings,
    or_settings_indexes: np.array,
    candles: np.array,
    strat_indexes_len: int,
    exit_signals: np.array,
):
    total_bars = candles.shape[0]
    order_records = np.empty(total_bars * strat_indexes_len, dtype=or_dt)
    total_order_records_filled = 0

    for i in range(strat_indexes_len):
        indicator_settings_index = indicator_indexes[i]
        order_settings_index = or_settings_indexes[i]
        current_indicator_entries = entries[:, indicator_settings_index]
        current_exit_signals = exit_signals[:, indicator_settings_index]
        order_settings = get_order_settings(order_settings_index, os_cart_arrays)

        order = Order.instantiate(
            order_settings=order_settings,
            exchange_settings=exchange_settings,
            long_or_short=order_settings.long_or_short,
            order_records=order_records,
            total_order_records_filled=total_order_records_filled,
        )

        for bar_index in range(total_bars):
            if current_indicator_entries[bar_index]:  # add in that we are also not at max entry amount
                try:
                    order.calculate_stop_loss(bar_index=bar_index, candles=candles)
                    order.calculate_increase_posotion(
                        entry_price=candles[
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
                            entry_size_usd=order.entry_size_usd,
                            entry_price=order.entry_price,
                            position_size_usd=order.position_size_usd,
                            sl_pct=order.sl_pct,
                            sl_price=order.sl_price,
                            tp_pct=order.tp_pct,
                            tp_price=order.tp_price,
                        )
                    )
                except RejectedOrder as e:
                    pass
            if order.position_size_usd > 0:
                try:
                    order.check_stop_loss_hit(current_candle=candles[bar_index, :])
                    order.check_liq_hit(current_candle=candles[bar_index, :])
                    order.check_take_profit_hit(
                        current_candle=candles[bar_index, :],
                        exit_signal=current_exit_signals[bar_index],
                    )
                    order.check_move_stop_loss_to_be(bar_index=bar_index, candles=candles)
                    order.check_move_trailing_stop_loss(bar_index=bar_index, candles=candles)
                except RejectedOrder as e:
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
