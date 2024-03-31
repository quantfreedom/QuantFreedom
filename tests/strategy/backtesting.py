import sys, os

sys.path.insert(0, os.path.abspath("E:\Coding\my_stuff"))
from my_keys import MufexKeys  # type: ignore
import numpy as np
from datetime import datetime

from strat import RSIRisingFalling
from quantfreedom.enums import CandleBodyType

from quantfreedom.enums import *
from quantfreedom.helper_funcs import dl_ex_candles

from quantfreedom.exchanges.mufex_exchange.mufex import Mufex
from multiprocessing import Pool, cpu_count
from time import perf_counter, sleep

import numpy as np
import pandas as pd
from logging import getLogger
from quantfreedom.custom_logger import set_loggers
from quantfreedom.helper_funcs import get_dos, get_qf_score, log_dynamic_order_settings
from quantfreedom.nb_funcs.nb_helper_funcs import order_records_to_df
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.plotting.plotting_base import plot_or_results
from quantfreedom.strategies.strategy import Strategy
from quantfreedom.enums import (
    BacktestSettings,
    CandleBodyType,
    DecreasePosition,
    DynamicOrderSettings,
    ExchangeSettings,
    OrderStatus,
    RejectedOrder,
    StaticOrderSettings,
    strat_df_array_dt,
    or_dt,
)
from quantfreedom.utils import pretty_qf

logger = getLogger("info")
logger.disabled = True


def multiprocess_backtest(
    backtest_settings_tuple: BacktestSettings,
    candles: np.array,
    exchange_settings_tuple: ExchangeSettings,
    order: OrderHandler,
    range_end: int,
    range_start: int,
    record_results: np.array,
    starting_equity: float,
    static_os_tuple: StaticOrderSettings,
    strategy: Strategy,
    total_bars: int,
):
    for set_idx in range(range_start, range_end):
        strategy.set_entries_exits_array(
            candles=candles,
            ind_set_index=set_idx,
        )
        strategy.log_indicator_settings(ind_set_index=set_idx)

        dynamic_order_settings = get_dos(
            dos_cart_arrays=strategy.dos_tuple,
            dos_index=set_idx,
        )
        log_dynamic_order_settings(
            dos_index=set_idx,
            dynamic_order_settings=dynamic_order_settings,
        )

        pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
        filled_pnl_counter = 0
        total_fees_paid = 0

        order.update_class_dos(dynamic_order_settings=dynamic_order_settings)
        order.set_order_variables(equity=starting_equity)

        logger.debug("Set order variables, class dos and pnl array")

        for bar_index in range(static_os_tuple.starting_bar - 1, total_bars):
            logger.info("\n\n")
            timestamp = pd.to_datetime(candles[bar_index, CandleBodyType.Timestamp], unit="ms")
            logger.info(f"set_idx= {set_idx} bar_idx= {bar_index} timestamp= {timestamp}")

            if order.position_size_usd > 0:
                try:
                    current_candle = candles[bar_index, :]
                    logger.debug("Checking stop loss hit")
                    order.check_stop_loss_hit(current_candle=current_candle)
                    logger.debug("Checking liq hit")
                    order.check_liq_hit(current_candle=current_candle)
                    logger.debug("Checking take profit hit")
                    order.check_take_profit_hit(
                        current_candle=current_candle,
                        exit_price=strategy.exit_prices[bar_index],
                    )

                    logger.debug("Checking to move stop to break even")
                    sl_to_be_price, sl_to_be_pct = order.check_move_sl_to_be(current_candle=current_candle)
                    if sl_to_be_price:
                        order.sl_pct = sl_to_be_pct
                        order.sl_price = sl_to_be_price

                    logger.debug("Checking to move trailing stop loss")
                    tsl_price, tsl_pct = order.check_move_tsl(current_candle=current_candle)
                    if tsl_price:
                        order.sl_pct = tsl_pct
                        order.sl_price = tsl_price

                except DecreasePosition as e:
                    (
                        equity,
                        fees_paid,
                        realized_pnl,
                    ) = order.calculate_decrease_position(
                        exit_fee_pct=e.exit_fee_pct,
                        exit_price=e.exit_price,
                        order_status=e.order_status,
                        market_fee_pct=exchange_settings_tuple.market_fee_pct,
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
                        entry_price=candles[bar_index, CandleBodyType.Close],
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
                    logger.info("We are in a position and filled the result")
                except RejectedOrder:
                    pass
                except Exception as e:
                    logger.error(f"Exception hit in eval strat -> {e}")
                    raise Exception(f"Exception hit in eval strat -> {e}")

        # Checking if gains
        gains_pct = round(((order.equity - starting_equity) / starting_equity) * 100, 3)
        wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
        total_trades_closed = wins_and_losses_array.size
        logger.info(
            f"""
Results from backtest
set_idx={set_idx}
Starting eq={starting_equity}
Ending eq={order.equity}
Gains pct={gains_pct}
total_trades={total_trades_closed}"""
        )
        if total_trades_closed > 0 and gains_pct > backtest_settings_tuple.gains_pct_filter:
            if wins_and_losses_array.size > backtest_settings_tuple.total_trade_filter:
                wins_and_losses_array_no_be = wins_and_losses_array[
                    (wins_and_losses_array < -0.009) | (wins_and_losses_array > 0.009)
                ]
                qf_score = get_qf_score(
                    gains_pct=gains_pct,
                    wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                )

                # Checking to the upside filter
                if qf_score > backtest_settings_tuple.qf_filter:
                    win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
                    wins = np.count_nonzero(win_loss)
                    losses = win_loss.size - wins
                    win_rate = round(wins / win_loss.size * 100, 3)

                    total_pnl = wins_and_losses_array.sum()

                    record_results[set_idx]["set_idx"] = set_idx
                    record_results[set_idx]["total_trades"] = wins_and_losses_array.size
                    record_results[set_idx]["wins"] = wins
                    record_results[set_idx]["losses"] = losses
                    record_results[set_idx]["gains_pct"] = gains_pct
                    record_results[set_idx]["win_rate"] = win_rate
                    record_results[set_idx]["qf_score"] = qf_score
                    record_results[set_idx]["fees_paid"] = round(total_fees_paid, 3)
                    record_results[set_idx]["total_pnl"] = total_pnl
                    record_results[set_idx]["ending_eq"] = order.equity
        logger.info(
            f"Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        )
    return record_results, range_start, range_end


def run_df_backtest(
    backtest_settings_tuple: BacktestSettings,
    candles: np.array,
    exchange_settings_tuple: ExchangeSettings,
    static_os_tuple: StaticOrderSettings,
    strategy: Strategy,
    threads: int,
):
    start = perf_counter()
    global strategy_result_records

    logger.disabled = True
    # logger.disabled = False
    # set_loggers(log_folder=strategy.log_folder)

    starting_equity = static_os_tuple.starting_equity

    order = OrderHandler(
        long_short=strategy.long_short,
        static_os_tuple=static_os_tuple,
        exchange_settings_tuple=exchange_settings_tuple,
    )

    # Creating Settings Vars

    total_bars = candles.shape[0]

    total_settings = strategy.total_order_settings * strategy.total_indicator_settings

    # logger.infoing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")
    print(f"Total indicator settings to test: {strategy.total_indicator_settings:,}")
    print(f"Total order settings to test: {strategy.total_order_settings:,}")
    print(f"Total combinations of settings to test: {total_settings:,}")
    print(f"Total candles: {total_bars:,}")
    print(f"Total candles to test: {total_settings * total_bars:,}")

    logger.info("Starting the backtest now ... and also here are some stats for your backtest.\n")
    logger.info(f"Total indicator settings to test: {strategy.total_indicator_settings:,}")
    logger.info(f"Total order settings to test: {strategy.total_order_settings:,}")
    logger.info(f"Total combinations of settings to test: {total_settings:,}")
    logger.info(f"Total candles: {total_bars:,}")
    logger.info(f"Total candles to test: {total_settings * total_bars:,}")

    record_results = np.full(
        shape=total_settings,
        fill_value=np.nan,
        dtype=strat_df_array_dt,
    )
    strategy_result_records = record_results.copy()

    range_multiplier = total_settings / threads
    p = Pool()
    results = []
    for thread in range(threads):
        range_start = int(thread * range_multiplier)
        range_end = int((thread + 1) * range_multiplier)
        record_results = np.full(
            shape=range_end - range_start,
            fill_value=np.nan,
            dtype=strat_df_array_dt,
        )

        r = p.apply_async(
            func=multiprocess_backtest,
            args=[
                backtest_settings_tuple,
                candles,
                exchange_settings_tuple,
                order,
                range_end,
                range_start,
                # record_results[range_start:range_end],
                record_results,
                starting_equity,
                static_os_tuple,
                strategy,
                total_bars,
            ],
            callback=proc_results,
            error_callback=handler,
        )
        results.append(r)
    for r in results:
        r.wait()

    p.close()
    p.join()
    end = perf_counter()
    print(f"Main took: ", end - start)
    for result in results:
        print(result._value[0])
    return results


def proc_results(results):
    # print("Results: ", results)
    begin = results[1]
    length = results[2] - results[1]
    for i in range(length):
        strategy_result_records[begin + i] = results[0][i - length]


# error callback function
def handler(error):
    print(f"Error: {error}", flush=True)


if __name__ == "__main__":
    mufex_main = Mufex(
        api_key=MufexKeys.mainnet_neo_api_key,
        secret_key=MufexKeys.mainnet_neo_secret_key,
        use_test_net=False,
    )
    symbol = "BTCUSDT"

    np.set_printoptions(formatter={"float_kind": "{:0.2f}".format})

    candles = dl_ex_candles(
        exchange="mufex",
        symbol="BTCUSDT",
        timeframe="5m",
        candles_to_dl=3000,
    )

    backtest_settings_tuple = BacktestSettings()

    dos_tuple = DynamicOrderSettings(
        account_pct_risk_per_trade=np.array([3]),
        max_trades=np.array([4]),
        risk_reward=np.array([2, 5]),
        sl_based_on_add_pct=np.array([0.1]),
        sl_based_on_lookback=np.array([20]),
        sl_bcb_type=np.array([CandleBodyType.Low]),
        sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
        sl_to_be_when_pct=np.array([0]),
        trail_sl_bcb_type=np.array([CandleBodyType.Low]),
        trail_sl_by_pct=np.array([0.5, 1.0]),
        trail_sl_when_pct=np.array([1, 2]),
    )

    exchange_settings_tuple = mufex_main.set_and_get_exchange_settings_tuple(
        leverage_mode=LeverageModeType.Isolated,
        position_mode=PositionModeType.HedgeMode,
        symbol=symbol,
    )

    static_os_tuple = StaticOrderSettings(
        increase_position_type=IncreasePositionType.RiskPctAccountEntrySize,
        leverage_strategy_type=LeverageStrategyType.Dynamic,
        pg_min_max_sl_bcb="min",
        sl_strategy_type=StopLossStrategyType.SLBasedOnCandleBody,
        sl_to_be_bool=False,
        starting_bar=50,
        starting_equity=1000.0,
        static_leverage=None,
        tp_fee_type="limit",
        tp_strategy_type=TakeProfitStrategyType.RiskReward,
        trail_sl_bool=True,
        z_or_e_type=None,
    )

    long_strat = RSIRisingFalling(
        long_short="long",
        dos_tuple=dos_tuple,
        rsi_length=np.array([14]),
        rsi_is_below=np.array([40, 60, 80]),
    )

    backtest_results = run_df_backtest(
        backtest_settings_tuple=backtest_settings_tuple,
        candles=candles,
        exchange_settings_tuple=exchange_settings_tuple,
        static_os_tuple=static_os_tuple,
        strategy=long_strat,
        threads=4,
    )

    print(backtest_results)

    # backtest_results.sort_values(by=["qf_score"], ascending=False).head(10)

    # order_records_df = or_backtest(
    #     backtest_settings_tuple=backtest_settings_tuple,
    #     candles=candles,
    #     dos_arrays=dos_arrays,
    #     exchange_settings_tuple=exchange_settings_tuple,
    #     static_os_tuple=static_os_tuple,
    #     strategy=long_strat,
    #     ind_set_index=2,
    #     dos_index=0,
    #     plot_results=False,
    #     logger_bool=True,
    # )

    # order_records_df
