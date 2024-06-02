import numpy as np
from logging import getLogger
from quantfreedom.helpers.custom_logger import set_loggers
from quantfreedom.helpers.helper_funcs import order_records_to_df
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.core.plotting_base import plot_or_results
from quantfreedom.core.strategy import Strategy
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    RejectedOrder,
    or_dt,
)
from quantfreedom.helpers.utils import pretty_qf

logger = getLogger()


def live_backtest(
    candles: FootprintCandlesTuple,
    disable_logger: bool,
    disable_plot: bool,
    strategy: Strategy,
    set_idx: int,
    logger_level: str = "INFO",
):
    if disable_logger:
        set_loggers(
            disable_logger=disable_logger,
        )
    else:
        set_loggers(
            disable_logger=disable_logger,
            log_path=strategy.log_folder,
            logger_level=logger_level,
        )

    starting_equity = strategy.static_os_tuple.starting_equity

    order = OrderHandler(
        exchange_settings_tuple=strategy.exchange_settings_tuple,
        long_short=strategy.long_short,
        static_os_tuple=strategy.static_os_tuple,
    )

    set_idx = strategy.get_settings_index(
        set_idx=set_idx,
    )

    strategy.set_cur_ind_tuple(
        set_idx=set_idx,
    )
    strategy.set_entries_exits_array(
        candles=candles,
    )
    strategy.set_cur_dos_tuple(set_idx=set_idx)

    order.update_class_dos(dynamic_order_settings=strategy.cur_dos_tuple)
    order.set_order_variables(equity=starting_equity)

    total_bars = candles.candle_open_timestamps.size

    or_filled = 0
    order_records = np.empty(shape=int(total_bars / 3), dtype=or_dt)

    loop_start = strategy.static_os_tuple.starting_bar - 1
    for bar_index in range(loop_start, total_bars):
        logger.debug("\n\n")
        datetime = candles.candle_open_datetimes[bar_index]
        logger.debug(f"set_idx= {set_idx} bar_idx= {bar_index} datetime= {datetime}")

        if order.position_size_usd > 0:
            try:
                current_candle = CurrentFootprintCandleTuple(
                    open_timestamp=candles.candle_open_timestamps[bar_index],
                    open_price=candles.candle_open_prices[bar_index],
                    high_price=candles.candle_high_prices[bar_index],
                    low_price=candles.candle_low_prices[bar_index],
                    close_price=candles.candle_close_prices[bar_index],
                )
                logger.debug("Checking stop loss hit")
                order.check_stop_loss_hit(
                    current_candle=current_candle,
                )
                logger.debug("Checking liq hit")
                order.check_liq_hit(
                    current_candle=current_candle,
                )
                logger.debug("Checking take profit hit")
                order.check_take_profit_hit(
                    current_candle=current_candle,
                    exit_price=strategy.exit_prices[bar_index],
                )

                logger.debug("Checking to move stop to break even")
                sl_to_be_price, sl_to_be_pct = order.check_move_sl_to_be(
                    current_candle=current_candle,
                )
                if sl_to_be_price:
                    order.sl_pct = sl_to_be_pct
                    order.sl_price = sl_to_be_price
                    logger.debug(f"Filling order for move sl to be")
                    order.fill_or_exit_move(
                        bar_index=bar_index,
                        set_idx=set_idx,
                        order_records=order_records[or_filled],
                        order_status=OrderStatus.MovedSLToBE,
                        timestamp=current_candle.open_timestamp,
                        sl_price=sl_to_be_price,
                        sl_pct=sl_to_be_pct,
                    )
                    or_filled += 1
                    logger.debug(f"Filled sl to be order records")

                logger.debug("Checking to move trailing stop loss")
                tsl_price, tsl_pct = order.check_move_tsl(
                    current_candle=current_candle,
                )
                if tsl_price:
                    order.sl_pct = tsl_pct
                    order.sl_price = tsl_price
                    logger.debug(f"Filling order for tsl")

                    order.fill_or_exit_move(
                        bar_index=bar_index,
                        set_idx=set_idx,
                        order_records=order_records[or_filled],
                        order_status=OrderStatus.MovedTSL,
                        timestamp=current_candle.open_timestamp,
                        sl_pct=tsl_pct,
                        sl_price=tsl_price,
                    )
                    or_filled += 1
                    logger.debug(f"Filled move tsl order records")

            except DecreasePosition as e:
                (
                    equity,
                    fees_paid,
                    realized_pnl,
                ) = order.calculate_decrease_position(
                    cur_datetime=current_candle.open_timestamp,
                    exit_fee_pct=e.exit_fee_pct,
                    exit_price=e.exit_price,
                    order_status=e.order_status,
                    market_fee_pct=strategy.exchange_settings_tuple.market_fee_pct,
                    equity=order.equity,
                )
                logger.debug(f"Filling or for decrease postiion {OrderStatus._fields[e.order_status]}")
                order.fill_or_exit_move(
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

                order.set_order_variables(equity=equity)
                logger.debug("reset order variables")

            except Exception as e:
                logger.error(f"Exception checking sl liq tp and move -> {e}")
                raise Exception(f"Exception checking sl liq tp and move -> {e}")
        else:
            logger.debug("Not in a pos so not checking SL Liq or TP")

        logger.debug("strategy evaluate")

        beg = bar_index - loop_start
        end = bar_index + 1

        result = strategy.live_bt(
            bar_index=bar_index,
            beg=beg,
            candles=candles,
            end=end,
        )

        if result:
            strategy.entry_message(bar_index=bar_index)
            try:
                logger.debug("calculate_stop_loss")
                sl_price = order.calculate_stop_loss(
                    bar_index=bar_index,
                    candles=candles,
                )

                logger.debug("calculate_increase_position")
                (
                    average_entry,
                    entry_price,
                    entry_size_asset,
                    entry_size_usd,
                    position_size_asset,
                    position_size_usd,
                    total_possible_loss,
                    total_trades,
                    sl_pct,
                ) = order.calculate_increase_position(
                    average_entry=order.average_entry,
                    entry_price=candles.candle_close_prices[bar_index],
                    equity=order.equity,
                    position_size_asset=order.position_size_asset,
                    position_size_usd=order.position_size_usd,
                    sl_price=sl_price,
                    total_trades=order.total_trades,
                )

                logger.debug("calculate_leverage")
                (
                    available_balance,
                    cash_borrowed,
                    cash_used,
                    leverage,
                    liq_price,
                ) = order.calculate_leverage(
                    available_balance=order.available_balance,
                    average_entry=average_entry,
                    cash_borrowed=order.cash_borrowed,
                    cash_used=order.cash_used,
                    position_size_usd=position_size_usd,
                    position_size_asset=position_size_asset,
                    sl_price=sl_price,
                )

                logger.debug("calculate_take_profit")
                (
                    can_move_sl_to_be,
                    tp_price,
                    tp_pct,
                ) = order.calculate_take_profit(
                    average_entry=average_entry,
                    position_size_usd=position_size_usd,
                    total_possible_loss=total_possible_loss,
                )

                logger.debug("calculate_take_profit")
                order.fill_order_result(
                    available_balance=available_balance,
                    average_entry=average_entry,
                    can_move_sl_to_be=can_move_sl_to_be,
                    cash_borrowed=cash_borrowed,
                    cash_used=cash_used,
                    entry_price=entry_price,
                    entry_size_asset=entry_size_asset,
                    entry_size_usd=entry_size_usd,
                    equity=order.equity,
                    exit_price=np.nan,
                    fees_paid=np.nan,
                    leverage=leverage,
                    liq_price=liq_price,
                    order_status=OrderStatus.EntryFilled,
                    position_size_asset=position_size_asset,
                    position_size_usd=position_size_usd,
                    total_possible_loss=total_possible_loss,
                    realized_pnl=np.nan,
                    sl_pct=sl_pct,
                    sl_price=sl_price,
                    total_trades=total_trades,
                    tp_pct=tp_pct,
                    tp_price=tp_price,
                )
                logger.debug("filling entry order records")
                order.fill_or_entry(
                    bar_index=bar_index + 1,
                    set_idx=set_idx,
                    order_records=order_records[or_filled],
                    timestamp=candles.candle_open_timestamps[bar_index + 1],
                )
                or_filled += 1
                logger.info("We are in a position and filled the result")
            except RejectedOrder:
                pass
            except Exception as e:
                if bar_index + 1 >= candles.candle_open_timestamps.size:
                    raise Exception(f"Exception hit in eval strat -> {e}")
                    pass
                else:
                    logger.error(f"Exception hit in eval strat -> {e}")
                    raise Exception(f"Exception hit in eval strat -> {e}")
    order_records_df = order_records_to_df(order_records[:or_filled])
    pretty_qf(strategy.cur_dos_tuple)
    pretty_qf(strategy.cur_ind_set_tuple)
    if not disable_plot:
        strategy.plot_signals(
            candles=candles,
        )
        plot_or_results(
            candles=candles,
            order_records_df=order_records_df,
        )
    return order_records_df
