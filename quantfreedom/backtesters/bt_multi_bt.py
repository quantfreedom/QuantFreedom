from typing import Optional
import numpy as np
import pandas as pd
from logging import getLogger
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from quantfreedom.helpers.custom_logger import set_loggers
from quantfreedom.helpers.helper_funcs import get_qf_score, order_records_to_df, make_bt_df
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
    TrailingSLStrategyType,
)
from quantfreedom.helpers.utils import pretty_qf

logger = getLogger()


def run_df_backtest(
    candles: FootprintCandlesTuple,
    strategy: Strategy,
    threads: int,
    step_by: int = 1,
) -> pd.DataFrame:
    global strategy_result_records

    logger.disabled = True
    # logger.disabled = False
    # set_loggers(log_folder=strategy.log_folder)

    starting_equity = strategy.static_os_tuple.starting_equity

    order = OrderHandler(
        long_short=strategy.get_long_or_short(),
        static_os_tuple=strategy.static_os_tuple,
        exchange_settings_tuple=strategy.exchange_settings_tuple,
    )

    # Creating Settings Vars
    total_bars = candles.candle_open_timestamps.size
    step_by_settings = strategy.total_filtered_settings // step_by
    chunk_process = step_by_settings // threads

    print("Starting the backtest now ... and also here are some stats for your backtest.")

    # TODO total settings combinations to test is wrong because we need to take into account the filtering in creating dos tuple

    print("\n" + f"Total threads to use: {threads:,}")
    print(f"Total Dynamic Order settings: {strategy.total_dos:,}")
    print(f"Total indicator settings: {strategy.total_indicator_settings:,}")
    print(f"Total settings combinations: {strategy.total_dos * strategy.total_indicator_settings:,}")
    print(f"Total settings combinations after filtering: {strategy.total_filtered_settings:,}")
    print(f"Total settings combinations with step by: {step_by_settings:,}")
    print(f"Total settings combinations to process per chunk: {chunk_process:,}")

    total_candles = strategy.total_filtered_settings * total_bars
    chunks = total_candles // threads
    candle_chunks = chunks // step_by
    print("\n" + f"Total candles: {total_bars:,}")
    print(f"Total candles to test: {total_candles:,}")
    print(f"Total candle chunks to be processed at the same time: {chunks:,}")
    print(f"Total candle chunks with step by: {candle_chunks:,}")

    num_array_columns = 9 + len(strategy.og_dos_tuple._fields) + len(strategy.og_ind_set_tuple._fields)
    arr_shape = (1000000, num_array_columns)
    # arr_shape = (strategy.total_filtered_settings, num_array_columns)
    strategy_result_records = np.full(arr_shape, np.nan)

    range_multiplier = strategy.total_filtered_settings / threads
    p = Pool()
    results = []
    for thread in range(threads):
        range_start = int(thread * range_multiplier)
        range_end = int((thread + 1) * range_multiplier)
        rec_arr_shape = (range_end - range_start, num_array_columns)
        record_results = np.full(rec_arr_shape, np.nan)

        r: ApplyResult = p.apply_async(
            func=multiprocess_backtest,
            args=[
                candles,
                order,
                range_end,
                range_start,
                record_results,
                starting_equity,
                strategy,
                total_bars,
                step_by,
            ],
            callback=proc_results,
            error_callback=handler,
        )
        results.append(r)

    print("\n" + "looping through results")
    for idx, r in enumerate(results):
        print(idx, end=", ")
        r.wait()

    print("\n" + "closing")
    p.close()
    print("joining")
    p.join()
    print("creating datafram")

    backtest_df = make_bt_df(
        strategy=strategy,
        strategy_result_records=strategy_result_records,
    )

    return backtest_df


def multiprocess_backtest(
    candles: FootprintCandlesTuple,
    order: OrderHandler,
    range_end: int,
    range_start: int,
    record_results: np.ndarray,
    starting_equity: float,
    strategy: Strategy,
    total_bars: int,
    step_by: int,
):
    logger.disabled = True
    rec_idx = 0
    for set_idx in range(range_start, range_end, step_by):
        logger.debug(set_idx)

        strategy.set_cur_ind_set_tuple(
            set_idx=set_idx,
        )

        strategy.set_cur_dos_tuple(
            set_idx=set_idx,
        )

        strategy.set_entries_exits_array(
            candles=candles,
        )

        pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
        filled_pnl_counter = 0
        total_fees_paid = 0

        order.update_class_dos(
            dynamic_order_settings=strategy.cur_dos_tuple,
        )
        order.set_order_variables(
            equity=starting_equity,
        )

        logger.debug("Set order variables, class dos and pnl array")

        starting_bar = strategy.static_os_tuple.starting_bar - 1

        for bar_index in range(starting_bar, total_bars):
            logger.debug("\n\n")
            logger.debug(
                f"set_idx= {strategy.cur_dos_tuple.settings_index} loop_idx = {set_idx} bar_idx= {bar_index} datetime= {candles.candle_open_datetimes[bar_index]}"
            )

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

                    logger.debug("Checking to move trailing stop loss")
                    tsl_price, tsl_pct = order.check_move_tsl(
                        current_candle=current_candle,
                    )
                    if tsl_price:
                        order.sl_pct = tsl_pct
                        order.sl_price = tsl_price

                except DecreasePosition as e:
                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = order.calculate_decrease_position(
                        cur_datetime=candles.candle_open_datetimes[bar_index],
                        exit_fee_pct=e.exit_fee_pct,
                        exit_price=e.exit_price,
                        order_status=e.order_status,
                        market_fee_pct=strategy.exchange_settings_tuple.market_fee_pct,
                        equity=order.equity,
                    )

                    pnl_array[filled_pnl_counter] = realized_pnl
                    filled_pnl_counter += 1
                    total_fees_paid += fees_paid
                    logger.debug("Filled pnl array and updated total fees paid")

                    order.set_order_variables(equity=equity)
                    logger.debug("reset order variables")

                except Exception as e:
                    logger.error(f"Exception checking sl liq tp and move -> {e}")
                    raise Exception(f"Exception checking sl liq tp  and move -> {e}")
            else:
                logger.debug("Not in a pos so not checking SL Liq or TP")

            logger.debug("strategy evaluate")
            if strategy.entries[bar_index]:
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
                        position_size_asset=position_size_asset,
                        position_size_usd=position_size_usd,
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
                    logger.debug("filling order result")
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
                    logger.debug("We are in a position and filled the result")
                except RejectedOrder:
                    pass
                except Exception as e:
                    logger.error(f"Exception hit in eval strat -> {e}")
                    raise Exception(f"Exception hit in eval strat -> {e}")

        # Checking if gains
        gains_pct = round(((order.equity - starting_equity) / starting_equity) * 100, 2)
        wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
        total_trades_closed = wins_and_losses_array.size
        logger.debug(
            f"""
Results from backtest
set_idx={strategy.cur_dos_tuple.settings_index}
loop_idx = {set_idx}
Starting eq={starting_equity}
Ending eq={order.equity}
Gains pct={gains_pct}
total_trades={total_trades_closed}"""
        )
        if total_trades_closed > 0 and gains_pct > strategy.backtest_settings_tuple.gains_pct_filter:
            if wins_and_losses_array.size > strategy.backtest_settings_tuple.total_trade_filter:
                wins_and_losses_array_no_be = wins_and_losses_array[
                    (wins_and_losses_array < -0.009) | (wins_and_losses_array > 0.009)
                ]
                qf_score = get_qf_score(
                    gains_pct=gains_pct,
                    wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                )

                # Checking to the upside filter
                if qf_score > strategy.backtest_settings_tuple.qf_filter:
                    win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
                    wins = np.count_nonzero(win_loss)
                    losses = win_loss.size - wins
                    win_rate = round(wins / win_loss.size * 100, 2)

                    total_pnl = wins_and_losses_array.sum()
                    tuple_results = (
                        (
                            wins_and_losses_array.size,
                            wins,
                            losses,
                            gains_pct,
                            win_rate,
                            qf_score,
                            round(total_fees_paid, 2),
                            total_pnl,
                            order.equity,
                        )
                        + strategy.cur_dos_tuple
                        + strategy.cur_ind_set_tuple
                    )
                    record_results[rec_idx] = tuple_results
                    rec_idx += 1
        logger.debug(
            f"Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        )

    return range_start, range_end, record_results


def proc_results(
    results: tuple,
):
    start = results[0]
    end = results[1]
    arr = results[2]
    strategy_result_records[start:end] = arr


def handler(error):
    print(f"Error: {error}", flush=True)

