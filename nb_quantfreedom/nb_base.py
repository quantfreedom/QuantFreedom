import numpy as np
from numba import typed
import pandas as pd

from nb_quantfreedom.nb_custom_logger import *
from nb_quantfreedom.nb_enums import (
    BacktestSettings,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    IncreasePositionType,
    LeverageStrategyType,
    LoggerType,
    LongOrShortType,
    PriceGetterType,
    StaticOrderSettings,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
)
from nb_quantfreedom.nb_helper_funcs import (
    max_price_getter,
    min_price_getter,
    sl_to_entry,
    sl_to_z_e_pass,
    long_sl_to_zero,
)
from nb_quantfreedom.nb_order_handler.nb_decrease_position import decrease_position
from nb_quantfreedom.nb_order_handler.nb_increase_position import long_min_amount, long_rpa_slbcb
from nb_quantfreedom.nb_order_handler.nb_leverage import long_check_liq_hit, long_dynamic_lev, long_static_lev
from nb_quantfreedom.nb_order_handler.nb_stop_loss import (
    long_c_sl_hit,
    long_cm_sl_to_be,
    long_cm_sl_to_be_pass,
    long_cm_tsl,
    long_cm_tsl_pass,
    long_sl_bcb,
    move_stop_loss,
    move_stop_loss_pass,
)
from nb_quantfreedom.nb_order_handler.nb_take_profit import long_c_tp_hit_regular, long_tp_rr
from nb_quantfreedom.nb_simulate import run_backtest


def final_bt_df_only(
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
    log_func_type = types.void(types.unicode_type)
    log_func_list = typed.List.empty_list(log_func_type.as_type())

    str_func_type = types.unicode_type(types.float64)
    str_func_list = typed.List.empty_list(str_func_type.as_type())
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

    if logger_type == LoggerType.Print:
        log_func_list.append(print_log_debug)
        log_func_list.append(print_log_info)
        log_func_list.append(print_log_warning)
        log_func_list.append(print_log_error)

        str_func_list.append(print_float_to_str)
        str_func_list.append(print_log_datetime)
        str_func_list.append(print_candle_body_str)
        str_func_list.append(print_z_or_e_str)
        str_func_list.append(print_or_to_str)

    elif logger_type == LoggerType.File:
        set_loggers()
        log_func_list.append(file_log_debug)
        log_func_list.append(file_log_info)
        log_func_list.append(file_log_warning)
        log_func_list.append(file_log_error)

        str_func_list.append(file_float_to_str)
        str_func_list.append(file_log_datetime)
        str_func_list.append(file_candle_body_str)
        str_func_list.append(file_z_or_e_str)
        str_func_list.append(file_or_to_str)

    elif logger_type == LoggerType.Pass:
        log_func_list.append(logger_pass)
        log_func_list.append(logger_pass)
        log_func_list.append(logger_pass)
        log_func_list.append(logger_pass)

        str_func_list.append(stringer_pass)
        str_func_list.append(stringer_pass)
        str_func_list.append(stringer_pass)
        str_func_list.append(stringer_pass)
        str_func_list.append(stringer_pass)

    else:
        raise Exception("You need to select the correct logger type")
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
    if static_os.long_or_short == LongOrShortType.Long:
        # Decrease Position
        dec_pos_calculator = decrease_position

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

        # stop loss calulator
        if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
            sl_calculator = long_sl_bcb
            checker_sl_hit = long_c_sl_hit
            if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
                sl_bcb_price_getter = min_price_getter
            elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
                sl_bcb_price_getter = max_price_getter

        # SL break even
        if static_os.sl_to_be_bool:
            checker_sl_to_be = long_cm_sl_to_be
            # setting up stop loss be zero or entry
            if static_os.z_or_e_type == ZeroOrEntryType.ZeroLoss:
                zero_or_entry_calc = long_sl_to_zero
            elif static_os.z_or_e_type == ZeroOrEntryType.AverageEntry:
                zero_or_entry_calc = sl_to_entry
        else:
            checker_sl_to_be = long_cm_sl_to_be_pass
            zero_or_entry_calc = sl_to_z_e_pass

        # Trailing stop loss
        if static_os.trail_sl_bool:
            checker_tsl = long_cm_tsl
        else:
            checker_tsl = long_cm_tsl_pass

        if static_os.trail_sl_bool or static_os.sl_to_be_bool:
            sl_mover = move_stop_loss
        else:
            sl_mover = move_stop_loss_pass

        """
        #########################################
        #########################################
        #########################################
                    Increase position
                    Increase position
                    Increase position
        #########################################
        #########################################
        #########################################
        """

        if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
            if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
                inc_pos_calculator = long_rpa_slbcb

            elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
                inc_pos_calculator = long_min_amount

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
    print("Total indicator settings to test: " + str(total_indicator_settings))
    print("Total order settings to test: " + str(total_order_settings))
    print("Total combinations of settings to test: " + str(int(total_indicator_settings * total_order_settings)))
    print("Total candles: " + str(total_bars))
    print("Total candles to test: " + str(int(total_indicator_settings * total_order_settings * total_bars)))

    strategy_result_records = run_backtest(
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
