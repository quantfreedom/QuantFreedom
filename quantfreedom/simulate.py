import numpy as np
import pandas as pd
from logging import getLogger
from quantfreedom.custom_logger import set_loggers
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
)
from quantfreedom.helper_funcs import dos_cart_product, get_dos, get_to_the_upside_nb
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.strategies.strategy import Strategy

logger = getLogger("info")


def run_df_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    static_os: StaticOrderSettings,
    strategy: Strategy,
):
    if static_os.logger_bool == False:
        logger.disabled = True
    else:
        set_loggers()

    starting_equity = static_os.starting_equity

    dos_cart_arrays = dos_cart_product(
        dos_arrays=dos_arrays,
    )

    order = OrderHandler(static_os=static_os, exchange_settings=exchange_settings)

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

    array_size = int(backtest_settings.array_size)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )
    result_records_filled = 0

    for ind_set_index in range(total_indicator_settings):
        strategy.set_ind_settings(
            ind_set_index=ind_set_index,
        )

        for dos_index in range(total_order_settings):
            logger.info(f"Indicator settings index= {ind_set_index}")
            strategy.log_indicator_settings()

            logger.info(f"Dynamic Order settings index= {dos_index}")
            dynamic_order_settings = get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )
            log_dynamic_order_settings(dynamic_order_settings=dynamic_order_settings)

            starting_bar = dynamic_order_settings.num_candles - 1
            strategy.starting_bar = starting_bar
            logger.debug(f"Starting Bar= {starting_bar}")

            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0
            total_fees_paid = 0

            order.update_class_dos(dynamic_order_settings=dynamic_order_settings)
            order.reset_order_variables(equity=starting_equity)

            logger.debug("Set order variables, class dos and pnl array")

            for bar_index in range(starting_bar, total_bars):
                logger.info("\n\n")
                timestamp = pd.to_datetime(candles[bar_index, CandleBodyType.Timestamp], unit="ms")
                logger.info(
                    f"ind_idx= {ind_set_index} dos_idx= {dos_index} bar_idx= {bar_index} timestamp= {timestamp}"
                )

                if order.order_position_size_usd > 0:
                    try:
                        current_candle = candles[bar_index, :]
                        logger.debug("Checking stop loss hit")
                        order.check_stop_loss_hit(current_candle=current_candle)
                        logger.debug("Checking liq hit")
                        order.check_liq_hit(current_candle=current_candle)
                        logger.debug("Checking take profit hit")
                        order.check_take_profit_hit(current_candle=current_candle)

                        logger.debug("Checking to move stop to break even")
                        sl_to_be_price = order.check_move_sl_to_be(current_candle=current_candle)
                        if sl_to_be_price:
                            order.order_sl_price = sl_to_be_price

                        logger.debug("Checking to move trailing stop loss")
                        tsl_price = order.check_move_tsl(current_candle=current_candle)
                        if tsl_price:
                            order.order_sl_price = tsl_price
                    except DecreasePosition as e:
                        (
                            equity,
                            fees_paid,
                            realized_pnl,
                        ) = order.calculate_decrease_position(
                            exit_fee_pct=e.exit_fee_pct,
                            exit_price=e.exit_price,
                            order_status=e.order_status,
                        )

                        pnl_array[filled_pnl_counter] = realized_pnl
                        filled_pnl_counter += 1
                        total_fees_paid += fees_paid
                        logger.debug("Filled pnl array and updated total fees paid")

                        order.reset_order_variables(equity=equity)
                        logger.debug("reset order variables")

                    except Exception as e:
                        logger.error(f"Exception checking sl liq tp and move -> {e}")
                        raise Exception(f"Exception checking sl liq tp  and move -> {e}")
                else:
                    logger.debug("Not in a pos so not checking SL Liq or TP")

                logger.debug("strategy evaluate")
                if strategy.evaluate(bar_index=bar_index, candles=candles):
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
                            average_entry=order.order_average_entry,
                            entry_price=candles[bar_index + 1, CandleBodyType.Open],
                            equity=order.order_equity,
                            position_size_asset=order.order_position_size_asset,
                            position_size_usd=order.order_position_size_usd,
                            possible_loss=order.order_possible_loss,
                            sl_price=sl_price,
                            total_trades=order.order_total_trades,
                        )

                        logger.debug("calculate_leverage")
                        (
                            available_balance,
                            cash_borrowed,
                            cash_used,
                            leverage,
                            liq_price,
                        ) = order.calculate_leverage(
                            available_balance=order.order_available_balance,
                            average_entry=average_entry,
                            cash_borrowed=order.order_cash_borrowed,
                            cash_used=order.order_cash_used,
                            entry_size_usd=entry_size_usd,
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
                        order.fill_order_result(
                            available_balance=available_balance,
                            average_entry=average_entry,
                            can_move_sl_to_be=can_move_sl_to_be,
                            cash_borrowed=cash_borrowed,
                            cash_used=cash_used,
                            entry_price=entry_price,
                            entry_size_asset=entry_size_asset,
                            entry_size_usd=entry_size_usd,
                            equity=order.order_equity,
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
                        logger.debug("We are in a position and filled the result")
                    except RejectedOrder:
                        pass
                    except Exception as e:
                        logger.debug(f"Exception hit in eval strat -> {e}")
                        pass
            # Checking if gains
            gains_pct = round(((order.order_equity - starting_equity) / starting_equity) * 100, 3)
            wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
            total_trades_closed = wins_and_losses_array.size
            logger.info(
                f"Results from backtest\n\
ind_set_index={ind_set_index}\n\
dos_index={dos_index}\n\
Starting eq={starting_equity}\n\
Ending eq={order.order_equity}\n\
Gains pct={gains_pct}\n\
Total_trades={total_trades_closed}"
            )
            if total_trades_closed > 0 and gains_pct > backtest_settings.gains_pct_filter:
                if wins_and_losses_array.size > backtest_settings.total_trade_filter:
                    wins_and_losses_array_no_be = wins_and_losses_array[
                        (wins_and_losses_array < -0.009) | (wins_and_losses_array > 0.009)
                    ]
                    to_the_upside = get_to_the_upside_nb(
                        gains_pct=gains_pct,
                        wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                    )

                    # Checking to the upside filter
                    if to_the_upside > backtest_settings.upside_filter:
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
                        record["to_the_upside"] = to_the_upside
                        record["fees_paid"] = round(total_fees_paid, 3)
                        record["total_pnl"] = total_pnl
                        record["ending_eq"] = order.order_equity

                        result_records_filled += 1
            logger.info(
                f"Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            )
    return pd.DataFrame(strategy_result_records[:result_records_filled])


def log_dynamic_order_settings(dynamic_order_settings: DynamicOrderSettingsArrays):
    logger.info(
        f"Set Dynamic Order Settings\n\
max_equity_risk_pct={round(dynamic_order_settings.max_equity_risk_pct * 100, 3)}\n\
max_trades={dynamic_order_settings.max_trades}\n\
num_candles={dynamic_order_settings.num_candles}\n\
risk_account_pct_size={round(dynamic_order_settings.risk_account_pct_size * 100, 3)}\n\
risk_reward={dynamic_order_settings.risk_reward}\n\
sl_based_on_add_pct={round(dynamic_order_settings.sl_based_on_add_pct * 100, 3)}\n\
sl_based_on_lookback={dynamic_order_settings.sl_based_on_lookback}\n\
sl_bcb_type={dynamic_order_settings.sl_bcb_type}\n\
sl_to_be_cb_type={dynamic_order_settings.sl_to_be_cb_type}\n\
sl_to_be_when_pct={round(dynamic_order_settings.sl_to_be_when_pct * 100, 3)}\n\
static_leverage={dynamic_order_settings.static_leverage}\n\
trail_sl_bcb_type={dynamic_order_settings.trail_sl_bcb_type}\n\
trail_sl_by_pct={round(dynamic_order_settings.trail_sl_by_pct * 100, 3)}\n\
trail_sl_when_pct={round(dynamic_order_settings.trail_sl_when_pct * 100, 3)}"
    )
