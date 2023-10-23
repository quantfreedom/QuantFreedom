import numpy as np
from numba import njit
from nb_quantfreedom.nb_enums import *
from nb_quantfreedom.nb_custom_logger import CustomLoggerClass
from nb_quantfreedom.nb_helper_funcs import get_to_the_upside_nb, nb_get_dos
from nb_quantfreedom.nb_order_handler.nb_class_helpers import PriceGetterNB, ZeroOrEntryNB
from nb_quantfreedom.nb_order_handler.nb_decrease_position import DecreasePositionNB
from nb_quantfreedom.nb_order_handler.nb_increase_position import AccExOther, IncreasePositionNB, OrderInfo
from nb_quantfreedom.nb_order_handler.nb_leverage import LeverageClass, LeverageNB


from nb_quantfreedom.nb_order_handler.nb_stop_loss import StopLossClass
from nb_quantfreedom.nb_order_handler.nb_take_profit import TakeProfitNB
from nb_quantfreedom.strategies.nb_strategy import nb_CreateInd, nb_Strategy


@njit(cache=True)
def nb_run_backtest(
    sl_calculator: StopLossClass,
    backtest_settings: BacktestSettings,
    candles: np.array,
    checker_liq_hit: LeverageClass,
    checker_sl_hit: StopLossClass,
    checker_tp_hit: TakeProfitNB,
    checker_tsl: StopLossClass,
    dec_pos_calculator: DecreasePositionNB,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    exit_fee_pct: float,
    inc_pos_calculator: IncreasePositionNB,
    logger: CustomLoggerClass,
    lev_calculator: LeverageNB,
    checker_sl_to_be: StopLossClass,
    set_z_e: ZeroOrEntryNB,
    sl_bcb_price_getter: PriceGetterNB,
    sl_mover: StopLossClass,
    starting_equity: float,
    strategy: nb_Strategy,
    ind_creator: nb_CreateInd,
    total_bars: int,
    total_indicator_settings: int,
    total_order_settings: int,
    tp_calculator: TakeProfitNB,
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
        indicator_settings = strategy.nb_get_current_ind_settings(
            ind_set_index=ind_set_index,
            logger=logger,
        )

        for dos_index in range(total_order_settings):
            logger.log_info(
                "nb_simulate.py - No Class - nb_run_backtest() - Indicator settings index=" + str(ind_set_index)
            )
            logger.log_info(
                (
                    "nb_simulate.py - No Class - nb_run_backtest() - Indicator settings\n"
                    + strategy.nb_get_ind_set_str(indicator_settings=indicator_settings, logger=logger)
                )
            )
            dynamic_order_settings = nb_get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )
            logger.log_info(
                "nb_simulate.py - No Class - nb_run_backtest() - Dynamic Order settings index=" + str(dos_index)
            )
            # logger.log_info(
            #     "nb_simulate.py - No Class - nb_run_backtest() - Created Dynamic Order Settings part 1"
            #     + "\nentry_size_asset= "
            #     + logger.float_to_str(dynamic_order_settings.entry_size_asset)
            #     + "\nmax_equity_risk_pct= "
            #     + logger.float_to_str(round(dynamic_order_settings.max_equity_risk_pct * 100, 3))
            #     + "\nmax_trades= "
            #     + str(dynamic_order_settings.max_trades)
            #     + "\nnum_candles= "
            #     + str(dynamic_order_settings.num_candles)
            #     + "\nrisk_account_pct_size= "
            #     + logger.float_to_str(round(dynamic_order_settings.risk_account_pct_size * 100, 3))
            #     + "\nrisk_reward= "
            #     + logger.float_to_str(dynamic_order_settings.risk_reward)
            #     + "\nsl_based_on_add_pct= "
            #     + logger.float_to_str(round(dynamic_order_settings.sl_based_on_add_pct * 100, 3))
            #     + "\nsl_based_on_lookback= "
            #     + str(dynamic_order_settings.sl_based_on_lookback)
            # )
            # logger.log_info(
            #     "nb_simulate.py - No Class - nb_run_backtest() - Created Dynamic Order Settings part 2"
            #     + "\nsl_bcb_type= "
            #     + logger.candle_body_str(dynamic_order_settings.sl_bcb_type)
            #     + "\nsl_to_be_cb_type= "
            #     + logger.candle_body_str(dynamic_order_settings.sl_to_be_cb_type)
            #     + "\nsl_to_be_when_pct= "
            #     + logger.float_to_str(round(dynamic_order_settings.sl_to_be_when_pct * 100, 3))
            #     + "\nsl_to_be_ze_type= "
            #     + logger.z_or_e_str(dynamic_order_settings.sl_to_be_ze_type)
            #     + "\nstatic_leverage= "
            #     + logger.float_to_str(dynamic_order_settings.static_leverage)
            #     + "\ntrail_sl_bcb_type= "
            #     + logger.candle_body_str(dynamic_order_settings.trail_sl_bcb_type)
            #     + "\ntrail_sl_by_pct= "
            #     + logger.float_to_str(round(dynamic_order_settings.trail_sl_by_pct * 100, 3))
            #     + "\ntrail_sl_when_pct= "
            #     + logger.float_to_str(round(dynamic_order_settings.trail_sl_when_pct * 100, 3))
            # )

            starting_bar = dynamic_order_settings.num_candles - 1
            logger.log_info("nb_simulate.py - No Class - nb_run_backtest() - Starting Bar=" + str(starting_bar))

            account_state = AccountState(
                # where we are at
                ind_set_index=-1,
                dos_index=-1,
                bar_index=-1,
                timestamp=-1,
                # account info
                available_balance=starting_equity,
                cash_borrowed=0.0,
                cash_used=0.0,
                equity=starting_equity,
                fees_paid=0.0,
                possible_loss=0.0,
                realized_pnl=0.0,
                total_trades=0,
            )
            order_result = OrderResult(
                average_entry=0.0,
                can_move_sl_to_be=False,
                entry_price=0.0,
                entry_size_asset=0.0,
                entry_size_usd=0.0,
                exit_price=0.0,
                leverage=1.0,
                liq_price=0.0,
                order_status=OrderStatus.Nothing,
                position_size_asset=0.0,
                position_size_usd=0.0,
                sl_pct=0.0,
                sl_price=0.0,
                tp_pct=0.0,
                tp_price=0.0,
            )

            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0

            total_fees_paid = 0
            logger.log_info(
                "nb_simulate.py - No Class - nb_run_backtest() - account state order results pnl array all set to default"
            )
            for bar_index in range(starting_bar, total_bars):
                logger.log_info("\n\n")
                logger.log_info(
                    (
                        "nb_simulate.py - No Class - nb_run_backtest() - ind_idx="
                        + str(ind_set_index)
                        + " dos_idx="
                        + str(dos_index)
                        + " bar_idx="
                        + str(bar_index)
                        + " timestamp="
                        + logger.log_datetime(int(candles[bar_index, CandleBodyType.Timestamp]))
                    )
                )

                if order_result.position_size_usd > 0:
                    try:
                        # checking if sl hit
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - check_stop_loss_hit")
                        sl_hit_bool = checker_sl_hit.check_stop_loss_hit(
                            current_candle=candles[bar_index, :],
                            sl_price=order_result.sl_price,
                            logger=logger,
                        )
                        if sl_hit_bool:
                            logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - decrease_position")
                            (
                                account_state,
                                fees_paid,
                                order_result,
                                realized_pnl,
                            ) = dec_pos_calculator.decrease_position(
                                average_entry=order_result.average_entry,
                                equity=account_state.equity,
                                exit_fee_pct=market_fee_pct,
                                exit_price=order_result.sl_price,
                                logger=logger,
                                market_fee_pct=market_fee_pct,
                                position_size_asset=order_result.position_size_asset,
                            )
                            pnl_array[filled_pnl_counter] = realized_pnl
                            filled_pnl_counter += 1
                            total_fees_paid += fees_paid
                            raise DecreasePosition

                        # checking if liq hit
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - check_liq_hit")
                        liq_hit_bool = checker_liq_hit.check_liq_hit(
                            current_candle=candles[bar_index, :],
                            liq_price=order_result.liq_price,
                            logger=logger,
                        )
                        if liq_hit_bool:
                            logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - decrease_position")
                            (
                                account_state,
                                fees_paid,
                                order_result,
                                realized_pnl,
                            ) = dec_pos_calculator.decrease_position(
                                average_entry=order_result.average_entry,
                                equity=account_state.equity,
                                exit_fee_pct=market_fee_pct,
                                exit_price=order_result.liq_price,
                                logger=logger,
                                market_fee_pct=market_fee_pct,
                                position_size_asset=order_result.position_size_asset,
                            )
                            pnl_array[filled_pnl_counter] = realized_pnl
                            filled_pnl_counter += 1
                            total_fees_paid += fees_paid
                            raise DecreasePosition

                        # checking if tp hit
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - check_tp_hit")
                        tp_hit_bool = checker_tp_hit.check_tp_hit(
                            current_candle=candles[bar_index, :],
                            tp_price=order_result.tp_price,
                            logger=logger,
                        )
                        if tp_hit_bool:
                            logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - decrease_position")
                            (
                                account_state,
                                fees_paid,
                                order_result,
                                realized_pnl,
                            ) = dec_pos_calculator.decrease_position(
                                average_entry=order_result.average_entry,
                                equity=account_state.equity,
                                exit_fee_pct=exit_fee_pct,
                                exit_price=order_result.tp_price,
                                logger=logger,
                                market_fee_pct=market_fee_pct,
                                position_size_asset=order_result.position_size_asset,
                            )
                            pnl_array[filled_pnl_counter] = realized_pnl
                            filled_pnl_counter += 1
                            total_fees_paid += fees_paid
                            raise DecreasePosition

                        # checking to move stop loss

                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - check_move_stop_loss_to_be")
                        temp_sl = checker_sl_to_be.check_move_stop_loss_to_be(
                            average_entry=order_result.average_entry,
                            can_move_sl_to_be=order_result.can_move_sl_to_be,
                            candle_body_type=dynamic_order_settings.sl_to_be_cb_type,
                            current_candle=candles[bar_index, :],
                            set_z_e=set_z_e,
                            sl_price=order_result.sl_price,
                            sl_to_be_move_when_pct=dynamic_order_settings.sl_to_be_when_pct,
                            logger=logger,
                        )
                        if temp_sl > 0:
                            logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - move_stop_loss")
                            account_state, order_result = sl_mover.move_stop_loss(
                                account_state=account_state,
                                bar_index=bar_index,
                                can_move_sl_to_be=False,
                                dos_index=dos_index,
                                ind_set_index=ind_set_index,
                                logger=logger,
                                order_result=order_result,
                                order_status=OrderStatus.MovedSLToBE,
                                sl_price=temp_sl,
                                timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                            )

                        # Checking to move trailing stop loss

                        logger.log_debug(
                            "nb_simulate.py - No Class - nb_run_backtest() - check_move_trailing_stop_loss"
                        )
                        temp_tsl = checker_tsl.check_move_trailing_stop_loss(
                            average_entry=order_result.average_entry,
                            can_move_sl_to_be=order_result.can_move_sl_to_be,
                            candle_body_type=dynamic_order_settings.trail_sl_bcb_type,
                            current_candle=candles[bar_index, :],
                            sl_price=order_result.sl_price,
                            trail_sl_by_pct=dynamic_order_settings.trail_sl_by_pct,
                            trail_sl_when_pct=dynamic_order_settings.trail_sl_when_pct,
                            logger=logger,
                        )
                        if temp_tsl > 0:
                            logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - move_stop_loss")
                            account_state, order_result = sl_mover.move_stop_loss(
                                account_state=account_state,
                                bar_index=bar_index,
                                can_move_sl_to_be=False,
                                dos_index=dos_index,
                                ind_set_index=ind_set_index,
                                logger=logger,
                                order_result=order_result,
                                order_status=OrderStatus.MovedSLToBE,
                                sl_price=temp_tsl,
                                timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                            )
                    except Exception:
                        # raise Exception
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - Exception hit in eval strat")
                        pass
                else:
                    logger.log_debug(
                        "nb_simulate.py - No Class - nb_run_backtest() - Not in a pos so not checking SL Liq or TP"
                    )
                logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - strategy evaluate")
                eval_bool = strategy.evaluate(
                    bar_index=bar_index,
                    starting_bar=starting_bar,
                    candles=candles,
                    indicator_settings=indicator_settings,
                    ind_creator=ind_creator,
                    logger=logger,
                )
                if eval_bool:
                    try:
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - calculate_stop_loss")
                        sl_price = sl_calculator.calculate_stop_loss(
                            bar_index=bar_index,
                            candles=candles,
                            logger=logger,
                            price_tick_step=price_tick_step,
                            sl_based_on_add_pct=dynamic_order_settings.sl_based_on_add_pct,
                            sl_based_on_lookback=dynamic_order_settings.sl_based_on_lookback,
                            sl_bcb_price_getter=sl_bcb_price_getter,
                            sl_bcb_type=dynamic_order_settings.sl_bcb_type,
                        )

                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - calculate_increase_posotion")
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
                        ) = inc_pos_calculator.calculate_increase_posotion(
                            acc_ex_other=AccExOther(
                                account_state_equity=account_state.equity,
                                asset_tick_step=asset_tick_step,
                                logger=logger,
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
                        )

                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - calculate_leverage")
                        (
                            available_balance,
                            cash_borrowed,
                            cash_used,
                            leverage,
                            liq_price,
                        ) = lev_calculator.calculate_leverage(
                            available_balance=account_state.available_balance,
                            average_entry=average_entry,
                            cash_borrowed=account_state.cash_borrowed,
                            cash_used=account_state.cash_used,
                            entry_size_usd=entry_size_usd,
                            max_leverage=max_leverage,
                            min_leverage=min_leverage,
                            mmr_pct=mmr_pct,
                            sl_price=sl_price,
                            static_leverage=dynamic_order_settings.static_leverage,
                            leverage_tick_step=leverage_tick_step,
                            price_tick_step=price_tick_step,
                            logger=logger,
                        )

                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - calculate_take_profit")
                        (
                            can_move_sl_to_be,
                            tp_price,
                            tp_pct,
                        ) = tp_calculator.calculate_take_profit(
                            average_entry=average_entry,
                            market_fee_pct=market_fee_pct,
                            position_size_usd=position_size_usd,
                            possible_loss=possible_loss,
                            price_tick_step=price_tick_step,
                            risk_reward=dynamic_order_settings.risk_reward,
                            tp_fee_pct=exit_fee_pct,
                            logger=logger,
                        )

                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - Recorded Trade")
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
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - Account State OrderResult")
                    except Exception:
                        logger.log_debug("nb_simulate.py - No Class - nb_run_backtest() - Exception hit in eval strat")
                        pass
                        # raise Exception
            # Checking if gains
            gains_pct = round(((account_state.equity - starting_equity) / starting_equity) * 100, 2)
            wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
            total_trades_closed = wins_and_losses_array.size
            logger.log_info(
                "nb_simulate.py - No Class - nb_run_backtest() - Results from backtest\n"
                + "\nind_set_index= "
                + str(ind_set_index)
                + "\ndos_index= "
                + str(dos_index)
                + "\nStarting eq= "
                + logger.float_to_str(starting_equity)
                + "\nEnding eq= "
                + logger.float_to_str(account_state.equity)
                + "\nGains pct= "
                + logger.float_to_str(gains_pct)
                + "\nTotal_trades= "
                + str(total_trades_closed)
                + "\n"
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
                        win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)

                        total_pnl = wins_and_losses_array.sum()

                        # strat array
                        strategy_result_records[result_records_filled]["ind_set_idx"] = ind_set_index
                        strategy_result_records[result_records_filled]["dos_index"] = dos_index
                        strategy_result_records[result_records_filled]["total_trades"] = wins_and_losses_array.size
                        strategy_result_records[result_records_filled]["gains_pct"] = gains_pct
                        strategy_result_records[result_records_filled]["win_rate"] = win_rate
                        strategy_result_records[result_records_filled]["to_the_upside"] = to_the_upside
                        strategy_result_records[result_records_filled]["fees_paid"] = round(total_fees_paid, 3)
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["ending_eq"] = account_state.equity

                        result_records_filled += 1
            logger.log_info(
                "Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            )
    return strategy_result_records[:result_records_filled]
