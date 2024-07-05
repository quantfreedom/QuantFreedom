import numpy as np

from logging import getLogger

from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    RejectedOrder,
    ExchangeSettings,
    StaticOrderSettings,
    or_dt,
)

from quantfreedom.order_handler.grid_order_handler import *

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

    total_bars = candles.candle_open_timestamps.size
    or_filled = 0
    order_records = np.empty(shape=int(total_bars / 3), dtype=or_dt)

    for bar_index in range(1, closing_prices.size):
        try:
            if position_size > 0:  # in a long position

                current_candle = grid_order_handler.helpers.get_current_candle(
                    bar_index=bar_index,
                    candles=candles,
                )

                pnl_exec = GridDPExecLong.long_pnl_exec

                grid_order_handler.check_stop_loss_hit(
                    current_candle=current_candle,
                    sl_hit_exec=GridSLExecLong.long_sl_hit_exec,
                )

                grid_order_handler.check_liq_hit(
                    current_candle=current_candle,
                    liq_hit_bool_exec=GridLevExecLong.long_liq_hit_bool_exec,
                )

            elif position_size < 0:

                current_candle = grid_order_handler.helpers.get_current_candle(
                    bar_index=bar_index,
                    candles=candles,
                )

                pnl_exec = GridDPExecShort.short_pnl_exec

                grid_order_handler.check_stop_loss_hit(
                    current_candle=current_candle,
                    sl_hit_exec=GridSLExecShort.short_sl_hit_exec,
                )

                grid_order_handler.check_liq_hit(
                    current_candle=current_candle,
                    liq_hit_bool_exec=GridLevExecShort.short_liq_hit_bool_exec,
                )

        except DecreasePosition as dp:
            (
                equity,
                fees_paid,
                realized_pnl,
            ) = grid_order_handler.calculate_decrease_position(
                cur_datetime=candles.candle_open_datetimes[bar_index],
                exit_price=dp.exit_price,
                equity=grid_order_handler.equity,
                order_status=dp.order_status,
                pnl_exec=pnl_exec,
            )

            grid_order_handler.helpers.fill_order_record_exit(
                bar_index=bar_index,
                set_idx=0,
                order_records=order_records[or_filled],
                order_status=dp.order_status,
                timestamp=current_candle.open_timestamp,
                equity=equity,
                fees_paid=fees_paid,
                realized_pnl=realized_pnl,
                sl_price=dp.sl_price,
                liq_price=dp.liq_price,
            )

            or_filled += 1
            logger.debug(f"Filled decrease postiion order records for {OrderStatus._fields[dp.order_status]}")

            grid_order_handler.helpers.reset_grid_order_variables(
                equity=equity,
            )
            logger.debug("reset order variables")
        try:
            if low_prices[bar_index] <= buy_order:
                order_size = equity * pct_account
                temp_pos_size = position_size + order_size

                buy_signals[bar_index] = buy_order
                if position_size >= 0:
                    # adding to long position
                    get_bankruptcy_price_exec = GridLevExecLong.long_get_bankruptcy_price_exec
                    get_liq_price_exec = GridLevExecLong.long_get_liq_price_exec

                    average_entry = grid_order_handler.calculate_increase_position(
                        order_size=order_size,
                        entry_price=buy_order,
                    )
                    ae_buy_array[bar_index] = average_entry

                elif temp_pos_size >= 0 and position_size <= 0:
                    # switch from short to long
                    get_bankruptcy_price_exec = GridLevExecLong.long_get_bankruptcy_price_exec
                    get_liq_price_exec = GridLevExecLong.long_get_liq_price_exec

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        equity=equity,
                        order_status=OrderStatus.TakeProfitFilled,
                        pnl_exec=GridDPExecShort.short_pnl_exec,
                    )

                    average_entry = buy_order
                    ae_buy_array[bar_index] = average_entry

                elif temp_pos_size < 0:
                    # tp on short
                    get_bankruptcy_price_exec = GridLevExecShort.short_get_bankruptcy_price_exec
                    get_liq_price_exec = GridLevExecShort.short_get_liq_price_exec

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        equity=equity,
                        order_status=OrderStatus.TakeProfitFilled,
                        pnl_exec=GridDPExecShort.short_pnl_exec,
                    )

                position_size = temp_pos_size

                (
                    available_balance,
                    cash_borrowed,
                    cash_used,
                    liq_price,
                ) = grid_order_handler.leverage_class.calculate_liquidation_price(
                    average_entry=average_entry,
                    leverage=leverage,
                    og_available_balance=avaliable_balance,
                    og_cash_borrowed=cash_borrowed,
                    og_cash_used=cash_used,
                    position_size_asset=average_entry / position_size,
                    position_size_usd=position_size,
                )

                grid_order_handler.fill_or_entry(
                    bar_index=bar_index + 1,
                    set_idx=0,
                    order_records=order_records[or_filled],
                    timestamp=candles.candle_open_timestamps[bar_index + 1],
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
        except RejectedOrder:
            pass
