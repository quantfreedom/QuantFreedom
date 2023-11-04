import numpy as np
import pandas as pd
from logging import getLogger
from quantfreedom.enums import *
from quantfreedom.custom_logger import *

from quantfreedom.order_handler.decrease_position import decrease_position
from quantfreedom.order_handler.increase_position import AccExOther, OrderInfo, long_min_amount, long_rpa_slbcb
from quantfreedom.order_handler.order import OrderHandler
from quantfreedom.order_handler.take_profit import long_c_tp_hit_regular, long_tp_rr
from quantfreedom.order_handler.leverage import long_check_liq_hit, long_dynamic_lev, long_static_lev
from quantfreedom.helper_funcs import (
    get_dos,
    get_to_the_upside_nb,
    max_price_getter,
    min_price_getter,
    sl_to_entry,
    sl_to_z_e_pass,
    long_sl_to_zero,
)
from quantfreedom.order_handler.stop_loss import (
    long_c_sl_hit,
    long_cm_sl_to_be,
    long_cm_sl_to_be_pass,
    long_cm_tsl,
    long_cm_tsl_pass,
    long_sl_bcb,
    move_stop_loss,
    move_stop_loss_pass,
)

logger = getLogger("info")


def sim_df_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    evaluate,
    exchange_settings: ExchangeSettings,
    get_current_ind_settings,
    get_ind_set_str,
    get_total_ind_settings,
    ind_creator,
    logger_type: LoggerType,
    starting_equity: float,
    static_os: StaticOrderSettings,
):

    if static_os.long_or_short == LongOrShortType.Long:
        # Decrease Position
        dec_pos_calculator = decrease_position
  

        """
        #########################################
        #########################################
        #########################################
                        Leverage
                        Leverage
                        Leverage
        #########################################
        #########################################
        #########################################
        """

        if static_os.leverage_strategy_type == LeverageStrategyType.Dynamic:
            lev_calculator = long_dynamic_lev
        else:
            lev_calculator = long_static_lev

        checker_liq_hit = long_check_liq_hit
        """
        #########################################
        #########################################
        #########################################
                        Take Profit
                        Take Profit
                        Take Profit
        #########################################
        #########################################
        #########################################
        """

        if static_os.tp_strategy_type == TakeProfitStrategyType.RiskReward:
            tp_calculator = long_tp_rr
            checker_tp_hit = long_c_tp_hit_regular
        elif static_os.tp_strategy_type == TakeProfitStrategyType.Provided:
            pass
    """
    #########################################
    #########################################
    #########################################
                Other Settings
                Other Settings
                Other Settings
    #########################################
    #########################################
    #########################################
    """

    if static_os.tp_fee_type == TakeProfitFeeType.Market:
        exit_fee_pct = exchange_settings.market_fee_pct
    else:
        exit_fee_pct = exchange_settings.limit_fee_pct
    """
    #########################################
    #########################################
    #########################################
                End User Setup
                End User Setup
                End User Setup
    #########################################
    #########################################
    #########################################
    """
    # Creating Settings Vars
    total_order_settings = dos_cart_arrays[0].size

    total_indicator_settings = get_total_ind_settings()

    total_bars = candles.shape[0]

    # logger.infoing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings to test: {total_order_settings:,}")
    print(f"Total combinations of settings to test: {total_indicator_settings * total_order_settings:,}")
    print(f"Total candles: {total_bars:,}")
    print(f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}")

    strategy_result_records = run_df_backtest(
        backtest_settings=backtest_settings,
        candles=candles,
        checker_liq_hit=checker_liq_hit,
        checker_sl_hit=checker_sl_hit,
        checker_sl_to_be=checker_sl_to_be,
        checker_tp_hit=checker_tp_hit,
        checker_tsl=checker_tsl,
        dec_pos_calculator=dec_pos_calculator,
        dos_cart_arrays=dos_cart_arrays,
        evaluate=evaluate,
        exchange_settings=exchange_settings,
        exit_fee_pct=exit_fee_pct,
        get_current_ind_settings=get_current_ind_settings,
        get_ind_set_str=get_ind_set_str,
        inc_pos_calculator=inc_pos_calculator,
        ind_creator=ind_creator,
        lev_calculator=lev_calculator,
        logger=log_func_list,
        sl_bcb_price_getter=sl_bcb_price_getter,
        sl_calculator=sl_calculator,
        sl_mover=sl_mover,
        starting_equity=starting_equity,
        stringer=str_func_list,
        total_bars=total_bars,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
        tp_calculator=tp_calculator,
        zero_or_entry_calc=zero_or_entry_calc,
    )
    return pd.DataFrame(strategy_result_records)


def run_df_backtest(
    candles: np.array,
    order: OrderHandler,
    exchange_settings: ExchangeSettings,
):
    market_fee_pct = exchange_settings.market_fee_pct
    leverage_tick_step = exchange_settings.leverage_tick_step
    price_tick_step = exchange_settings.price_tick_step
    asset_tick_step = exchange_settings.asset_tick_step
    min_asset_size = exchange_settings.min_asset_size
    max_asset_size = exchange_settings.max_asset_size
    max_leverage = exchange_settings.max_leverage
    min_leverage = exchange_settings.min_leverage
    mmr_pct = exchange_settings.mmr_pct

    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )
    result_records_filled = 0

    for ind_set_index in range(total_indicator_settings):
        indicator_settings = get_current_ind_settings(
            ind_set_index=ind_set_index,
        )

        for dos_index in range(total_order_settings):
            logger.info(f"Indicator settings index=" + str(ind_set_index))
            dynamic_order_settings = get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )
            logger.info(f"Dynamic Order settings index=" + str(dos_index))
            logger.info(
                f"Created Dynamic Order Settings \
                \nmax_equity_risk_pct={round(dynamic_order_settings.max_equity_risk_pct * 100, 3)}\
                \nmax_trades={dynamic_order_settings.max_trades}\
                \nnum_candles={dynamic_order_settings.num_candles}\
                \nrisk_account_pct_size={round(dynamic_order_settings.risk_account_pct_size * 100, 3)}\
                \nrisk_reward={dynamic_order_settings.risk_reward}\
                \nsl_based_on_add_pct={round(dynamic_order_settings.sl_based_on_add_pct * 100, 3)}\
                \nsl_based_on_lookback={dynamic_order_settings.sl_based_on_lookback}\
                \nsl_bcb_type={dynamic_order_settings.sl_bcb_type}\
                \nsl_to_be_cb_type={dynamic_order_settings.sl_to_be_cb_type}\
                \nsl_to_be_when_pct={round(dynamic_order_settings.sl_to_be_when_pct * 100, 3)}\
                \nstatic_leverage={dynamic_order_settings.static_leverage}\
                \ntrail_sl_bcb_type={dynamic_order_settings.trail_sl_bcb_type}\
                \ntrail_sl_by_pct={round(dynamic_order_settings.trail_sl_by_pct * 100, 3)}\
                \ntrail_sl_when_pct={round(dynamic_order_settings.trail_sl_when_pct * 100, 3)}"
            )

            starting_bar = dynamic_order_settings.num_candles - 1
            logger.info(f"Starting Bar= {starting_bar}")

            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0

            total_fees_paid = 0
            logger.info(f"account state order results pnl array all set to default")
            for bar_index in range(starting_bar, total_bars):
                logger.info(f"\n\n")
                logger.info(
                    f"ind_idx= {ind_set_index} dos_idx= {dos_index} bar_idx= {bar_index} timestamp= {candles[bar_index, CandleBodyType.Timestamp]}"
                )

                if order_result.position_size_usd > 0:
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
                else:
                    logger.debug("Not in a pos so not checking SL Liq or TP")
                logger.debug("strategy evaluate")
                eval_bool = evaluate(
                    bar_index=bar_index,
                    starting_bar=starting_bar,
                    candles=candles,
                    indicator_settings=indicator_settings,
                    ind_creator=ind_creator,
                    logger=logger,
                    stringer=stringer,
                )
                if eval_bool:
                    try:
                        logger.debug("calculate_stop_loss")
                        sl_price = order.calc_stop_loss(
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
                        ) = inc_pos_calculator(
                            acc_ex_other=AccExOther(
                                account_state_equity=account_state.equity,
                                asset_tick_step=asset_tick_step,
                                market_fee_pct=market_fee_pct,
                                max_asset_size=max_asset_size,
                                min_asset_size=min_asset_size,
                                possible_loss=account_state.possible_loss,
                                price_tick_step=price_tick_step,
                                total_trades=account_state.total_trades,
                            ),
                            order_info=OrderInfo(
                                average_entry=order_result.average_entry,
                                entry_price=candles[bar_index, CandleBodyType.Close],
                                in_position=order_result.position_size_usd > 0,
                                max_equity_risk_pct=dynamic_order_settings.max_equity_risk_pct,
                                max_trades=dynamic_order_settings.max_trades,
                                position_size_asset=order_result.position_size_asset,
                                position_size_usd=order_result.position_size_usd,
                                risk_account_pct_size=dynamic_order_settings.risk_account_pct_size,
                                sl_price=sl_price,
                            ),
                            logger=logger,
                            stringer=stringer,
                        )

                        logger.debug("calculate_leverage")
                        (
                            available_balance,
                            cash_borrowed,
                            cash_used,
                            leverage,
                            liq_price,
                        ) = lev_calculator(
                            available_balance=account_state.available_balance,
                            average_entry=average_entry,
                            cash_borrowed=account_state.cash_borrowed,
                            cash_used=account_state.cash_used,
                            entry_size_usd=entry_size_usd,
                            max_leverage=max_leverage,
                            min_leverage=min_leverage,
                            stringer=stringer,
                            mmr_pct=mmr_pct,
                            sl_price=sl_price,
                            static_leverage=dynamic_order_settings.static_leverage,
                            leverage_tick_step=leverage_tick_step,
                            price_tick_step=price_tick_step,
                            logger=logger,
                        )

                        logger.debug("calculate_take_profit")
                        (
                            can_move_sl_to_be,
                            tp_price,
                            tp_pct,
                        ) = tp_calculator(
                            average_entry=average_entry,
                            market_fee_pct=market_fee_pct,
                            position_size_usd=position_size_usd,
                            possible_loss=possible_loss,
                            price_tick_step=price_tick_step,
                            risk_reward=dynamic_order_settings.risk_reward,
                            tp_fee_pct=exit_fee_pct,
                            stringer=stringer,
                            logger=logger,
                        )

                        logger.debug("Recorded Trade")
                        account_state = AccountState(
                            # where we are at
                            ind_set_index=ind_set_index,
                            dos_index=dos_index,
                            bar_index=bar_index + 1,  # put plus 1 because we need to place entry on next bar
                            timestamp=int(candles[bar_index + 1, CandleBodyType.Timestamp]),
                            # account info
                            available_balance=available_balance,
                            cash_borrowed=cash_borrowed,
                            cash_used=cash_used,
                            equity=account_state.equity,
                            fees_paid=0.0,
                            possible_loss=possible_loss,
                            realized_pnl=0.0,
                            total_trades=total_trades,
                        )
                        order_result = OrderResult(
                            average_entry=average_entry,
                            can_move_sl_to_be=can_move_sl_to_be,
                            entry_price=entry_price,
                            entry_size_asset=entry_size_asset,
                            entry_size_usd=entry_size_usd,
                            exit_price=0.0,
                            leverage=leverage,
                            liq_price=liq_price,
                            order_status=OrderStatus.EntryFilled,
                            position_size_asset=position_size_asset,
                            position_size_usd=position_size_usd,
                            sl_pct=sl_pct,
                            sl_price=sl_price,
                            tp_pct=tp_pct,
                            tp_price=tp_price,
                        )
                        logger.debug("Account State OrderResult")
                    # except Exception as e:
                    #     logger.debug(
                    #         f"Exception hit in eval strat -> {e}"
                    #     )
                    #     pass
                    except Exception:
                        logger.debug("Exception hit in eval strat")
                        pass
            # Checking if gains
            gains_pct = round(((account_state.equity - starting_equity) / starting_equity) * 100, 2)
            wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
            total_trades_closed = wins_and_losses_array.size
            logger.info(
                f"Results from backtest\
                \nind_set_index={ind_set_index}\
                \ndos_index={dos_index}\
                \nStarting eq={starting_equity}\
                \nEnding eq={account_state.equity}\
                \nGains pct={gains_pct}\
                \nTotal_trades={total_trades_closed}"
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
                        win_rate = round(wins / win_loss.size * 100, 2)

                        total_pnl = wins_and_losses_array.sum()

                        # strat array
                        strategy_result_records[result_records_filled]["ind_set_idx"] = ind_set_index
                        strategy_result_records[result_records_filled]["dos_index"] = dos_index
                        strategy_result_records[result_records_filled]["total_trades"] = wins_and_losses_array.size
                        strategy_result_records[result_records_filled]["wins"] = wins
                        strategy_result_records[result_records_filled]["losses"] = losses
                        strategy_result_records[result_records_filled]["gains_pct"] = gains_pct
                        strategy_result_records[result_records_filled]["win_rate"] = win_rate
                        strategy_result_records[result_records_filled]["to_the_upside"] = to_the_upside
                        strategy_result_records[result_records_filled]["fees_paid"] = round(total_fees_paid, 3)
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["ending_eq"] = account_state.equity

                        result_records_filled += 1
            logger.info(
                f"Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            )
    return strategy_result_records[:result_records_filled]
