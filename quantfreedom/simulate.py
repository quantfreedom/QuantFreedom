import numpy as np
import pandas as pd
from logging import getLogger
from quantfreedom.custom_logger import set_loggers
from quantfreedom.helper_funcs import dos_cart_product, get_dos, get_qf_score, log_dynamic_order_settings
from quantfreedom.nb_funcs.nb_helper_funcs import order_records_to_df
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.plotting.plotting_base import plot_or_results
from quantfreedom.strategies.strategy import Strategy
from quantfreedom.enums import (
    BacktestSettings,
    CandleBodyType,
    DecreasePosition,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    OrderStatus,
    RejectedOrder,
    StaticOrderSettings,
    strat_df_array_dt,
    or_dt,
)
from quantfreedom.utils import pretty_qf

logger = getLogger("info")


def run_df_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    logger_bool: bool,
    static_os: StaticOrderSettings,
    strategy: Strategy,
):
    if logger_bool == False:
        logger.disabled = True
    else:
        logger.disabled = False
        set_loggers()

    starting_equity = static_os.starting_equity

    dos_cart_arrays = dos_cart_product(
        dos_arrays=dos_arrays,
    )

    order = OrderHandler(
        long_short=strategy.long_short,
        static_os=static_os,
        exchange_settings=exchange_settings,
    )

    # Creating Settings Vars
    total_order_settings = dos_cart_arrays[0].size

    total_indicator_settings = strategy.indicator_settings_arrays[0].size

    total_bars = candles.shape[0]

    # logger.infoing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings to test: {total_order_settings:,}")
    print(f"Total combinations of settings to test: {total_indicator_settings * total_order_settings:,}")
    print(f"Total candles: {total_bars:,}")
    print(f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}")

    logger.info("Starting the backtest now ... and also here are some stats for your backtest.\n")
    logger.info(f"Total indicator settings to test: {total_indicator_settings:,}")
    logger.info(f"Total order settings to test: {total_order_settings:,}")
    logger.info(f"Total combinations of settings to test: {total_indicator_settings * total_order_settings:,}")
    logger.info(f"Total candles: {total_bars:,}")
    logger.info(f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}")

    strategy_result_records = np.empty(
        backtest_settings.record_size,
        dtype=strat_df_array_dt,
    )
    result_records_filled = 0

    for ind_set_index in range(total_indicator_settings):
        strategy.set_entries_exits_array(
            candles=candles,
            ind_set_index=ind_set_index,
        )

        for dos_index in range(total_order_settings):
            strategy.log_indicator_settings(ind_set_index=ind_set_index)
            dynamic_order_settings = get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )
            log_dynamic_order_settings(
                dynamic_order_settings=dynamic_order_settings,
                dos_index=dos_index,
            )

            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0
            total_fees_paid = 0

            order.update_class_dos(dynamic_order_settings=dynamic_order_settings)
            order.set_order_variables(equity=starting_equity)

            logger.debug("Set order variables, class dos and pnl array")

            for bar_index in range(static_os.starting_bar - 1, total_bars):
                logger.info("\n\n")
                timestamp = pd.to_datetime(candles[bar_index, CandleBodyType.Timestamp], unit="ms")
                logger.info(
                    f"ind_idx= {ind_set_index} dos_idx= {dos_index} bar_idx= {bar_index} timestamp= {timestamp}"
                )

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
                            market_fee_pct=exchange_settings.market_fee_pct,
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
                        # raise Exception(f"Exception checking sl liq tp  and move -> {e}")
                        pass
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

                        logger.debug("calculate_increase_posotion")
                        (
                            average_entry,
                            entry_price,
                            entry_size_asset,
                            entry_size_usd,
                            position_size_asset,
                            position_size_usd,
                            possible_loss,
                            total_trades,
                            sl_pct,
                        ) = order.calculate_increase_posotion(
                            average_entry=order.average_entry,
                            entry_price=candles[bar_index, CandleBodyType.Close],
                            equity=order.equity,
                            position_size_asset=order.position_size_asset,
                            position_size_usd=order.position_size_usd,
                            possible_loss=order.possible_loss,
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
                            possible_loss=possible_loss,
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
                            possible_loss=possible_loss,
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
                        # raise Exception(f"Exception hit in eval strat -> {e}")
                        pass

            # Checking if gains
            gains_pct = round(((order.equity - starting_equity) / starting_equity) * 100, 3)
            wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
            total_trades_closed = wins_and_losses_array.size
            logger.info(
                f"Results from backtest\
                \nind_set_index={ind_set_index}\
                \ndos_index={dos_index}\
                \nStarting eq={starting_equity}\
                \nEnding eq={order.equity}\
                \nGains pct={gains_pct}\
                \ntotal_trades={total_trades_closed}"
            )
            if total_trades_closed > 0 and gains_pct > backtest_settings.gains_pct_filter:
                if wins_and_losses_array.size > backtest_settings.total_trade_filter:
                    wins_and_losses_array_no_be = wins_and_losses_array[
                        (wins_and_losses_array < -0.009) | (wins_and_losses_array > 0.009)
                    ]
                    qf_score = get_qf_score(
                        gains_pct=gains_pct,
                        wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                    )

                    # Checking to the upside filter
                    if qf_score > backtest_settings.qf_filter:
                        win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
                        wins = np.count_nonzero(win_loss)
                        losses = win_loss.size - wins
                        win_rate = round(wins / win_loss.size * 100, 3)

                        total_pnl = wins_and_losses_array.sum()

                        # strat array
                        record = strategy_result_records[result_records_filled]

                        record["ind_set_idx"] = ind_set_index
                        record["dos_index"] = dos_index
                        record["total_trades"] = wins_and_losses_array.size
                        record["wins"] = wins
                        record["losses"] = losses
                        record["gains_pct"] = gains_pct
                        record["win_rate"] = win_rate
                        record["qf_score"] = qf_score
                        record["fees_paid"] = round(total_fees_paid, 3)
                        record["total_pnl"] = total_pnl
                        record["ending_eq"] = order.equity

                        result_records_filled += 1
            logger.info(
                f"Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            )
    return pd.DataFrame(strategy_result_records[:result_records_filled])


def or_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    logger_bool: bool,
    static_os: StaticOrderSettings,
    strategy: Strategy,
    dos_index: int,
    ind_set_index: int,
    plot_results: bool = False,
):
    if logger_bool == False:
        logger.disabled = True
    else:
        logger.disabled = False
        set_loggers()

    starting_equity = static_os.starting_equity

    dos_cart_arrays = dos_cart_product(
        dos_arrays=dos_arrays,
    )

    order = OrderHandler(
        static_os=static_os,
        exchange_settings=exchange_settings,
        long_short=strategy.long_short,
    )

    strategy.set_entries_exits_array(
        candles=candles,
        ind_set_index=ind_set_index,
    )
    strategy.log_indicator_settings(ind_set_index=ind_set_index)

    dynamic_order_settings = get_dos(
        dos_cart_arrays=dos_cart_arrays,
        dos_index=dos_index,
    )
    log_dynamic_order_settings(
        dynamic_order_settings=dynamic_order_settings,
        dos_index=dos_arrays,
    )

    order.update_class_dos(dynamic_order_settings=dynamic_order_settings)
    order.set_order_variables(equity=starting_equity)

    total_bars = candles.shape[0]

    or_filled = 0
    order_records = np.empty(shape=int(total_bars / 3), dtype=or_dt)

    for bar_index in range(static_os.starting_bar - 1, total_bars):
        logger.info("\n\n")
        pd_timestamp = pd.to_datetime(candles[bar_index, CandleBodyType.Timestamp], unit="ms")
        logger.info(f"ind_idx= {ind_set_index} dos_idx= {dos_index} bar_idx= {bar_index} timestamp= {pd_timestamp}")

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
                    logger.debug(f"Filling order for move sl to be")
                    order.fill_or_exit_move(
                        bar_index=bar_index,
                        dos_index=dos_index,
                        ind_set_index=ind_set_index,
                        order_records=order_records[or_filled],
                        order_status=OrderStatus.MovedSLToBE,
                        timestamp=current_candle[CandleBodyType.Timestamp],
                        sl_price=sl_to_be_price,
                        sl_pct=sl_to_be_pct,
                    )
                    or_filled += 1
                    logger.debug(f"Filled sl to be order records")
                logger.debug("Checking to move trailing stop loss")
                tsl_price, tsl_pct = order.check_move_tsl(current_candle=current_candle)
                if tsl_price:
                    order.sl_pct = tsl_pct
                    order.sl_price = tsl_price
                    logger.debug(f"Filling order for tsl")
                    order.fill_or_exit_move(
                        bar_index=bar_index,
                        dos_index=dos_index,
                        ind_set_index=ind_set_index,
                        order_records=order_records[or_filled],
                        order_status=OrderStatus.MovedTSL,
                        timestamp=current_candle[CandleBodyType.Timestamp],
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
                    exit_fee_pct=e.exit_fee_pct,
                    exit_price=e.exit_price,
                    order_status=e.order_status,
                    market_fee_pct=exchange_settings.market_fee_pct,
                    equity=order.equity,
                )
                logger.debug(f"Filling or for decrease postiion {OrderStatus._fields[e.order_status]}")
                order.fill_or_exit_move(
                    bar_index=bar_index,
                    dos_index=dos_index,
                    ind_set_index=ind_set_index,
                    order_records=order_records[or_filled],
                    order_status=e.order_status,
                    timestamp=current_candle[CandleBodyType.Timestamp],
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
        if strategy.entries[bar_index]:
            strategy.entry_message(bar_index=bar_index)
            try:
                logger.debug("calculate_stop_loss")
                sl_price = order.calculate_stop_loss(
                    bar_index=bar_index,
                    candles=candles,
                )

                logger.debug("calculate_increase_posotion")
                (
                    average_entry,
                    entry_price,
                    entry_size_asset,
                    entry_size_usd,
                    position_size_asset,
                    position_size_usd,
                    possible_loss,
                    total_trades,
                    sl_pct,
                ) = order.calculate_increase_posotion(
                    average_entry=order.average_entry,
                    entry_price=candles[bar_index, CandleBodyType.Close],
                    equity=order.equity,
                    position_size_asset=order.position_size_asset,
                    position_size_usd=order.position_size_usd,
                    possible_loss=order.possible_loss,
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
                    possible_loss=possible_loss,
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
                    possible_loss=possible_loss,
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
                    dos_index=dos_index,
                    ind_set_index=ind_set_index,
                    order_records=order_records[or_filled],
                    timestamp=candles[bar_index + 1, CandleBodyType.Timestamp],
                )
                or_filled += 1
                logger.info("We are in a position and filled the result")
            except RejectedOrder:
                pass
            except Exception as e:
                if bar_index + 1 >= candles.shape[0]:
                    pass
                else:
                    logger.error(f"Exception hit in eval strat -> {e}")
                    raise Exception(f"Exception hit in eval strat -> {e}")
    order_records_df = order_records_to_df(order_records[:or_filled])
    pretty_qf(dynamic_order_settings)
    if plot_results:
        strategy.plot_signals(candles=candles)
        plot_or_results(candles=candles, order_records_df=order_records_df)
    return order_records_df
