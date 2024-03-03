from typing import Callable
import numpy as np
from quantfreedom.enums import (
    AccountState,
    CandleBodyType,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    OrderResult,
    StaticOrderSettings,
    StaticOrderSettings,
    OrderStatus,
    DecreasePosition,
    StringerFuncType,
    or_dt,
)
from numba import njit
from quantfreedom.nb_funcs.nb_helper_funcs import nb_fill_order_records, nb_get_dos, nb_create_ao
from quantfreedom.nb_funcs.nb_order_handler.nb_decrease_position import nb_decrease_position
from quantfreedom.nb_funcs.nb_order_handler.nb_increase_position import AccExOther, OrderInfo
from quantfreedom.nb_funcs.nb_order_handler.nb_leverage import LevOrderInfo, nb_check_liq_hit, LevAccExOther


@njit(cache=True)
def nb_run_or_backtest(
    candles: np.array,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    dos_index: int,
    exchange_settings: ExchangeSettings,
    exit_fee_pct: float,
    ind_set_index: int,
    logger: Callable,
    nb_calc_dynamic_lev: Callable,
    nb_checker_sl_hit: Callable,
    nb_checker_sl_to_be: Callable,
    nb_checker_tp_hit: Callable,
    nb_checker_tsl: Callable,
    nb_entry_calc_np: Callable,
    nb_entry_calc_p: Callable,
    nb_get_bankruptcy_price: Callable,
    nb_get_liq_price: Callable,
    nb_get_tp_price: Callable,
    nb_inc_pos_calculator: Callable,
    nb_lev_calculator: Callable,
    nb_liq_hit_bool: Callable,
    nb_move_sl_bool: Callable,
    nb_pnl_calc: Callable,
    nb_sl_bcb_price_getter: Callable,
    nb_sl_calculator: Callable,
    nb_sl_hit_bool: Callable,
    nb_sl_mover: Callable,
    nb_sl_price_calc: Callable,
    nb_strat_evaluate: Callable,
    nb_strat_get_current_ind_settings: Callable,
    nb_strat_get_ind_set_str: Callable,
    nb_strat_ind_creator: Callable,
    nb_tp_calculator: Callable,
    nb_tp_hit_bool: Callable,
    nb_zero_or_entry_calc: Callable,
    static_os: StaticOrderSettings,
    stringer: list,
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

    indicator_settings = nb_strat_get_current_ind_settings(
        ind_set_index=ind_set_index,
        logger=logger,
    )

    logger("nb_simulate.py - nb_run_backtest() - Indicator settings index=" + str(ind_set_index))
    logger(nb_strat_get_ind_set_str(indicator_settings=indicator_settings, stringer=stringer))
    dynamic_order_settings = nb_get_dos(
        dos_cart_arrays=dos_cart_arrays,
        dos_index=dos_index,
    )
    logger("nb_simulate.py - nb_run_backtest() - Dynamic Order settings index=" + str(dos_index))
    logger(
        "nb_simulate.py - nb_run_backtest() - Created Dynamic Order Settings"
        + "\nmax_equity_risk_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.max_equity_risk_pct * 100, 3))
        + "\nmax_trades= "
        + str(dynamic_order_settings.max_trades)
        + "\nrisk_account_pct_size= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.risk_account_pct_size * 100, 3))
        + "\nrisk_reward= "
        + stringer[StringerFuncType.float_to_str](dynamic_order_settings.risk_reward)
        + "\nsl_based_on_add_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.sl_based_on_add_pct * 100, 3))
        + "\nsl_based_on_lookback= "
        + str(dynamic_order_settings.sl_based_on_lookback)
        + "\nsl_bcb_type= "
        + stringer[StringerFuncType.candle_body_str](dynamic_order_settings.sl_bcb_type)
        + "\nsl_to_be_cb_type= "
        + stringer[StringerFuncType.candle_body_str](dynamic_order_settings.sl_to_be_cb_type)
        + "\nsl_to_be_when_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.sl_to_be_when_pct * 100, 3))
        + "\ntrail_sl_bcb_type= "
        + stringer[StringerFuncType.candle_body_str](dynamic_order_settings.trail_sl_bcb_type)
        + "\ntrail_sl_by_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.trail_sl_by_pct * 100, 3))
        + "\ntrail_sl_when_pct= "
        + stringer[StringerFuncType.float_to_str](round(dynamic_order_settings.trail_sl_when_pct * 100, 3))
    )

    logger("nb_simulate.py - nb_run_backtest() - Starting Bar=" + str(static_os.starting_bar))

    account_state, order_result = nb_create_ao(
        starting_equity=static_os.starting_equity,
    )
    logger("nb_sim_ordder_records.py - nb_run_backtest() - account state order results pnl array all set to default")
    total_bars = candles.shape[0]
    order_records = np.empty(total_bars, dtype=or_dt)
    or_index = 0
    for bar_index in range(static_os.starting_bar - 1, total_bars):
        logger("\n\n")
        logger(
            (
                "nb_simulate.py - nb_run_backtest() - ind_idx="
                + str(ind_set_index)
                + " dos_idx="
                + str(dos_index)
                + " bar_idx="
                + str(bar_index)
                + " timestamp= "
                + stringer[StringerFuncType.log_datetime](candles[bar_index, CandleBodyType.Timestamp])
            )
        )

        if order_result.position_size_usd > 0:
            try:
                # checking if sl hit
                logger("nb_simulate.py - nb_run_backtest() - check_stop_loss_hit")
                sl_hit_bool = nb_checker_sl_hit(
                    current_candle=candles[bar_index, :],
                    logger=logger,
                    nb_sl_hit_bool=nb_sl_hit_bool,
                    sl_price=order_result.sl_price,
                    stringer=stringer,
                )
                if sl_hit_bool:
                    logger("nb_simulate.py - nb_run_backtest() - decrease_position")
                    account_state, order_result = nb_decrease_position(
                        average_entry=order_result.average_entry,
                        bar_index=bar_index,
                        dos_index=dos_index,
                        equity=account_state.equity,
                        exit_fee_pct=market_fee_pct,
                        exit_price=order_result.sl_price,
                        ind_set_index=ind_set_index,
                        logger=logger,
                        market_fee_pct=market_fee_pct,
                        nb_pnl_calc=nb_pnl_calc,
                        order_status=OrderStatus.StopLossFilled,
                        position_size_asset=order_result.position_size_asset,
                        stringer=stringer,
                        timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                    )
                    or_index = nb_fill_order_records(
                        account_state=account_state,
                        or_index=or_index,
                        order_result=order_result,
                        order_records=order_records[or_index],
                    )
                    raise DecreasePosition

                # checking if liq hit
                logger("nb_simulate.py - nb_run_backtest() - check_liq_hit")
                liq_hit_bool = nb_check_liq_hit(
                    current_candle=candles[bar_index, :],
                    liq_price=order_result.liq_price,
                    logger=logger,
                    nb_liq_hit_bool=nb_liq_hit_bool,
                    stringer=stringer,
                )
                if liq_hit_bool:
                    logger("nb_simulate.py - nb_run_backtest() - decrease_position")
                    account_state, order_result = nb_decrease_position(
                        average_entry=order_result.average_entry,
                        bar_index=bar_index,
                        dos_index=dos_index,
                        equity=account_state.equity,
                        exit_fee_pct=market_fee_pct,
                        exit_price=order_result.liq_price,
                        ind_set_index=ind_set_index,
                        logger=logger,
                        market_fee_pct=market_fee_pct,
                        nb_pnl_calc=nb_pnl_calc,
                        order_status=OrderStatus.LiquidationFilled,
                        position_size_asset=order_result.position_size_asset,
                        stringer=stringer,
                        timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                    )
                    or_index = nb_fill_order_records(
                        account_state=account_state,
                        or_index=or_index,
                        order_result=order_result,
                        order_records=order_records[or_index],
                    )
                    raise DecreasePosition

                # checking if tp hit
                logger("nb_simulate.py - nb_run_backtest() - check_tp_hit")
                tp_hit_bool = nb_checker_tp_hit(
                    current_candle=candles[bar_index, :],
                    logger=logger,
                    nb_tp_hit_bool=nb_tp_hit_bool,
                    tp_price=order_result.tp_price,
                    stringer=stringer,
                )
                if tp_hit_bool:
                    logger("nb_simulate.py - nb_run_backtest() - decrease_position")
                    account_state, order_result = nb_decrease_position(
                        average_entry=order_result.average_entry,
                        bar_index=bar_index,
                        dos_index=dos_index,
                        equity=account_state.equity,
                        exit_fee_pct=exit_fee_pct,
                        exit_price=order_result.tp_price,
                        ind_set_index=ind_set_index,
                        logger=logger,
                        market_fee_pct=market_fee_pct,
                        nb_pnl_calc=nb_pnl_calc,
                        order_status=OrderStatus.TakeProfitFilled,
                        position_size_asset=order_result.position_size_asset,
                        stringer=stringer,
                        timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                    )
                    or_index = nb_fill_order_records(
                        account_state=account_state,
                        or_index=or_index,
                        order_result=order_result,
                        order_records=order_records[or_index],
                    )
                    raise DecreasePosition

                # checking to move stop loss

                logger("nb_simulate.py - nb_run_backtest() - check_move_stop_loss_to_be")
                temp_sl, temp_sl_pct = nb_checker_sl_to_be(
                    average_entry=order_result.average_entry,
                    can_move_sl_to_be=order_result.can_move_sl_to_be,
                    current_candle=candles[bar_index, :],
                    logger=logger,
                    market_fee_pct=market_fee_pct,
                    nb_move_sl_bool=nb_move_sl_bool,
                    nb_zero_or_entry_calc=nb_zero_or_entry_calc,
                    price_tick_step=price_tick_step,
                    sl_price=order_result.sl_price,
                    sl_to_be_cb_type=dynamic_order_settings.sl_to_be_cb_type,
                    sl_to_be_when_pct=dynamic_order_settings.sl_to_be_when_pct,
                    stringer=stringer,
                )
                if temp_sl > 0:
                    logger("nb_simulate.py - nb_run_backtest() - move_stop_loss")
                    account_state, order_result = nb_sl_mover(
                        account_state=account_state,
                        bar_index=bar_index,
                        can_move_sl_to_be=False,
                        dos_index=0,
                        ind_set_index=0,
                        logger=logger,
                        order_result=order_result,
                        order_status=OrderStatus.MovedSLToBE,
                        sl_price=temp_sl,
                        sl_pct=temp_sl_pct,
                        timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                    )
                    or_index = nb_fill_order_records(
                        account_state=account_state,
                        or_index=or_index,
                        order_result=order_result,
                        order_records=order_records[or_index],
                    )

                # Checking to move trailing stop loss

                logger("nb_simulate.py - nb_run_backtest() - check_move_trailing_stop_loss")
                temp_tsl, temp_tsl_pct = nb_checker_tsl(
                    average_entry=order_result.average_entry,
                    current_candle=candles[bar_index, :],
                    logger=logger,
                    nb_move_sl_bool=nb_move_sl_bool,
                    nb_sl_price_calc=nb_sl_price_calc,
                    price_tick_step=price_tick_step,
                    sl_price=order_result.sl_price,
                    stringer=stringer,
                    trail_sl_bcb_type=dynamic_order_settings.trail_sl_bcb_type,
                    trail_sl_by_pct=dynamic_order_settings.trail_sl_by_pct,
                    trail_sl_when_pct=dynamic_order_settings.trail_sl_when_pct,
                )
                if temp_tsl > 0:
                    logger("nb_simulate.py - nb_run_backtest() - move_stop_loss")
                    account_state, order_result = nb_sl_mover(
                        account_state=account_state,
                        bar_index=bar_index,
                        can_move_sl_to_be=False,
                        dos_index=dos_index,
                        ind_set_index=ind_set_index,
                        logger=logger,
                        order_result=order_result,
                        order_status=OrderStatus.MovedTSL,
                        sl_price=temp_tsl,
                        sl_pct=temp_tsl_pct,
                        timestamp=int(candles[bar_index, CandleBodyType.Timestamp]),
                    )
                    or_index = nb_fill_order_records(
                        account_state=account_state,
                        or_index=or_index,
                        order_result=order_result,
                        order_records=order_records[or_index],
                    )
            # except Exception as e:
            #     logger(
            #         f"nb_simulate.py - nb_run_backtest() - Checking hit Exception -> {e}"
            #     )
            #     pass
            except Exception:
                logger("nb_simulate.py - nb_run_backtest() - Exception hit during Checking")
                pass
        else:
            logger("nb_simulate.py - nb_run_backtest() - Not in a pos so not checking SL Liq or TP")
        logger("nb_simulate.py - nb_run_backtest() - strategy evaluate")
        eval_bool = nb_strat_evaluate(
            bar_index=bar_index,
            candle_group_size=static_os.starting_bar,
            candles=candles,
            indicator_settings=indicator_settings,
            nb_strat_ind_creator=nb_strat_ind_creator,
            logger=logger,
            stringer=stringer,
        )
        if eval_bool:
            try:
                logger("nb_simulate.py - nb_run_backtest() - calculate_stop_loss")
                sl_price = nb_sl_calculator(
                    bar_index=bar_index,
                    candles=candles,
                    logger=logger,
                    nb_sl_bcb_price_getter=nb_sl_bcb_price_getter,
                    nb_sl_price_calc=nb_sl_price_calc,
                    price_tick_step=price_tick_step,
                    sl_based_on_add_pct=dynamic_order_settings.sl_based_on_add_pct,
                    sl_based_on_lookback=dynamic_order_settings.sl_based_on_lookback,
                    sl_bcb_type=CandleBodyType.High,
                    stringer=stringer,
                )

                logger("nb_simulate.py - nb_run_backtest() - calculate_increase_position")
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
                ) = nb_inc_pos_calculator(
                    acc_ex_other=AccExOther(
                        equity=account_state.equity,
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
                    nb_entry_calc_p=nb_entry_calc_p,
                    nb_entry_calc_np=nb_entry_calc_np,
                )

                logger("nb_simulate.py - nb_run_backtest() - calculate_leverage")
                (
                    available_balance,
                    cash_borrowed,
                    cash_used,
                    leverage,
                    liq_price,
                ) = nb_lev_calculator(
                    lev_acc_ex_other=LevAccExOther(
                        available_balance=account_state.available_balance,
                        cash_borrowed=account_state.cash_borrowed,
                        cash_used=account_state.cash_used,
                        leverage_tick_step=leverage_tick_step,
                        market_fee_pct=market_fee_pct,
                        max_leverage=max_leverage,
                        min_leverage=min_leverage,
                        mmr_pct=mmr_pct,
                        price_tick_step=price_tick_step,
                    ),
                    lev_order_info=LevOrderInfo(
                        average_entry=average_entry,
                        position_size_asset=position_size_asset,
                        position_size_usd=position_size_usd,
                        sl_price=sl_price,
                        static_leverage=static_os.static_leverage,
                    ),
                    logger=logger,
                    nb_calc_dynamic_lev=nb_calc_dynamic_lev,
                    nb_get_bankruptcy_price=nb_get_bankruptcy_price,
                    nb_get_liq_price=nb_get_liq_price,
                    stringer=stringer,
                )

                logger("nb_simulate.py - nb_run_backtest() - calculate_take_profit")
                (
                    can_move_sl_to_be,
                    tp_price,
                    tp_pct,
                ) = nb_tp_calculator(
                    average_entry=average_entry,
                    logger=logger,
                    market_fee_pct=market_fee_pct,
                    nb_get_tp_price=nb_get_tp_price,
                    position_size_usd=position_size_usd,
                    possible_loss=possible_loss,
                    price_tick_step=price_tick_step,
                    risk_reward=dynamic_order_settings.risk_reward,
                    stringer=stringer,
                    tp_fee_pct=exit_fee_pct,
                )

                logger("nb_simulate.py - nb_run_backtest() - Recorded Trade")
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
                or_index = nb_fill_order_records(
                    account_state=account_state,
                    or_index=or_index,
                    order_result=order_result,
                    order_records=order_records[or_index],
                )
                logger("nb_simulate.py - nb_run_backtest() - Account State OrderResult")
            # except Exception as e:
            #     print(f"nb_simulate.py - nb_run_backtest() - Exception hit in eval strat -> {e}")
            #     pass
            except Exception:
                logger("nb_simulate.py - nb_run_backtest() - Exception hit in eval strat")
                pass
    return order_records[:or_index], indicator_settings, dynamic_order_settings
