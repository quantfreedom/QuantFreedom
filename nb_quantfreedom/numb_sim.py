import numpy as np
from numba import njit
from nb_quantfreedom.nb_enums import *
from nb_quantfreedom.nb_custom_logger import CustomLoggerNB
from nb_quantfreedom.nb_helper_funcs import get_to_the_upside_nb, nb_get_dos
from nb_quantfreedom.nb_order_handler.nb_class_helpers import PriceGetterNB, ZeroOrEntryNB
from nb_quantfreedom.nb_order_handler.nb_decrease_position import DecreasePositionNB
from nb_quantfreedom.nb_order_handler.nb_increase_position import IncreasePositionNB
from nb_quantfreedom.nb_order_handler.nb_leverage import LeverageClass, LeverageNB


from nb_quantfreedom.nb_order_handler.nb_stop_loss import StopLossNB
from nb_quantfreedom.nb_order_handler.nb_take_profit import TakeProfitNB
from nb_quantfreedom.strategies.nb_strategy import nb_CreateInd, nb_Strategy


@njit(cache=True)
def nb_run_backtest(
    sl_calculator: StopLossNB,
    backtest_settings: BacktestSettings,
    candles: np.array,
    checker_liq_hit: LeverageClass,
    checker_sl_hit: StopLossNB,
    checker_tp_hit: TakeProfitNB,
    checker_tsl: StopLossNB,
    dec_pos_calculator: DecreasePositionNB,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    exit_fee_pct: float,
    inc_pos_calculator: IncreasePositionNB,
    logger: CustomLoggerNB,
    lev_calculator: LeverageNB,
    checker_sl_to_be: StopLossNB,
    set_z_e: ZeroOrEntryNB,
    sl_bcb_price_getter: PriceGetterNB,
    sl_mover: StopLossNB,
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
    mmr_pct = exchange_settings.mmr_pct

    array_size = int(total_indicator_settings * total_order_settings / backtest_settings.divide_records_array_size_by)

    strategy_result_records = np.empty(
        array_size,
        dtype=strat_df_array_dt,
    )
    result_records_filled = 0

    for ind_set_index in range(total_indicator_settings):
        logger.log_info("Indicator settings index = {ind_set_index:,")
        indicator_settings = strategy.nb_get_current_ind_settings(
            ind_set_index=ind_set_index,
            logger=logger,
        )

        for dos_index in range(total_order_settings):
            logger.log_info("Order settings index = {dos_index:,")
            dynamic_order_settings = nb_get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )

            logger.log_info("Created Order class")

            starting_bar = dynamic_order_settings.num_candles - 1

            order_result = OrderResult(
                ind_set_index=-1,
                dos_index=-1,
                bar_index=-1,
                timestamp=-1,
                equity=starting_equity,
                available_balance=starting_equity,
                cash_borrowed=0.0,
                cash_used=0.0,
                average_entry=0.0,
                can_move_sl_to_be=False,
                fees_paid=0.0,
                leverage=0.0,
                liq_price=0.0,
                order_status=OrderStatus.Nothing,
                possible_loss=0.0,
                entry_size_asset=0.0,
                entry_size_usd=0.0,
                entry_price=0.0,
                exit_price=0.0,
                position_size_asset=0.0,
                position_size_usd=0.0,
                realized_pnl=0.0,
                sl_pct=0.0,
                sl_price=0.0,
                total_trades=0,
                tp_pct=0.0,
                tp_price=0.0,
            )

            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0

            total_fees_paid = 0
            at_max_entries = False
            # entries loop
            for bar_index in range(starting_bar, total_bars):
                logger.log_info(
                    "ind_idx={ind_set_index:,} dos_idx={dos_index:,} bar_idx={bar_index:,} timestamp={timestamp"
                )

                if order_result.position_size_usd > 0:
                    try:
                        logger.log_debug("nb_base.py - nb_run_backtest() - will check_stop_loss_hit")
                        # checker_sl_hit.check_stop_loss_hit(
                        #     current_candle=candles[bar_index, :],
                        #     exit_fee_pct=market_fee_pct,
                        #     sl_price=order_result.sl_price,
                        #     logger=logger,
                        # )
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will check_liq_hit")
                        # checker_liq_hit.check_liq_hit(
                        #     current_candle=candles[bar_index, :],
                        #     exit_fee_pct=market_fee_pct,
                        #     liq_price=order_result.liq_price,
                        #     logger=logger,
                        # )

                        # logger.log_debug("nb_base.py - nb_run_backtest() - will check_tp_hit")
                        # checker_tp_hit.check_tp_hit(
                        #     current_candle=candles[bar_index, :],
                        #     exit_fee_pct=exit_fee_pct,
                        #     tp_price=order_result.tp_price,
                        #     logger=logger,
                        # )
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will check_move_stop_loss_to_be")
                        # checker_sl_to_be.check_move_stop_loss_to_be(
                        #     average_entry=order_result.average_entry,
                        #     can_move_sl_to_be=order_result.can_move_sl_to_be,
                        #     candle_body_type=dynamic_order_settings.sl_to_be_cb_type,
                        #     current_candle=candles[bar_index, :],
                        #     set_z_e=set_z_e,
                        #     market_fee_pct=market_fee_pct,
                        #     sl_price=order_result.sl_price,
                        #     sl_to_be_move_when_pct=dynamic_order_settings.sl_to_be_when_pct,
                        #     price_tick_step=price_tick_step,
                        #     logger=logger,
                        # )

                        # logger.log_debug("nb_base.py - nb_run_backtest() - will check_move_trailing_stop_loss")
                        # checker_tsl.check_move_trailing_stop_loss(
                        #     average_entry=order_result.average_entry,
                        #     can_move_sl_to_be=order_result.can_move_sl_to_be,
                        #     candle_body_type=dynamic_order_settings.trail_sl_bcb_type,
                        #     current_candle=candles[bar_index, :],
                        #     price_tick_step=price_tick_step,
                        #     sl_price=order_result.sl_price,
                        #     trail_sl_by_pct=dynamic_order_settings.trail_sl_by_pct,
                        #     trail_sl_when_pct=dynamic_order_settings.trail_sl_when_pct,
                        #     logger=logger,
                        # )
                    except RejectedOrder:
                        # logger.log_info("RejectedOrder -> {msg}")msg=RejectedOrder().msg
                        pass
                    except MoveStopLoss:
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will move_stop_loss")
                        # order_result = sl_mover.move_stop_loss(
                        #     bar_index=bar_index,
                        #     can_move_sl_to_be=MoveStopLoss().can_move_sl_to_be,
                        #     dos_index=dos_index,
                        #     ind_set_index=ind_set_index,
                        #     order_result=order_result,
                        #     order_status=MoveStopLoss().order_status,
                        #     sl_price=MoveStopLoss().sl_price,
                        #     timestamp=candles[bar_index : CandleBodyType.Timestamp],
                        #     logger=logger,
                        # )
                        pass
                    except DecreasePosition:
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will decrease_position")
                        # equity, fees_paid, realized_pnl = dec_pos_calculator.decrease_position(
                        #     average_entry=order_result.average_entry,
                        #     equity=order_result.equity,
                        #     exit_fee_pct=DecreasePosition().exit_fee_pct,
                        #     exit_price=DecreasePosition().exit_price,
                        #     market_fee_pct=market_fee_pct,
                        #     order_status=DecreasePosition().order_status,
                        #     position_size_asset=order_result.position_size_asset,
                        #     logger=logger,
                        # )
                        # # Fill pnl array
                        # pnl_array[filled_pnl_counter] = realized_pnl
                        # filled_pnl_counter += 1
                        # total_fees_paid += fees_paid

                        # # reset the order result
                        # order_result = OrderResult(
                        #     ind_set_index=-1,
                        #     dos_index=-1,
                        #     bar_index=-1,
                        #     timestamp=-1,
                        #     equity=equity,
                        #     available_balance=equity,
                        #     cash_borrowed=0.0,
                        #     cash_used=0.0,
                        #     average_entry=0.0,
                        #     can_move_sl_to_be=False,
                        #     fees_paid=0.0,
                        #     leverage=0.0,
                        #     liq_price=0.0,
                        #     order_status=OrderStatus.Nothing,
                        #     possible_loss=0.0,
                        #     entry_size_asset=0.0,
                        #     entry_size_usd=0.0,
                        #     entry_price=0.0,
                        #     exit_price=0.0,
                        #     position_size_asset=0.0,
                        #     position_size_usd=0.0,
                        #     realized_pnl=0.0,
                        #     sl_pct=0.0,
                        #     sl_price=0.0,
                        #     total_trades=0,
                        #     tp_pct=0.0,
                        #     tp_price=0.0,
                        # )
                        # at_max_entries = False
                        pass

                    except Exception:
                        # logger.log_info("Exception moving or decreasing order -> {e}")e=Exception
                        # raise Exception("Exception moving or decreasing order -> {e}")e=Exception
                        pass
                # TODO: this

                logger.log_debug("\n\n")
                logger.log_debug("nb_base.py - nb_run_backtest() - will strategy.evaluate")
                if not at_max_entries and strategy.evaluate(
                    bar_index=bar_index,
                    starting_bar=starting_bar,
                    candles=candles,
                    indicator_settings=indicator_settings,
                    ind_creator=ind_creator,
                    logger=logger,
                ):  # TODO: this and add in that we are also not at max entry amount
                    try:
                        logger.log_debug("nb_base.py - nb_run_backtest() - will calculate_stop_loss")
                        # sl_price = sl_calculator.calculate_stop_loss(
                        #     bar_index=bar_index,
                        #     candles=candles,
                        #     price_tick_step=price_tick_step,
                        #     sl_based_on_add_pct=dynamic_order_settings.sl_based_on_add_pct,
                        #     sl_based_on_lookback=dynamic_order_settings.sl_based_on_lookback,
                        #     sl_bcb_price_getter=sl_bcb_price_getter,
                        #     sl_bcb_type=dynamic_order_settings.sl_bcb_type,
                        #     logger=logger,
                        # )
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will calculate_increase_posotion")
                        # (
                        #     average_entry,
                        #     entry_price,
                        #     entry_size_asset,
                        #     entry_size_usd,
                        #     position_size_asset,
                        #     position_size_usd,
                        #     possible_loss,
                        #     total_trades,
                        #     sl_pct,
                        # ) = inc_pos_calculator.calculate_increase_posotion(
                        #     account_state_equity=order_result.equity,
                        #     asset_tick_step=asset_tick_step,
                        #     average_entry=order_result.average_entry,
                        #     entry_price=candles[bar_index, CandleBodyType.Close],
                        #     in_position=order_result.position_size_usd > 0,
                        #     market_fee_pct=market_fee_pct,
                        #     max_asset_size=max_asset_size,
                        #     max_equity_risk_pct=dynamic_order_settings.max_equity_risk_pct,
                        #     max_trades=dynamic_order_settings.max_trades,
                        #     min_asset_size=min_asset_size,
                        #     position_size_asset=order_result.position_size_asset,
                        #     position_size_usd=order_result.position_size_usd,
                        #     possible_loss=order_result.possible_loss,
                        #     price_tick_step=price_tick_step,
                        #     risk_account_pct_size=dynamic_order_settings.risk_account_pct_size,
                        #     sl_price=sl_price,
                        #     total_trades=order_result.total_trades,
                        #     logger=logger,
                        # )
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will calculate_leverage")
                        # (
                        #     available_balance,
                        #     can_move_sl_to_be,
                        #     cash_borrowed,
                        #     cash_used,
                        #     leverage,
                        #     liq_price,
                        # ) = lev_calculator.calculate_leverage(
                        #     available_balance=order_result.available_balance,
                        #     average_entry=average_entry,
                        #     cash_borrowed=order_result.cash_borrowed,
                        #     cash_used=order_result.cash_used,
                        #     entry_size_usd=entry_size_usd,
                        #     max_leverage=max_leverage,
                        #     mmr_pct=mmr_pct,
                        #     sl_price=sl_price,
                        #     static_leverage=dynamic_order_settings.static_leverage,
                        #     leverage_tick_step=leverage_tick_step,
                        #     price_tick_step=price_tick_step,
                        #     logger=logger,
                        # )

                        # logger.log_debug("nb_base.py - nb_run_backtest() - will calculate_take_profit")
                        # (
                        #     can_move_sl_to_be,
                        #     tp_price,
                        #     tp_pct,
                        # ) = tp_calculator.calculate_take_profit(
                        #     average_entry=average_entry,
                        #     market_fee_pct=market_fee_pct,
                        #     position_size_usd=position_size_usd,
                        #     possible_loss=possible_loss,
                        #     price_tick_step=price_tick_step,
                        #     risk_reward=dynamic_order_settings.risk_reward,
                        #     tp_fee_pct=exit_fee_pct,
                        #     logger=logger,
                        # )
                        # logger.log_debug("nb_base.py - nb_run_backtest() - will OrderResult")
                        # order_result = OrderResult(
                        #     # where we are at
                        #     ind_set_index=ind_set_index,
                        #     dos_index=dos_index,
                        #     bar_index=bar_index + 1,  # put plus 1 because we need to place entry on next bar
                        #     timestamp=candles[bar_index + 1, CandleBodyType.Timestamp],
                        #     # account info
                        #     equity=order_result.equity,
                        #     available_balance=available_balance,
                        #     cash_borrowed=cash_borrowed,
                        #     cash_used=cash_used,
                        #     # order info
                        #     average_entry=average_entry,
                        #     can_move_sl_to_be=can_move_sl_to_be,
                        #     fees_paid=0.0,
                        #     leverage=leverage,
                        #     liq_price=liq_price,
                        #     order_status=OrderStatus.EntryFilled,
                        #     possible_loss=possible_loss,
                        #     entry_size_asset=entry_size_asset,
                        #     entry_size_usd=entry_size_usd,
                        #     entry_price=entry_price,
                        #     exit_price=0.0,
                        #     position_size_asset=position_size_asset,
                        #     position_size_usd=position_size_usd,
                        #     realized_pnl=0.0,
                        #     sl_pct=sl_pct,
                        #     sl_price=sl_price,
                        #     total_trades=total_trades,
                        #     tp_pct=tp_pct,
                        #     tp_price=tp_price,
                        # )

                    except RejectedOrder:
                        # logger.log_info("RejectedOrder -> {msg}")msg=RejectedOrder().msg
                        # at_max_entries = RejectedOrder().at_max_entries
                        pass
                    except Exception:
                        # logger.log_info("Exception placing order -> {e}")e=Exception
                        # raise Exception("Exception placing order -> {e}")e=Exception
                        pass
            # Checking if gains
            gains_pct = round(((order_result.equity - starting_equity) / starting_equity) * 100, 2)
            logger.log_info("Starting eq={starting_equity Ending eq={equity gains pct={gains_pct")
            if gains_pct > backtest_settings.gains_pct_filter:
                wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]

                # Checking total trade filter
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
                        strategy_result_records[result_records_filled]["fees_paid"] = round(total_fees_paid, 4)
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["ending_eq"] = order_result.equity

                        result_records_filled += 1
        logger.log_info("Starting New Loop\n\n")
    return strategy_result_records[:result_records_filled]
