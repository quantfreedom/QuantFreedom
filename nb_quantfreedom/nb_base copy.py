# import numpy as np
# import pandas as pd
# from nb_quantfreedom.nb_custom_logger import FileLogs, PassLogs, PrintLogs

# from nb_quantfreedom.nb_enums import *
# from nb_quantfreedom.nb_order_handler.nb_class_helpers import (
#     ZeroOrEntryNB,
#     nb_GetMaxPrice,
#     nb_GetMinPrice,
#     nb_Long_SLToEntry,
#     nb_Long_SLToZero,
#     PGPass,
# )
# from nb_quantfreedom.nb_order_handler.nb_decrease_position import nb_Long_DP
# from nb_quantfreedom.nb_order_handler.nb_increase_position import nb_Long_RPAandSLB, nb_Long_SEP
# from nb_quantfreedom.nb_order_handler.nb_leverage import nb_Long_DLev, nb_Long_Leverage, nb_Long_SLev
# from nb_quantfreedom.nb_order_handler.nb_stop_loss import Long_SLBCB, Long_StopLoss, MoveSL, SLPass, PGPass
# from nb_quantfreedom.nb_order_handler.nb_take_profit import nb_Long_RR, nb_Long_TPHitReg
# from nb_quantfreedom.nb_simulate import nb_run_backtest
# from nb_quantfreedom.strategies.nb_strategy import nb_BacktestInd, nb_Strategy
# from numba import njit


# def backtest_df_only(
#     backtest_settings: BacktestSettings,
#     candles: np.array,
#     dos_cart_arrays: DynamicOrderSettingsArrays,
#     exchange_settings: ExchangeSettings,
#     logger_type: LoggerType,
#     starting_equity: float,
#     static_os: StaticOrderSettings,
#     strategy: nb_Strategy,
#     ind_creator: nb_BacktestInd,
# ) -> tuple[pd.DataFrame, pd.DataFrame]:
#     """
#     #########################################
#     #########################################
#     #########################################
#                     Logger
#                     Logger
#                     Logger
#     #########################################
#     #########################################
#     #########################################
#     """

#     if logger_type == LoggerType.Print:
#         logger = PrintLogs()

#     elif logger_type == LoggerType.File:
#         logger = FileLogs()
#     else:
#         logger = PassLogs()

#     """
#     #########################################
#     #########################################
#     #########################################
#                     Trading
#                     Trading
#                     Trading
#     #########################################
#     #########################################
#     #########################################
#     """
#     if static_os.long_or_short == LongOrShortType.Long:
#         # Decrease Position
#         dec_pos_calculator = nb_Long_DP()

#         """
#         #########################################
#         #########################################
#         #########################################
#                         Stop Loss
#                         Stop Loss
#                         Stop Loss
#         #########################################
#         #########################################
#         #########################################
#         """

#         # setting up stop loss calulator
#         if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
#             sl_calculator = Long_SLBCB()
#             checker_sl_hit = Long_StopLoss()
#             if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
#                 sl_bcb_price_getter = nb_GetMinPrice()
#             elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
#                 sl_bcb_price_getter = nb_GetMaxPrice()
#         elif static_os.sl_strategy_type == StopLossStrategyType.Nothing:
#             sl_calculator = PGPass()
#             sl_bcb_price_getter = PGPass()

#         # setting up stop loss break even checker
#         if static_os.sl_to_be_bool:
#             checker_sl_to_be = Long_StopLoss()
#             # setting up stop loss be zero or entry
#             if static_os.z_or_e_type == ZeroOrEntryType.ZeroLoss:
#                 set_z_e = nb_Long_SLToZero()
#             elif static_os.z_or_e_type == ZeroOrEntryType.AverageEntry:
#                 set_z_e = nb_Long_SLToEntry()
#         else:
#             checker_sl_to_be = PGPass()
#             set_z_e = ZeroOrEntryNB()

#         # setting up stop loss break even checker
#         if static_os.trail_sl_bool:
#             checker_tsl = Long_StopLoss()
#         else:
#             checker_tsl = PGPass()

#         if static_os.trail_sl_bool or static_os.sl_to_be_bool:
#             sl_mover = MoveSL()
#         else:
#             sl_mover = PGPass()

#         """
#         #########################################
#         #########################################
#         #########################################
#                     Increase position
#                     Increase position
#                     Increase position
#         #########################################
#         #########################################
#         #########################################
#         """

#         if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
#             if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
#                 inc_pos_calculator = nb_Long_RPAandSLB()

#             elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
#                 inc_pos_calculator = nb_Long_SEP()

#         """
#         #########################################
#         #########################################
#         #########################################
#                         Leverage
#                         Leverage
#                         Leverage
#         #########################################
#         #########################################
#         #########################################
#         """

#         if static_os.leverage_strategy_type == LeverageStrategyType.Dynamic:
#             lev_calculator = nb_Long_DLev()
#         else:
#             lev_calculator = nb_Long_SLev()

#         checker_liq_hit = nb_Long_Leverage()
#         """
#         #########################################
#         #########################################
#         #########################################
#                         Take Profit
#                         Take Profit
#                         Take Profit
#         #########################################
#         #########################################
#         #########################################
#         """

#         if static_os.tp_strategy_type == TakeProfitStrategyType.RiskReward:
#             tp_calculator = nb_Long_RR()
#             checker_tp_hit = nb_Long_TPHitReg()
#         elif static_os.tp_strategy_type == TakeProfitStrategyType.Provided:
#             pass
#     """
#     #########################################
#     #########################################
#     #########################################
#                 Other Settings
#                 Other Settings
#                 Other Settings
#     #########################################
#     #########################################
#     #########################################
#     """

#     if static_os.tp_fee_type == TakeProfitFeeType.Market:
#         exit_fee_pct = exchange_settings.market_fee_pct
#     else:
#         exit_fee_pct = exchange_settings.limit_fee_pct
#     """
#     #########################################
#     #########################################
#     #########################################
#                 End User Setup
#                 End User Setup
#                 End User Setup
#     #########################################
#     #########################################
#     #########################################
#     """
#     # Creating Settings Vars
#     total_order_settings = dos_cart_arrays[0].size

#     total_indicator_settings = strategy.get_total_ind_settings()

#     total_bars = candles.shape[0]

#     # logger.infoing out total numbers of things
#     print("Starting the backtest now ... and also here are some stats for your backtest.\n")
#     print("Total indicator settings to test: " + str(total_indicator_settings))
#     print("Total order settings to test: " + str(total_order_settings))
#     print("Total combinations of settings to test: " + str(int(total_indicator_settings * total_order_settings)))
#     print("Total candles: " + str(total_bars))
#     print("Total candles to test: " + str(int(total_indicator_settings * total_order_settings * total_bars)))

#     strategy_result_records = nb_run_backtest(
#         backtest_settings=backtest_settings,
#         candles=candles,
#         checker_liq_hit=checker_liq_hit,
#         checker_sl_hit=checker_sl_hit,
#         checker_sl_to_be=checker_sl_to_be,
#         checker_tp_hit=checker_tp_hit,
#         checker_tsl=checker_tsl,
#         dec_pos_calculator=dec_pos_calculator,
#         dos_cart_arrays=dos_cart_arrays,
#         exchange_settings=exchange_settings,
#         exit_fee_pct=exit_fee_pct,
#         inc_pos_calculator=inc_pos_calculator,
#         lev_calculator=lev_calculator,
#         logger=logger,
#         set_z_e=set_z_e,
#         sl_bcb_price_getter=sl_bcb_price_getter,
#         sl_calculator=sl_calculator,
#         sl_mover=sl_mover,
#         starting_equity=starting_equity,
#         strategy=strategy,
#         ind_creator=ind_creator,
#         total_bars=total_bars,
#         total_indicator_settings=total_indicator_settings,
#         total_order_settings=total_order_settings,
#         tp_calculator=tp_calculator,
#     )
#     return strategy_result_records


# @njit(cache=True)
# def get_classes(
#     backtest_settings: BacktestSettings,
#     candles: np.array,
#     dos_cart_arrays: DynamicOrderSettingsArrays,
#     exchange_settings: ExchangeSettings,
#     logger_type: LoggerType,
#     starting_equity: float,
#     static_os: StaticOrderSettings,
#     strategy: nb_Strategy,
#     ind_creator: nb_BacktestInd,
# ) -> tuple[pd.DataFrame, pd.DataFrame]:
#     """
#     #########################################
#     #########################################
#     #########################################
#                     Logger
#                     Logger
#                     Logger
#     #########################################
#     #########################################
#     #########################################
#     """

#     if logger_type == LoggerType.Print:
#         logger = PrintLogs()

#     elif logger_type == LoggerType.File:
#         logger = FileLogs()
#         logger.set_loggers()
#     else:
#         logger = PassLogs()

#     """
#     #########################################
#     #########################################
#     #########################################
#                     Trading
#                     Trading
#                     Trading
#     #########################################
#     #########################################
#     #########################################
#     """
#     if static_os.long_or_short == LongOrShortType.Long:
#         # Decrease Position
#         dec_pos_calculator = nb_Long_DP()

#         """
#         #########################################
#         #########################################
#         #########################################
#                         Stop Loss
#                         Stop Loss
#                         Stop Loss
#         #########################################
#         #########################################
#         #########################################
#         """

#         # setting up stop loss calulator
#         if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
#             sl_calculator = Long_SLBCB()
#             checker_sl_hit = Long_StopLoss()
#             if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
#                 sl_bcb_price_getter = nb_GetMinPrice()
#             elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
#                 sl_bcb_price_getter = nb_GetMaxPrice()
#         elif static_os.sl_strategy_type == StopLossStrategyType.Nothing:
#             sl_calculator = SLPass()
#             # sl_bcb_price_getter = PGPass()

#         # setting up stop loss break even checker
#         if static_os.sl_to_be_bool:
#             checker_sl_to_be = Long_StopLoss()
#             # setting up stop loss be zero or entry
#             if static_os.z_or_e_type == ZeroOrEntryType.ZeroLoss:
#                 set_z_e = nb_Long_SLToZero()
#             elif static_os.z_or_e_type == ZeroOrEntryType.AverageEntry:
#                 set_z_e = nb_Long_SLToEntry()
#         else:
#             checker_sl_to_be = SLPass()
#             set_z_e = ZeroOrEntryNB()

#         # setting up stop loss break even checker
#         if static_os.trail_sl_bool:
#             checker_tsl = Long_StopLoss()
#         else:
#             checker_tsl = SLPass()

#         if static_os.trail_sl_bool or static_os.sl_to_be_bool:
#             sl_mover = MoveSL()
#         else:
#             sl_mover = SLPass()

#         """
#         #########################################
#         #########################################
#         #########################################
#                     Increase position
#                     Increase position
#                     Increase position
#         #########################################
#         #########################################
#         #########################################
#         """

#         if static_os.sl_strategy_type == StopLossStrategyType.SLBasedOnCandleBody:
#             if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
#                 inc_pos_calculator = nb_Long_RPAandSLB()

#             elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
#                 inc_pos_calculator = nb_Long_SEP()

#         """
#         #########################################
#         #########################################
#         #########################################
#                         Leverage
#                         Leverage
#                         Leverage
#         #########################################
#         #########################################
#         #########################################
#         """

#         if static_os.leverage_strategy_type == LeverageStrategyType.Dynamic:
#             lev_calculator = nb_Long_DLev()
#         else:
#             lev_calculator = nb_Long_SLev()

#         checker_liq_hit = nb_Long_Leverage()
#         """
#         #########################################
#         #########################################
#         #########################################
#                         Take Profit
#                         Take Profit
#                         Take Profit
#         #########################################
#         #########################################
#         #########################################
#         """

#         if static_os.tp_strategy_type == TakeProfitStrategyType.RiskReward:
#             tp_calculator = nb_Long_RR()
#             checker_tp_hit = nb_Long_TPHitReg()
#         elif static_os.tp_strategy_type == TakeProfitStrategyType.Provided:
#             pass
#     """
#     #########################################
#     #########################################
#     #########################################
#                 Other Settings
#                 Other Settings
#                 Other Settings
#     #########################################
#     #########################################
#     #########################################
#     """

#     if static_os.tp_fee_type == TakeProfitFeeType.Market:
#         exit_fee_pct = exchange_settings.market_fee_pct
#     else:
#         exit_fee_pct = exchange_settings.limit_fee_pct
#     """
#     #########################################
#     #########################################
#     #########################################
#                 End User Setup
#                 End User Setup
#                 End User Setup
#     #########################################
#     #########################################
#     #########################################
#     """
#     # Creating Settings Vars
#     total_order_settings = dos_cart_arrays[0].size

#     total_indicator_settings = strategy.get_total_ind_settings()

#     total_bars = candles.shape[0]

#     # logger.infoing out total numbers of things
#     print("Starting the backtest now ... and also here are some stats for your backtest.\n")
#     print("Total indicator settings to test: " + str(total_indicator_settings))
#     print("Total order settings to test: " + str(total_order_settings))
#     print("Total combinations of settings to test: " + str(int(total_indicator_settings * total_order_settings)))
#     print("Total candles: " + str(total_bars))
#     print("Total candles to test: " + str(int(total_indicator_settings * total_order_settings * total_bars)))


# # def order_records_bt(
# #     starting_equity: float,
# #     os_cart_arrays: OrderSettingsArrays,
# #     exchange_settings: ExchangeSettings,
# #     strategy: Strategy,
# #     candles: np.array,
# #     backtest_results: pd.DataFrame,
# #     backtest_index: int,
# # ):
# #     ind_or_indexes = backtest_results.iloc[backtest_index][["ind_set_idx", "or_set_idx"]].astype(int).values
# #     ind_set_index = ind_or_indexes[0]
# #     or_set_index = ind_or_indexes[1]
# #     total_bars = candles.shape[0]
# #     order_records = np.empty(total_bars, dtype=or_dt)
# #     total_order_records_filled = 0

# #     if strategy.candle_processing_mode == CandleProcessingType.Backtest:
# #         calc_starting_bar = starting_bar_backtest
# #     else:
# #         calc_starting_bar = starting_bar_real

# #     strategy.set_indicator_settings(ind_set_index=ind_set_index)

# #     order_settings = get_order_setting(
# #         order_settings_index=or_set_index,
# #         os_cart_arrays=os_cart_arrays,
# #     )

# #     order = Order.instantiate(
# #         equity=starting_equity,
# #         order_settings=order_settings,
# #         exchange_settings=exchange_settings,
# #         long_or_short=order_settings.long_or_short,
# #         order_records=order_records,
# #         total_order_records_filled=total_order_records_filled,
# #     )

# #     logger.log_info("Created Order class")

# #     starting_bar = calc_starting_bar(order_settings.num_candles)

# #     for bar_index in range(starting_bar, total_bars):
# #         logger.log_info(
# #             f"ind_idx={ind_set_index) os_idx={or_set_index) b_idx={bar_index} timestamp={pd.to_datetime(candles['timestamp'][bar_index], unit='ms')}"
# #         )
# #         if order.position_size_usd > 0:
# #             try:
# #                 order.check_stop_loss_hit(current_candle=candles[bar_index])
# #                 order.check_liq_hit(current_candle=candles[bar_index])
# #                 order.check_take_profit_hit(
# #                     current_candle=candles[bar_index],
# #                     exit_signal=strategy.current_exit_signals[bar_index],
# #                 )
# #                 order.check_move_stop_loss_to_be(bar_index=bar_index, candles=candles)
# #                 order.check_move_trailing_stop_loss(bar_index=bar_index, candles=candles)
# #             except RejectedOrder as e:
# #                 logger.log_info("RejectedOrder -> {e.msg}")
# #                 pass
# #             except DecreasePosition as e:
# #                 order.decrease_position(
# #                     order_status=e.order_status,
# #                     exit_price=e.exit_price,
# #                     exit_fee_pct=e.exit_fee_pct,
# #                     bar_index=bar_index,
# #                     timestamp=candles["timestamp"][bar_index],
# #                     ind_set_index=ind_set_index,
# #                     order_settings_index=or_set_index,
# #                 )
# #             except MoveStopLoss as e:
# #                 order.move_stop_loss(
# #                     sl_price=e.sl_price,
# #                     order_status=e.order_status,
# #                     bar_index=bar_index,
# #                     timestamp=candles["timestamp"][bar_index],
# #                     ind_set_index=ind_set_index,
# #                     order_settings_index=or_set_index,
# #                 )
# #             except Exception as e:
# #                 logger.log_info("Exception placing order -> {e}")
# #                 raise Exception(f"Exception placing order -> {e}")
# #         strategy.create_indicator(bar_index=bar_index, starting_bar=starting_bar)
# #         if strategy.evaluate():  # add in that we are also not at max entry amount
# #             try:
# #                 order.calculate_stop_loss(bar_index=bar_index, candles=candles)
# #                 order.calculate_increase_posotion(entry_price=candles["close"][bar_index])
# #                 order.calculate_leverage()
# #                 order.calculate_take_profit()
# #                 order.or_filler(
# #                     order_result=OrderResult(
# #                         ind_set_index=ind_set_index,
# #                         order_settings_index=or_set_index,
# #                         bar_index=bar_index + 1,
# #                         timestamp=candles["timestamp"][bar_index + 1],
# #                         available_balance=order.available_balance,
# #                         cash_borrowed=order.cash_borrowed,
# #                         cash_used=order.cash_used,
# #                         average_entry=order.average_entry,
# #                         leverage=order.leverage,
# #                         liq_price=order.liq_price,
# #                         order_status=order.order_status,
# #                         possible_loss=order.possible_loss,
# #                         entry_size_usd=order.entry_size_usd,
# #                         entry_price=order.entry_price,
# #                         position_size_usd=order.position_size_usd,
# #                         sl_pct=order.sl_pct,
# #                         sl_price=order.sl_price,
# #                         tp_pct=order.tp_pct,
# #                         tp_price=order.tp_price,
# #                     )
# #                 )
# #             except RejectedOrder as e:
# #                 logger.log_info("RejectedOrder -> {e.msg}")
# #                 pass
# #             except Exception as e:
# #                 logger.log_info("Exception placing order -> {e}")
# #                 raise Exception(f"Exception placing order -> {e}")

# #     order_records = order.order_records
# #     total_order_records_filled = order.total_order_records_filled

# #     return pd.DataFrame(order_records[:total_order_records_filled])
