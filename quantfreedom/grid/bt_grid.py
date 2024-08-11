import numpy as np
from os.path import join, abspath

from logging import getLogger

from quantfreedom.core.enums import (
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    RejectedOrder,
    ExchangeSettings,
    StaticOrderSettings,
    or_dt,
)

from quantfreedom.grid.grid_order_handler.grid_order import GridOrderHandler
from quantfreedom.grid.grid_order_handler.grid_leverage.grid_lev_exec import Grid_Lev_Funcs
from quantfreedom.grid.grid_order_handler.grid_stop_loss.grid_sl_exec import Grid_SL_Funcs
from quantfreedom.grid.grid_order_handler.grid_decrease_position.grid_dp_exec import Grid_DP_Funcs
from quantfreedom.helpers.custom_logger import set_loggers


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
    set_loggers(
        disable_logger=False,
        log_level="DEBUG",
        log_path=abspath(join(abspath(""), "..")),
    )
    price_pct /= 100
    pct_account /= 100

    position_size_usd = 0
    average_entry = 0

    closing_prices = candles.candle_close_prices
    low_prices = candles.candle_low_prices
    high_prices = candles.candle_high_prices
    open_prices = candles.candle_open_prices
    datetimes = candles.candle_open_datetimes

    grid_order_handler = GridOrderHandler()

    grid_order_handler.reset_grid_order_variables(equity=equity)

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
        logger.debug(f"\n\n\n\n\n")
        logger.debug(f"Bar Index: {bar_index}")
        try:
            if position_size_usd > 0:  # in a long position

                current_candle = grid_order_handler.helpers.get_current_candle(
                    bar_index=bar_index,
                    candles=candles,
                )

                get_pnl = Grid_DP_Funcs.long_get_pnl

                grid_order_handler.check_stop_loss_hit(
                    check_sl_hit_bool=Grid_SL_Funcs.long_check_sl_hit_bool,
                    current_candle=current_candle,
                )

                grid_order_handler.check_liq_hit(
                    check_liq_hit_bool=Grid_Lev_Funcs.long_check_liq_hit_bool,
                    current_candle=current_candle,
                )

            elif position_size_usd < 0:

                current_candle = grid_order_handler.helpers.get_current_candle(
                    bar_index=bar_index,
                    candles=candles,
                )

                get_pnl = Grid_DP_Funcs.short_get_pnl

                grid_order_handler.check_stop_loss_hit(
                    check_sl_hit_bool=Grid_SL_Funcs.short_check_sl_hit_bool,
                    current_candle=current_candle,
                )

                grid_order_handler.check_liq_hit(
                    current_candle=current_candle,
                    check_liq_hit_bool=Grid_Lev_Funcs.short_check_liq_hit_bool,
                )

        except DecreasePosition as dp:
            (
                equity,
                fees_paid,
                realized_pnl,
            ) = grid_order_handler.calculate_decrease_position(
                cur_datetime=candles.candle_open_datetimes[bar_index],
                exit_fee=grid_order_handler.market_fee_pct,
                exit_price=dp.exit_price,
                exit_size_asset=abs(grid_order_handler.position_size_asset),
                equity=grid_order_handler.equity,
                get_pnl=get_pnl,
                order_status=dp.order_status,
            )

            grid_order_handler.helpers.fill_order_records(
                bar_index=bar_index,
                equity=equity,
                exit_price=dp.exit_price,
                fees_paid=fees_paid,
                liq_price=dp.liq_price,
                order_records=order_records[or_filled],
                order_status=dp.order_status,
                realized_pnl=realized_pnl,
                set_idx=0,
                sl_price=dp.sl_price,
                timestamp=current_candle.open_timestamp,
            )

            or_filled += 1
            position_size_usd = 0.0

            logger.debug(f"Filled decrease postiion order records for {OrderStatus._fields[dp.order_status]}")
            logger.debug("reset order variables")
        try:
            if low_prices[bar_index] <= buy_order:
                logger.debug("buy order hit")

                order_size_usd = equity * pct_account
                temp_pos_size_usd = position_size_usd + order_size_usd

                buy_signals[bar_index] = buy_order
                if position_size_usd >= 0:
                    # either entering or adding to a long position
                    logger.debug("either entering or adding to a long position adding to a long position")

                    get_bankruptcy_price = Grid_Lev_Funcs.long_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.long_get_liq_price

                    average_entry = grid_order_handler.calculate_average_entry(
                        entry_price=buy_order,
                        order_size_usd=order_size_usd,
                    )

                    ae_buy_array[bar_index] = average_entry
                    entry_price = buy_order
                    entry_size_asset = order_size_usd / average_entry
                    entry_size_usd = order_size_usd
                    equity = grid_order_handler.equity
                    order_status = OrderStatus.EntryFilled

                    fees_paid = np.nan
                    realized_pnl = np.nan
                    exit_price = np.nan
                    (
                        available_balance,
                        cash_borrowed,
                        cash_used,
                        liq_price,
                    ) = grid_order_handler.calculate_liquidation_price(
                        average_entry=average_entry,
                        equity=grid_order_handler.equity,
                        get_bankruptcy_price=get_bankruptcy_price,
                        get_liq_price=get_liq_price,
                        leverage=leverage,
                        position_size_usd=abs(temp_pos_size_usd),
                    )

                elif temp_pos_size_usd > 0:
                    # switch from short to long
                    logger.debug("switching from short to long")

                    get_bankruptcy_price = Grid_Lev_Funcs.long_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.long_get_liq_price

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=abs(position_size_usd) / average_entry,
                        equity=equity,
                        get_pnl=Grid_DP_Funcs.short_get_pnl,
                        order_status=OrderStatus.TakeProfitFilled,
                    )

                    average_entry = buy_order
                    entry_price = buy_order
                    entry_size_asset = order_size_usd / average_entry
                    entry_size_usd = order_size_usd
                    exit_price = buy_order
                    order_status = OrderStatus.TakeProfitFilled

                    ae_buy_array[bar_index] = average_entry
                    (
                        available_balance,
                        cash_borrowed,
                        cash_used,
                        liq_price,
                    ) = grid_order_handler.calculate_liquidation_price(
                        average_entry=average_entry,
                        equity=grid_order_handler.equity,
                        get_bankruptcy_price=get_bankruptcy_price,
                        get_liq_price=get_liq_price,
                        leverage=leverage,
                        position_size_usd=abs(temp_pos_size_usd),
                    )

                elif temp_pos_size_usd < 0 and position_size_usd < 0:
                    # tp on short
                    logger.debug("tp on short")

                    get_bankruptcy_price = Grid_Lev_Funcs.short_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.short_get_liq_price

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=order_size_usd / average_entry,
                        equity=equity,
                        get_pnl=Grid_DP_Funcs.short_get_pnl,
                        order_status=OrderStatus.TakeProfitFilled,
                    )
                    average_entry = grid_order_handler.average_entry
                    entry_price = buy_order
                    entry_size_asset = order_size_usd / average_entry
                    entry_size_usd = order_size_usd
                    exit_price = buy_order
                    order_status = OrderStatus.TakeProfitFilled

                    (
                        available_balance,
                        cash_borrowed,
                        cash_used,
                        liq_price,
                    ) = grid_order_handler.calculate_liquidation_price(
                        average_entry=average_entry,
                        equity=grid_order_handler.equity,
                        get_bankruptcy_price=get_bankruptcy_price,
                        get_liq_price=get_liq_price,
                        leverage=leverage,
                        position_size_usd=abs(temp_pos_size_usd),
                    )

                else:
                    # closing short position
                    logger.debug("Closing short position")
                    
                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=buy_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=order_size_usd / average_entry,
                        equity=equity,
                        get_pnl=Grid_DP_Funcs.short_get_pnl,
                        order_status=OrderStatus.TakeProfitFilled,
                    )
                    
                    average_entry = 0
                    entry_price = buy_order
                    entry_size_asset = order_size_usd / average_entry
                    entry_size_usd = order_size_usd
                    exit_price = buy_order

                position_size_usd = temp_pos_size_usd
                grid_order_handler.set_grid_variables(
                    available_balance=available_balance,
                    average_entry=average_entry,
                    cash_borrowed=cash_borrowed,
                    cash_used=cash_used,
                    entry_price=entry_price,
                    entry_size_asset=entry_size_asset,
                    entry_size_usd=entry_size_usd,
                    equity=equity,
                    exit_price=exit_price,
                    fees_paid=fees_paid,
                    leverage=leverage,
                    liq_price=liq_price,
                    order_status=order_status,
                    position_size_asset=position_size_usd / average_entry,
                    position_size_usd=position_size_usd,
                    total_possible_loss=np.nan,
                    realized_pnl=np.nan,
                    sl_pct=np.nan,
                    sl_price=np.nan,
                    total_trades=np.nan,
                    tp_pct=np.nan,
                    tp_price=np.nan,
                )

                grid_order_handler.helpers.fill_order_records(
                    bar_index=bar_index,
                    equity=equity,
                    exit_price=exit_price,
                    fees_paid=fees_paid,
                    liq_price=liq_price,
                    order_records=order_records[or_filled],
                    order_status=order_status,
                    realized_pnl=realized_pnl,
                    set_idx=0,
                    timestamp=candles.candle_open_timestamps[bar_index],
                )

                or_filled += 1

                ps_array[bar_index] = position_size_usd
                buy_order = closing_prices[bar_index] - (closing_prices[bar_index] * price_pct)
                sell_order = closing_prices[bar_index] + (closing_prices[bar_index] * price_pct)

            elif high_prices[bar_index] >= sell_order:
                logger.debug("sell order hit")
                order_size_usd = equity * pct_account
                temp_pos_size_usd = position_size_usd + -order_size_usd

                sell_signals[bar_index] = sell_order

                if position_size_usd <= 0:
                    # adding to short position
                    logger.debug("adding to short position")

                    get_bankruptcy_price = Grid_Lev_Funcs.short_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.short_get_liq_price

                    average_entry = grid_order_handler.calculate_average_entry(
                        entry_price=sell_order,
                        order_size_usd=order_size_usd,
                    )
                    ae_buy_array[bar_index] = average_entry
                    entry_price = sell_order
                    entry_size_asset = order_size_usd / average_entry
                    entry_size_usd = order_size_usd
                    equity = grid_order_handler.equity
                    fees_paid = np.nan
                    realized_pnl = np.nan
                    exit_price = np.nan

                elif temp_pos_size_usd <= 0 and position_size_usd > 0:
                    # switching from long to short
                    logger.debug("switching from long to short")

                    get_bankruptcy_price = Grid_Lev_Funcs.short_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.short_get_liq_price

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=sell_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=abs(position_size_usd) / average_entry,
                        equity=equity,
                        get_pnl=Grid_DP_Funcs.long_get_pnl,
                        order_status=OrderStatus.TakeProfitFilled,
                    )

                    average_entry = sell_order
                    entry_price = sell_order
                    entry_size_asset = order_size_usd / average_entry
                    entry_size_usd = order_size_usd
                    exit_price = sell_order

                    ae_buy_array[bar_index] = average_entry

                elif temp_pos_size_usd > 0:
                    # tp on long
                    logger.debug("tp on long")

                    get_bankruptcy_price = Grid_Lev_Funcs.long_get_bankruptcy_price
                    get_liq_price = Grid_Lev_Funcs.long_get_liq_price

                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = grid_order_handler.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_price=sell_order,
                        exit_fee=grid_order_handler.limit_fee_pct,
                        exit_size_asset=order_size_usd / average_entry,
                        equity=equity,
                        get_pnl=Grid_DP_Funcs.long_get_pnl,
                        order_status=OrderStatus.TakeProfitFilled,
                    )
                    average_entry = grid_order_handler.average_entry
                    entry_price = np.nan
                    entry_size_asset = np.nan
                    entry_size_usd = np.nan
                    exit_price = sell_order

                position_size_usd = temp_pos_size_usd
                ps_array[bar_index] = position_size_usd
                buy_order = closing_prices[bar_index] - (closing_prices[bar_index] * price_pct)
                sell_order = closing_prices[bar_index] + (closing_prices[bar_index] * price_pct)

        except RejectedOrder:
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            raise Exception(e)

    return ps_array, ae_buy_array, ae_sell_array, pnl_array, buy_signals, sell_signals, order_records
