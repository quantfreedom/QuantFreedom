import numpy as np
import pandas as pd
from quantfreedom.enums import (
    BacktestSettings,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    StaticOrderSettings,
    StaticOrderSettings,
    OrderStatus,
    DecreasePosition,
    StopLossStrategyType,
    LeverageStrategyType,
    IncreasePositionType,
    TakeProfitStrategyType,
    strat_df_array_dt,
)
from numba import njit, typed, types
from quantfreedom.helper_funcs import dos_cart_product
from quantfreedom.nb_funcs.nb_custom_logger import *
from quantfreedom.nb_funcs.nb_helper_funcs import nb_float_to_str, nb_get_dos, nb_get_qf_score
from quantfreedom.nb_funcs.nb_order_handler.nb_decrease_position import *
from quantfreedom.nb_funcs.nb_order_handler.nb_increase_position import *
from quantfreedom.nb_funcs.nb_order_handler.nb_leverage import *
from quantfreedom.nb_funcs.nb_order_handler.nb_stop_loss import *
from quantfreedom.nb_funcs.nb_order_handler.nb_take_profit import *


@njit(cache=True)
def nb_create_ao(
    starting_equity: float,
):
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
    return account_state, order_result


def nb_sim_df_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    long_short: str,
    nb_strat_get_current_ind_settings,
    nb_strat_get_total_ind_settings,
    nb_strat_get_ind_set_str,
    nb_strat_ind_creator,
    nb_strat_evaluate,
    static_os: StaticOrderSettings,
):
    dos_cart_arrays = dos_cart_product(
        dos_arrays=dos_arrays,
    )

    # Creating Settings Vars
    total_order_settings = dos_cart_arrays[0].size

    total_indicator_settings = nb_strat_get_total_ind_settings()

    total_bars = candles.shape[0]
    """
    #########################################
    #########################################
    #########################################
                    Logger
                    Logger
                    Logger
    #########################################
    #########################################
    #########################################
    """
    log_func_type = types.void(types.unicode_type)
    logger = typed.List.empty_list(log_func_type.as_type())

    str_func_type = types.unicode_type(types.float64)
    stringer = typed.List.empty_list(str_func_type.as_type())

    if static_os.logger_bool:
        logger.append(nb_log_debug)
        logger.append(nb_log_info)
        logger.append(nb_log_warning)
        logger.append(nb_log_error)

        stringer.append(nb_float_to_str)
        stringer.append(nb_log_datetime)
        stringer.append(nb_candle_body_str)
        stringer.append(nb_z_or_e_str)
        stringer.append(nb_os_to_str)

    else:
        logger.append(nb_logger_pass)
        logger.append(nb_logger_pass)
        logger.append(nb_logger_pass)
        logger.append(nb_logger_pass)

        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)

    # logger.infoing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings to test: {total_order_settings:,}")
    print(f"Total combinations of settings to test: {total_indicator_settings * total_order_settings:,}")
    print(f"Total candles: {total_bars:,}")
    print(f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}")

    strategy_result_records = nb_run_df_backtest(
        backtest_settings=backtest_settings,
        candles=candles,
        dos_cart_arrays=dos_cart_arrays,
        exchange_settings=exchange_settings,
        logger=logger,
        long_short=long_short,
        nb_strat_evaluate=nb_strat_evaluate,
        nb_strat_get_current_ind_settings=nb_strat_get_current_ind_settings,
        nb_strat_get_ind_set_str=nb_strat_get_ind_set_str,
        nb_strat_ind_creator=nb_strat_ind_creator,
        static_os=static_os,
        stringer=stringer,
        total_bars=total_bars,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
    )
    return pd.DataFrame(strategy_result_records)


@njit(cache=True)
def nb_run_df_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    logger,
    long_short: str,
    nb_strat_get_current_ind_settings,
    nb_strat_get_ind_set_str,
    nb_strat_ind_creator,
    nb_strat_evaluate,
    static_os: StaticOrderSettings,
    stringer,
    total_bars: int,
    total_indicator_settings: int,
    total_order_settings: int,
):
    """
    #########################################
    #########################################
    #########################################
                    Trading
                    Trading
                    Trading
    #########################################
    #########################################
    #########################################
    """
    if long_short == "long":
        # stop loss
        nb_sl_hit_bool = nb_long_sl_hit_bool
        nb_move_sl_bool = nb_num_greater_than_num
        nb_sl_price_calc = nb_long_sl_price_calc

        # increase position
        nb_entry_calc_p = nb_long_entry_size_p
        nb_entry_calc_np = nb_long_entry_size_np

        # leverage
        nb_calc_dynamic_lev = nb_long_calc_dynamic_lev
        nb_get_liq_price = nb_long_get_liq_price
        nb_get_bankruptcy_price = nb_long_get_bankruptcy_price
        nb_liq_hit_bool = nb_long_liq_hit_bool

        # Take Profit
        nb_get_tp_price = nb_long_tp_price
        nb_tp_hit_bool = nb_long_tp_hit_bool

        # Decrease position
        nb_pnl_calc = nb_long_pnl_calc

    elif long_short == "short":
        # stop loss
        nb_sl_hit_bool = nb_short_sl_hit_bool
        nb_move_sl_bool = nb_num_less_than_num
        nb_sl_price_calc = nb_short_sl_price_calc

        # increase position
        nb_entry_calc_p = nb_short_entry_size_p
        nb_entry_calc_np = nb_short_entry_size_np

        # leverage
        nb_calc_dynamic_lev = nb_short_calc_dynamic_lev
        nb_get_liq_price = nb_short_get_liq_price
        nb_get_bankruptcy_price = nb_short_get_bankruptcy_price
        nb_liq_hit_bool = nb_short_liq_hit_bool

        # take profit
        nb_get_tp_price = nb_short_tp_price
        nb_tp_hit_bool = nb_short_tp_hit_bool

        # Decrease position
        nb_pnl_calc = nb_short_pnl_calc

    """
    #########################################
    #########################################
    #########################################
                    Stop Loss
                    Stop Loss
                    Stop Loss
    #########################################
    #########################################
    #########################################
    """

    # stop loss
    if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
        nb_sl_calculator = nb_sl_based_on_candle_body
        nb_checker_sl_hit = nb_check_sl_hit
        if static_os.pg_min_max_sl_bcb == "min":
            nb_sl_bcb_price_getter = nb_min_price_getter
        elif static_os.pg_min_max_sl_bcb == "max":
            nb_sl_bcb_price_getter = nb_max_price_getter
        else:
            raise Exception("min or max are the only options for pg_min_max_sl_bcb")
    else:
        nb_sl_calculator = nb_sl_calculator_pass
        nb_checker_sl_hit = nb_check_sl_hit_pass
        nb_sl_bcb_price_getter = nb_price_getter_pass

    # SL break even
    if static_os.sl_to_be_bool:
        nb_checker_sl_to_be = nb_check_move_sl_to_be
        # setting up stop loss be zero or entry
        if static_os.z_or_e_type == "entry":
            nb_zero_or_entry_calc = nb_sl_to_entry
        if static_os.z_or_e_type == "zero":
            if long_short == "long":
                nb_zero_or_entry_calc = nb_long_sl_to_zero
            elif long_short == "short":
                nb_zero_or_entry_calc = nb_short_sl_to_zero
        else:
            raise Exception("zero or entry are the only options for z_or_e_type")
    else:
        nb_checker_sl_to_be = nb_cm_sl_to_be_pass
        nb_zero_or_entry_calc = nb_sl_to_z_e_pass

    # Trailing stop loss
    if static_os.trail_sl_bool:
        nb_checker_tsl = nb_check_move_tsl
    else:
        nb_checker_tsl = nb_cm_tsl_pass

    if static_os.trail_sl_bool or static_os.sl_to_be_bool:
        nb_sl_mover = nb_move_stop_loss
    else:
        nb_sl_mover = nb_move_stop_loss_pass

    # Increase Position
    if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
        if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
            nb_inc_pos_calculator = nb_rpa_slbcb
        elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
            nb_inc_pos_calculator = nb_min_asset_amount

    # Leverage
    if static_os.leverage_strategy_type == LeverageStrategyType.Dynamic:
        nb_lev_calculator = nb_dynamic_lev

    # Take Profit
    if static_os.tp_strategy_type == TakeProfitStrategyType.RiskReward:
        nb_tp_calculator = nb_tp_rr
        nb_checker_tp_hit = nb_c_tp_hit_regular

    if static_os.tp_fee_type == "market":
        exit_fee_pct = exchange_settings.market_fee_pct
    else:
        exit_fee_pct = exchange_settings.limit_fee_pct

    market_fee_pct = exchange_settings.market_fee_pct
    leverage_tick_step = exchange_settings.leverage_tick_step
    price_tick_step = exchange_settings.price_tick_step
    asset_tick_step = exchange_settings.asset_tick_step
    min_asset_size = exchange_settings.min_asset_size
    max_asset_size = exchange_settings.max_asset_size
    max_leverage = exchange_settings.max_leverage
    min_leverage = exchange_settings.min_leverage
    mmr_pct = exchange_settings.mmr_pct

    strategy_result_records = np.empty(
        backtest_settings.array_size,
        dtype=strat_df_array_dt,
    )
    result_records_filled = 0

    for ind_set_index in range(total_indicator_settings):
        indicator_settings = nb_strat_get_current_ind_settings(
            ind_set_index=ind_set_index,
            logger=logger,
        )

        for dos_index in range(total_order_settings):
            logger[LoggerFuncType.Info](
                "nb_simulate.py - nb_run_backtest() - Indicator settings index=" + str(ind_set_index)
            )
            logger[LoggerFuncType.Info](
                nb_strat_get_ind_set_str(indicator_settings=indicator_settings, stringer=stringer)
            )
            dynamic_order_settings = nb_get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )
            logger[LoggerFuncType.Info](
                "nb_simulate.py - nb_run_backtest() - Dynamic Order settings index=" + str(dos_index)
            )
            logger[LoggerFuncType.Info](
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

            logger[LoggerFuncType.Info](
                "nb_simulate.py - nb_run_backtest() - Starting Bar=" + str(static_os.starting_bar)
            )

            new_account_state, order_result = nb_create_ao(
                starting_equity=static_os.starting_equity,
            )

            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0

            total_fees_paid = 0
            logger[LoggerFuncType.Info](
                "nb_simulate.py - nb_run_backtest() - account state order results pnl array all set to default"
            )
            for bar_index in range(static_os.starting_bar - 1, total_bars):
                logger[LoggerFuncType.Info]("\n\n")
                logger[LoggerFuncType.Info](
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
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - check_stop_loss_hit")
                        sl_hit_bool = nb_checker_sl_hit(
                            current_candle=candles[bar_index, :],
                            logger=logger,
                            nb_sl_hit_bool=nb_sl_hit_bool,
                            sl_price=order_result.sl_price,
                            stringer=stringer,
                        )
                        if sl_hit_bool:
                            logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - decrease_position")
                            new_account_state, order_result = nb_decrease_position(
                                average_entry=order_result.average_entry,
                                bar_index=bar_index,
                                dos_index=dos_index,
                                equity=new_account_state.equity,
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
                            pnl_array[filled_pnl_counter] = new_account_state.realized_pnl
                            filled_pnl_counter += 1
                            total_fees_paid += new_account_state.fees_paid
                            raise DecreasePosition

                        # checking if liq hit
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - check_liq_hit")
                        new_liq_hit_bool = nb_check_liq_hit(
                            current_candle=candles[bar_index, :],
                            logger=logger,
                            nb_liq_hit_bool=nb_liq_hit_bool,
                            liq_price=order_result.liq_price,
                            stringer=stringer,
                        )
                        if new_liq_hit_bool:
                            logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - decrease_position")
                            new_account_state, order_result = nb_decrease_position(
                                average_entry=order_result.average_entry,
                                bar_index=bar_index,
                                dos_index=dos_index,
                                equity=new_account_state.equity,
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
                            pnl_array[filled_pnl_counter] = new_account_state.realized_pnl
                            filled_pnl_counter += 1
                            total_fees_paid += new_account_state.fees_paid
                            raise DecreasePosition

                        # checking if tp hit
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - check_tp_hit")
                        new_tp_hit_bool = nb_checker_tp_hit(
                            current_candle=candles[bar_index, :],
                            logger=logger,
                            nb_tp_hit_bool=nb_tp_hit_bool,
                            tp_price=order_result.tp_price,
                            stringer=stringer,
                        )
                        if new_tp_hit_bool:
                            logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - decrease_position")
                            new_account_state, order_result = nb_decrease_position(
                                average_entry=order_result.average_entry,
                                bar_index=bar_index,
                                dos_index=dos_index,
                                equity=new_account_state.equity,
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
                            pnl_array[filled_pnl_counter] = new_account_state.realized_pnl
                            filled_pnl_counter += 1
                            total_fees_paid += new_account_state.fees_paid
                            raise DecreasePosition

                        # checking to move stop loss

                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - check_move_stop_loss_to_be")
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
                            logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - move_stop_loss")
                            new_account_state, order_result = nb_sl_mover(
                                account_state=new_account_state,
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

                        # Checking to move trailing stop loss

                        logger[LoggerFuncType.Debug](
                            "nb_simulate.py - nb_run_backtest() - check_move_trailing_stop_loss"
                        )
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
                            logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - move_stop_loss")
                            new_account_state, order_result = nb_sl_mover(
                                account_state=new_account_state,
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
                    # except Exception as e:
                    #     logger[LoggerFuncType.Debug](
                    #         f"nb_simulate.py - nb_run_backtest() - Checking hit Exception -> {e}"
                    #     )
                    #     pass
                    except Exception:
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - Checking hit Exception")
                        pass
                else:
                    logger[LoggerFuncType.Debug](
                        "nb_simulate.py - nb_run_backtest() - Not in a pos so not checking SL Liq or TP"
                    )
                logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - strategy evaluate")
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
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - calculate_stop_loss")
                        new_sl_price = nb_sl_calculator(
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

                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - calculate_increase_posotion")
                        (
                            new_average_entry,
                            new_entry_price,
                            new_entry_size_asset,
                            new_entry_size_usd,
                            new_position_size_asset,
                            new_position_size_usd,
                            new_possible_loss,
                            new_total_trades,
                            new_sl_pct,
                        ) = nb_inc_pos_calculator(
                            acc_ex_other=AccExOther(
                                equity=new_account_state.equity,
                                asset_tick_step=asset_tick_step,
                                market_fee_pct=market_fee_pct,
                                max_asset_size=max_asset_size,
                                min_asset_size=min_asset_size,
                                possible_loss=new_account_state.possible_loss,
                                price_tick_step=price_tick_step,
                                total_trades=new_account_state.total_trades,
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
                                sl_price=new_sl_price,
                            ),
                            logger=logger,
                            stringer=stringer,
                            nb_entry_calc_p=nb_entry_calc_p,
                            nb_entry_calc_np=nb_entry_calc_np,
                        )

                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - calculate_leverage")
                        (
                            new_available_balance,
                            new_cash_borrowed,
                            new_cash_used,
                            new_leverage,
                            new_liq_price,
                        ) = nb_lev_calculator(
                            lev_acc_ex_other=LevAccExOther(
                                available_balance=new_account_state.available_balance,
                                cash_borrowed=new_account_state.cash_borrowed,
                                cash_used=new_account_state.cash_used,
                                leverage_tick_step=leverage_tick_step,
                                market_fee_pct=market_fee_pct,
                                max_leverage=max_leverage,
                                min_leverage=min_leverage,
                                mmr_pct=mmr_pct,
                                price_tick_step=price_tick_step,
                            ),
                            lev_order_info=LevOrderInfo(
                                average_entry=new_average_entry,
                                position_size_asset=new_position_size_asset,
                                position_size_usd=new_position_size_usd,
                                sl_price=new_sl_price,
                                static_leverage=static_os.static_leverage,
                            ),
                            logger=logger,
                            nb_calc_dynamic_lev=nb_calc_dynamic_lev,
                            nb_get_bankruptcy_price=nb_get_bankruptcy_price,
                            nb_get_liq_price=nb_get_liq_price,
                            stringer=stringer,
                        )

                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - calculate_take_profit")
                        (
                            new_can_move_sl_to_be,
                            new_tp_price,
                            new_tp_pct,
                        ) = nb_tp_calculator(
                            average_entry=new_average_entry,
                            logger=logger,
                            market_fee_pct=market_fee_pct,
                            nb_get_tp_price=nb_get_tp_price,
                            position_size_usd=new_position_size_usd,
                            possible_loss=new_possible_loss,
                            price_tick_step=price_tick_step,
                            risk_reward=dynamic_order_settings.risk_reward,
                            stringer=stringer,
                            tp_fee_pct=exit_fee_pct,
                        )

                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - Recorded Trade")
                        new_account_state = AccountState(
                            # where we are at
                            ind_set_index=ind_set_index,
                            dos_index=dos_index,
                            bar_index=bar_index + 1,  # put plus 1 because we need to place entry on next bar
                            timestamp=int(candles[bar_index + 1, CandleBodyType.Timestamp]),
                            # account info
                            available_balance=new_available_balance,
                            cash_borrowed=new_cash_borrowed,
                            cash_used=new_cash_used,
                            equity=new_account_state.equity,
                            fees_paid=0.0,
                            possible_loss=new_possible_loss,
                            realized_pnl=0.0,
                            total_trades=new_total_trades,
                        )
                        order_result = OrderResult(
                            average_entry=new_average_entry,
                            can_move_sl_to_be=new_can_move_sl_to_be,
                            entry_price=new_entry_price,
                            entry_size_asset=new_entry_size_asset,
                            entry_size_usd=new_entry_size_usd,
                            exit_price=0.0,
                            leverage=new_leverage,
                            liq_price=new_liq_price,
                            order_status=OrderStatus.EntryFilled,
                            position_size_asset=new_position_size_asset,
                            position_size_usd=new_position_size_usd,
                            sl_pct=new_sl_pct,
                            sl_price=new_sl_price,
                            tp_pct=new_tp_pct,
                            tp_price=new_tp_price,
                        )
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - Account State OrderResult")
                    # except Exception as e:
                    #     print(f"nb_simulate.py - nb_run_backtest() - Exception hit in eval strat -> {e}")
                    #     pass
                    except Exception:
                        logger[LoggerFuncType.Debug]("nb_simulate.py - nb_run_backtest() - Exception hit in eval strat")
                        pass
            # Checking if gains
            gains_pct = round(
                ((new_account_state.equity - static_os.starting_equity) / static_os.starting_equity) * 100, 3
            )
            wins_and_losses_array = pnl_array[~np.isnan(pnl_array)]
            total_trades_closed = wins_and_losses_array.size
            logger[LoggerFuncType.Info](
                "nb_simulate.py - nb_run_backtest() - Results from backtest\n"
                + "\nind_set_index= "
                + str(ind_set_index)
                + "\ndos_index= "
                + str(dos_index)
                + "\nStarting eq= "
                + stringer[StringerFuncType.float_to_str](static_os.starting_equity)
                + "\nEnding eq= "
                + stringer[StringerFuncType.float_to_str](new_account_state.equity)
                + "\nGains pct= "
                + stringer[StringerFuncType.float_to_str](gains_pct)
                + "\nTotal_trades= "
                + str(total_trades_closed)
                + "\n"
            )
            if total_trades_closed > 0 and gains_pct > backtest_settings.gains_pct_filter:
                if wins_and_losses_array.size > backtest_settings.total_trade_filter:
                    wins_and_losses_array_no_be = wins_and_losses_array[
                        (wins_and_losses_array < -0.009) | (wins_and_losses_array > 0.009)
                    ]
                    qf_score = nb_get_qf_score(
                        gains_pct=gains_pct,
                        wins_and_losses_array_no_be=wins_and_losses_array_no_be,
                    )

                    # Checking to the upside filter
                    if qf_score > backtest_settings.upside_filter:
                        win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
                        wins = np.count_nonzero(win_loss)
                        losses = win_loss.size - wins
                        win_rate = round(wins / win_loss.size * 100, 3)

                        total_pnl = wins_and_losses_array.sum()

                        # strat array
                        strategy_result_records[result_records_filled]["ind_set_idx"] = ind_set_index
                        strategy_result_records[result_records_filled]["dos_index"] = dos_index
                        strategy_result_records[result_records_filled]["total_trades"] = wins_and_losses_array.size
                        strategy_result_records[result_records_filled]["wins"] = wins
                        strategy_result_records[result_records_filled]["losses"] = losses
                        strategy_result_records[result_records_filled]["gains_pct"] = gains_pct
                        strategy_result_records[result_records_filled]["win_rate"] = win_rate
                        strategy_result_records[result_records_filled]["qf_score"] = qf_score
                        strategy_result_records[result_records_filled]["fees_paid"] = round(total_fees_paid, 3)
                        strategy_result_records[result_records_filled]["total_pnl"] = total_pnl
                        strategy_result_records[result_records_filled]["ending_eq"] = new_account_state.equity

                        result_records_filled += 1
            logger[LoggerFuncType.Info](
                "Starting New Loop\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            )
    return strategy_result_records[:result_records_filled]
