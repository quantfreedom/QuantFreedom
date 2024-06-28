from typing import Callable
import numpy as np
from logging import getLogger
from quantfreedom.helpers.helper_funcs import round_size_by_tick_step
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    RejectedOrder,
    ExchangeSettings,
    StaticOrderSettings,
)

from quantfreedom.order_handler.grid_order_handler import GridOrderHandler, GridStopLoss, GridLeverage

logger = getLogger()


def grid_backtest(
    candles: FootprintCandlesTuple,
    price_pct: float,
    pct_account: float,
    leverage: float,
    equity: float = 1000,
    exchange_settings_tuple: ExchangeSettings = None,
    static_os_tuple: StaticOrderSettings = None,
):

    position_size = 0
    average_entry = 0
    cash_borrowed = 0
    cash_used = 0
    avaliable_balance = equity

    closing_prices = candles.candle_close_prices
    low_prices = candles.candle_low_prices
    high_prices = candles.candle_high_prices
    open_prices = candles.candle_open_prices
    datetimes = candles.candle_open_datetimes

    grid_order_handler = GridOrderHandler(
        exchange_settings_tuple=exchange_settings_tuple,
        static_os_tuple=static_os_tuple,
    )

    pnl_array = np.full_like(closing_prices, np.nan)
    ae_buy_array = np.full_like(closing_prices, np.nan)
    ae_sell_array = np.full_like(closing_prices, np.nan)
    ps_array = np.full_like(closing_prices, np.nan)

    sell_order = closing_prices[0] + (closing_prices[0] * price_pct)
    sell_signals = np.full_like(closing_prices, np.nan)

    buy_order = closing_prices[0] - (closing_prices[0] * price_pct)
    buy_signals = np.full_like(closing_prices, np.nan)

    for bar_index in range(1, closing_prices.size):
        try:
            if position_size > 0:
                current_candle = CurrentFootprintCandleTuple(
                    open_timestamp=candles.candle_open_timestamps[bar_index],
                    open_price=candles.candle_open_prices[bar_index],
                    high_price=candles.candle_high_prices[bar_index],
                    low_price=candles.candle_low_prices[bar_index],
                    close_price=candles.candle_close_prices[bar_index],
                )
                grid_order_handler.obj_stop_loss.get_sl_hit = GridStopLoss.long_sl_hit_bool
                grid_order_handler.check_stop_loss_hit(current_candle=current_candle)

                grid_order_handler.obj_leverage.liq_hit_bool = GridLeverage.long_liq_hit_bool
                grid_order_handler.check_liq_hit(current_candle=current_candle)

            elif position_size < 0:
                current_candle = CurrentFootprintCandleTuple(
                    open_timestamp=candles.candle_open_timestamps[bar_index],
                    open_price=candles.candle_open_prices[bar_index],
                    high_price=candles.candle_high_prices[bar_index],
                    low_price=candles.candle_low_prices[bar_index],
                    close_price=candles.candle_close_prices[bar_index],
                )
                grid_order_handler.obj_stop_loss.get_sl_hit = GridStopLoss.short_sl_hit_bool
                grid_order_handler.check_stop_loss_hit(current_candle=current_candle)

                grid_order_handler.obj_leverage.liq_hit_bool = GridLeverage.short_liq_hit_bool
                grid_order_handler.check_liq_hit(current_candle=current_candle)

        except DecreasePosition as e:
            (
                equity,
                fees_paid,
                realized_pnl,
            ) = grid_order_handler.calculate_decrease_position(
                cur_datetime=candles.candle_open_datetimes[bar_index],
                exit_fee_pct=e.exit_fee_pct,
                exit_price=e.exit_price,
                order_status=e.order_status,
                market_fee_pct=strategy.exchange_settings_tuple.market_fee_pct,
                equity=order.equity,
            )
            logger.debug(f"Filling or for decrease postiion {OrderStatus._fields[e.order_status]}")
            grid_order_handler.fill_or_exit_move(
                bar_index=bar_index,
                set_idx=set_idx,
                order_records=order_records[or_filled],
                order_status=e.order_status,
                timestamp=current_candle.open_timestamp,
                equity=equity,
                exit_price=e.exit_price,
                fees_paid=fees_paid,
                realized_pnl=realized_pnl,
            )
            or_filled += 1
            logger.debug(f"Filled decrease postiion order records for {OrderStatus._fields[e.order_status]}")

            grid_order_handler.set_order_variables(equity=equity)
            logger.debug("reset order variables")

        if low_prices[bar_index] <= buy_order:
            order_size = equity * pct_account
            temp_pos_size = position_size + order_size

            buy_signals[bar_index] = buy_order
            if position_size >= 0:
                # adding to long position
                grid_order_handler.obj_leverage.get_bankruptcy_price = GridLeverage.long_get_bankruptcy_price
                grid_order_handler.obj_leverage.get_liq_price = GridLeverage.long_get_liq_price
                
                try:
                    average_entry = (position_size + order_size) / (
                        (position_size / average_entry) + (order_size / buy_order)
                    )
                    ae_buy_array[bar_index] = average_entry
                except ZeroDivisionError:
                    average_entry = buy_order
                    ae_buy_array[bar_index] = average_entry

            elif temp_pos_size >= 0 and position_size <= 0:
                # switch from short to long
                grid_order_handler.obj_leverage.get_bankruptcy_price = GridLeverage.long_get_bankruptcy_price
                grid_order_handler.obj_leverage.get_liq_price = GridLeverage.long_get_liq_price
                grid_order_handler.pnl_calc = grid_order_handler.short_pnl_calc
                
                grid_order_handler.calculate_decrease_position(
                    cur_datetime=candles.candle_open_datetimes[bar_index],
                    exit_price=buy_order,
                    equity=equity,   
                )

                average_entry = buy_order
                ae_buy_array[bar_index] = average_entry

            elif temp_pos_size < 0:
                # tp on short
                
                grid_order_handler.obj_leverage.get_bankruptcy_price = GridLeverage.short_get_bankruptcy_price
                grid_order_handler.obj_leverage.get_liq_price = GridLeverage.short_get_liq_price
                grid_order_handler.pnl_calc = grid_order_handler.short_pnl_calc
                
                
                equity = calc_take_profit(
                    average_entry=average_entry,
                    equity=equity,
                    bar_index=bar_index,
                    limit_order=buy_order,
                    order_size=order_size,
                    pnl_array=pnl_array,
                    tp_on_long_short="short",
                )

            position_size = temp_pos_size

            (
                available_balance,
                cash_borrowed,
                cash_used,
                liq_price,
            ) = grid_order_handler.obj_leverage.calc_liq_price(
                average_entry=average_entry,
                leverage=leverage,
                og_available_balance=avaliable_balance,
                og_cash_borrowed=cash_borrowed,
                og_cash_used=cash_used,
                position_size_asset=average_entry / position_size,
                position_size_usd=position_size,
            )

            ps_array[bar_index] = position_size
            buy_order = closing_prices[bar_index] - (closing_prices[bar_index] * price_pct)
            sell_order = closing_prices[bar_index] + (closing_prices[bar_index] * price_pct)

        elif high_prices[bar_index] >= sell_order:
            order_size = equity * pct_account
            temp_pos_size = position_size + -order_size

            sell_signals[bar_index] = sell_order

            if temp_pos_size > 0:
                # tp on long
                equity = calc_take_profit(
                    average_entry=average_entry,
                    equity=equity,
                    bar_index=bar_index,
                    limit_order=sell_order,
                    order_size=order_size,
                    pnl_array=pnl_array,
                    tp_on_long_short="long",
                )

            elif temp_pos_size <= 0 and position_size >= 0:

                equity = calc_take_profit(
                    average_entry=average_entry,
                    equity=equity,
                    bar_index=bar_index,
                    limit_order=sell_order,
                    order_size=position_size,
                    pnl_array=pnl_array,
                    tp_on_long_short="long",
                )
                average_entry = sell_order
                ae_sell_array[bar_index] = average_entry

            elif position_size <= 0:
                # adding to short position
                try:
                    average_entry = (-position_size + order_size) / (
                        (-position_size / average_entry) + (order_size / sell_order)
                    )
                    ae_sell_array[bar_index] = average_entry

                except ZeroDivisionError:
                    average_entry = sell_order
                    ae_sell_array[bar_index] = average_entry

            position_size = temp_pos_size
            ps_array[bar_index] = position_size
            buy_order = closing_prices[bar_index] - (closing_prices[bar_index] * price_pct)
            sell_order = closing_prices[bar_index] + (closing_prices[bar_index] * price_pct)
