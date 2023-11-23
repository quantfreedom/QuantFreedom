import numpy as np
import pandas as pd
from numba import typed, types

from quantfreedom.enums import (
    BacktestSettings,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    IncreasePositionType,
    LeverageStrategyType,
    StaticOrderSettings,
    StopLossStrategyType,
    TakeProfitStrategyType,
)
from quantfreedom.helper_funcs import dos_cart_product
from quantfreedom.nb_funcs.nb_custom_logger import *
from quantfreedom.nb_funcs.nb_helper_funcs import get_data_for_plotting, nb_float_to_str, order_records_to_df
from quantfreedom.nb_funcs.nb_order_handler.nb_decrease_position import *
from quantfreedom.nb_funcs.nb_order_handler.nb_increase_position import *
from quantfreedom.nb_funcs.nb_order_handler.nb_leverage import *
from quantfreedom.nb_funcs.nb_order_handler.nb_stop_loss import *
from quantfreedom.nb_funcs.nb_order_handler.nb_take_profit import *
from quantfreedom.nb_funcs.nb_sim_df import nb_run_df_backtest
from quantfreedom.nb_funcs.nb_sim_or import nb_run_or_backtest
from quantfreedom.plotting.plotting_base import plot_or_results
from quantfreedom.utils import pretty_qf


def nb_sim_backtest(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    logger_bool: bool,
    long_short: str,
    nb_strat_evaluate: Callable,
    nb_strat_get_current_ind_settings: Callable,
    nb_strat_get_ind_set_str: Callable,
    nb_strat_get_total_ind_settings: Callable,
    nb_strat_ind_creator: Callable,
    static_os: StaticOrderSettings,
    dos_index: int = None,
    ind_set_index: int = None,
    plot_results: bool = False,
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

    str_func_type = types.unicode_type(types.float64)
    stringer: list = typed.List.empty_list(str_func_type.as_type())

    if logger_bool:
        logger = nb_logger

        stringer.append(nb_float_to_str)
        stringer.append(nb_log_datetime)
        stringer.append(nb_candle_body_str)
        stringer.append(nb_z_or_e_str)
        stringer.append(nb_os_to_str)

    else:
        logger = nb_logger_pass

        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)
        stringer.append(nb_stringer_pass)

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

    # logger.infoing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest.\n")

    if ind_set_index is not None and dos_index is not None:
        order_records, indicator_settings, dynamic_order_settings = nb_run_or_backtest(
            candles=candles,
            dos_cart_arrays=dos_cart_arrays,
            dos_index=dos_index,
            exchange_settings=exchange_settings,
            exit_fee_pct=exit_fee_pct,
            ind_set_index=ind_set_index,
            logger=logger,
            nb_calc_dynamic_lev=nb_calc_dynamic_lev,
            nb_checker_sl_hit=nb_checker_sl_hit,
            nb_checker_sl_to_be=nb_checker_sl_to_be,
            nb_checker_tp_hit=nb_checker_tp_hit,
            nb_checker_tsl=nb_checker_tsl,
            nb_entry_calc_np=nb_entry_calc_np,
            nb_entry_calc_p=nb_entry_calc_p,
            nb_get_bankruptcy_price=nb_get_bankruptcy_price,
            nb_get_liq_price=nb_get_liq_price,
            nb_get_tp_price=nb_get_tp_price,
            nb_inc_pos_calculator=nb_inc_pos_calculator,
            nb_lev_calculator=nb_lev_calculator,
            nb_liq_hit_bool=nb_liq_hit_bool,
            nb_move_sl_bool=nb_move_sl_bool,
            nb_pnl_calc=nb_pnl_calc,
            nb_sl_bcb_price_getter=nb_sl_bcb_price_getter,
            nb_sl_calculator=nb_sl_calculator,
            nb_sl_hit_bool=nb_sl_hit_bool,
            nb_sl_mover=nb_sl_mover,
            nb_sl_price_calc=nb_sl_price_calc,
            nb_strat_evaluate=nb_strat_evaluate,
            nb_strat_get_current_ind_settings=nb_strat_get_current_ind_settings,
            nb_strat_get_ind_set_str=nb_strat_get_ind_set_str,
            nb_strat_ind_creator=nb_strat_ind_creator,
            nb_tp_calculator=nb_tp_calculator,
            nb_tp_hit_bool=nb_tp_hit_bool,
            nb_zero_or_entry_calc=nb_zero_or_entry_calc,
            static_os=static_os,
            stringer=stringer,
        )
        pretty_qf(indicator_settings)
        pretty_qf(dynamic_order_settings)
        order_records_df = order_records_to_df(order_records)
        data = get_data_for_plotting(order_records_df, candles)
        if plot_results:
            plot_or_results(candles=candles, order_records_df=order_records_df)
        return order_records_df, data
    elif ind_set_index is None and dos_index is None:
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
            exit_fee_pct=exit_fee_pct,
            logger=logger,
            nb_calc_dynamic_lev=nb_calc_dynamic_lev,
            nb_checker_sl_hit=nb_checker_sl_hit,
            nb_checker_sl_to_be=nb_checker_sl_to_be,
            nb_checker_tp_hit=nb_checker_tp_hit,
            nb_checker_tsl=nb_checker_tsl,
            nb_entry_calc_np=nb_entry_calc_np,
            nb_entry_calc_p=nb_entry_calc_p,
            nb_get_bankruptcy_price=nb_get_bankruptcy_price,
            nb_get_liq_price=nb_get_liq_price,
            nb_get_tp_price=nb_get_tp_price,
            nb_inc_pos_calculator=nb_inc_pos_calculator,
            nb_lev_calculator=nb_lev_calculator,
            nb_liq_hit_bool=nb_liq_hit_bool,
            nb_move_sl_bool=nb_move_sl_bool,
            nb_pnl_calc=nb_pnl_calc,
            nb_sl_bcb_price_getter=nb_sl_bcb_price_getter,
            nb_sl_calculator=nb_sl_calculator,
            nb_sl_hit_bool=nb_sl_hit_bool,
            nb_sl_mover=nb_sl_mover,
            nb_sl_price_calc=nb_sl_price_calc,
            nb_strat_evaluate=nb_strat_evaluate,
            nb_strat_get_current_ind_settings=nb_strat_get_current_ind_settings,
            nb_strat_get_ind_set_str=nb_strat_get_ind_set_str,
            nb_strat_ind_creator=nb_strat_ind_creator,
            nb_tp_calculator=nb_tp_calculator,
            nb_tp_hit_bool=nb_tp_hit_bool,
            nb_zero_or_entry_calc=nb_zero_or_entry_calc,
            static_os=static_os,
            stringer=stringer,
            total_bars=total_bars,
            total_indicator_settings=total_indicator_settings,
            total_order_settings=total_order_settings,
        )
        return pd.DataFrame(strategy_result_records)
    else:
        raise Exception("You need to send both ind set index and dos index or neither")
