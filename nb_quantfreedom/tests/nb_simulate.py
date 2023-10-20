import numpy as np
import pandas as pd
from numba import njit
import logging
from nb_quantfreedom.nb_custom_logger import CustomLogger, nb_NoLogs, nb_PrintLogs, nb_RegularLogs

from nb_quantfreedom.nb_helper_funcs import get_to_the_upside_nb, nb_get_dos
from nb_quantfreedom.nb_enums import (
    BacktestSettings,
    CandleBodyType,
    CandleProcessingType,
    DecreasePosition,
    DynamicOrderSettingsArrays,
    ExchangeSettings,
    IncreasePositionType,
    LeverageStrategyType,
    LoggerSettings,
    LongOrShortType,
    MoveStopLoss,
    OrderResult,
    OrderStatus,
    PriceGetterType,
    RejectedOrder,
    ZeroOrEntryType,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
    StaticOrderSettings,
    ZeroOrEntryType,
    strat_df_array_dt,
)
from nb_quantfreedom.nb_order_handler.nb_decrease_position import nb_DecreasePosition, nb_Long_DP
from nb_quantfreedom.nb_order_handler.nb_increase_position import (
    nb_IncreasePosition,
    nb_Long_RPAandSLB,
    nb_Long_SEP,
)
from nb_quantfreedom.nb_order_handler.nb_leverage import (
    nb_Leverage,
    nb_Long_DLev,
    nb_Long_Leverage,
    nb_Long_SLev,
)
from nb_quantfreedom.nb_order_handler.nb_class_helpers import (
    nb_GetMaxPrice,
    nb_GetMinPrice,
    nb_Long_SLToEntry,
    nb_Long_SLToZero,
    nb_PriceGetter,
    nb_ZeroOrEntry,
)

from nb_quantfreedom.nb_order_handler.nb_stop_loss import (
    nb_Long_SLBCB,
    nb_Long_StopLoss,
    nb_MoveSL,
    nb_StopLoss,
)
from nb_quantfreedom.nb_order_handler.nb_take_profit import (
    nb_Long_RR,
    nb_Long_TPHitReg,
    nb_TakeProfit,
)
from nb_quantfreedom.strategies.nb_strategy import (
    nb_BacktestInd,
    nb_CreateInd,
    nb_Strategy,
    nb_TradingInd,
)


@njit(cache=True)
def nb_tester(
    backtest_settings: BacktestSettings,
    candles: np.array,
    dos_cart_arrays: DynamicOrderSettingsArrays,
    exchange_settings: ExchangeSettings,
    exit_fee_pct: float,
    logger: CustomLogger,
    starting_equity: float,
    static_os: StaticOrderSettings,
    strategy: nb_Strategy,
    # Logger
):
    # Creating Settings Vars
    total_order_settings = dos_cart_arrays[0].size

    total_indicator_settings = strategy.get_total_ind_settings()

    total_bars = candles.shape[0]

    # logger.infoing out total numbers of things
    logger.log_info("Starting the backtest now ... and also here are some stats for your backtest.\n")
    logger.log_info("Total indicator settings to test: " + str(total_indicator_settings))
    logger.log_info("Total order settings to test: " + str(total_order_settings))
    logger.log_info(
        "Total combinations of settings to test: " + str(int(total_indicator_settings * total_order_settings))
    )
    logger.log_info("\nTotal candles: " + str(total_bars))
    logger.log_info("Total candles to test: " + str(int(total_indicator_settings * total_order_settings * total_bars)))

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
        logger.log_info("Indicator settings index= " + str(ind_set_index))
        indicator_settings = strategy.nb_get_current_ind_settings(
            ind_set_index=ind_set_index,
            logger=logger,
        )
        for dos_index in range(total_order_settings):
            logger.log_info("Order settings index= " + str(dos_index))
            dynamic_order_settings = nb_get_dos(
                dos_cart_arrays=dos_cart_arrays,
                dos_index=dos_index,
            )
            print(dynamic_order_settings)
            logger.log_info("Created Order class")

            starting_bar = dynamic_order_settings.num_candles - 1
            logger.log_info("starting bar " + str(starting_bar))
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
            logger.log_debug(order_result)
            pnl_array = np.full(shape=round(total_bars / 3), fill_value=np.nan)
            filled_pnl_counter = 0

            total_fees_paid = 0
            at_max_entries = False

            for bar_index in range(starting_bar, total_bars):
                logger.log_info(
                    "ind_idx=ind_set_index:,} dos_idx=dos_index:,} bar_idx=bar_index:,} timestamp=timestamp}"
                )

    return 0
