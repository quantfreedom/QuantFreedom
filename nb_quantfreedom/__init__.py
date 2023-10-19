# if static_os.long_or_short == LongOrShortType.Long:
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
#         if static_os.stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
#             sl_calc = nb_Long_SLCandleBody()
#             sl_hit_checker = nb_Long_StopLoss()
#             if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
#                 sl_price_getter = nb_GetMinPrice()
#             elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
#                 sl_price_getter = nb_GetMaxPrice()
#         elif static_os.stop_loss_type == StopLossStrategyType.Nothing:
#             sl_calc = nb_StopLoss()
#             sl_price_getter = nb_StopLoss()

#         # setting up stop loss break even checker
#         if static_os.sl_to_break_even:
#             move_sl_to_be_checker = nb_Long_StopLoss()
#             if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
#                 sl_to_be_price_getter = nb_GetMinPrice()
#             elif static_os.pg_min_max_sl_bcb == PriceGetterType.Max:
#                 sl_to_be_price_getter = nb_GetMaxPrice()
#         else:
#             move_sl_to_be_checker = nb_StopLoss()
#             sl_to_be_price_getter = nb_StopLoss()

#         # setting up stop loss break even checker
#         if static_os.trail_sl:
#             move_tsl_checker = nb_Long_StopLoss()
#             if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
#                 tsl_price_getter = nb_GetMinPrice()
#             if static_os.pg_min_max_sl_bcb == PriceGetterType.Min:
#                 tsl_price_getter = nb_GetMinPrice()
#         else:
#             move_tsl_checker = nb_StopLoss()
#             tsl_price_getter = nb_StopLoss()

#         # setting up stop loss be zero or entry
#         if static_os.sl_to_be_ze_type == SLToBeZeroOrEntryType.Nothing:
#             set_sl_to_be_z_or_e = nb_StopLoss()
#         elif static_os.sl_to_be_ze_type == SLToBeZeroOrEntryType.ZeroLoss:
#             set_sl_to_be_z_or_e = nb_Long_SLToZero()
#         elif static_os.sl_to_be_ze_type == SLToBeZeroOrEntryType.AverageEntry:
#             set_sl_to_be_z_or_e = nb_Long_SLToEntry()

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

#         if static_os.stop_loss_type == StopLossStrategyType.SLBasedOnCandleBody:
#             if static_os.increase_position_type == IncreasePositionType.RiskPctAccountEntrySize:
#                 calc_increase_pos = nb_Long_RPAandSLB()

#             elif static_os.increase_position_type == IncreasePositionType.SmalletEntrySizeAsset:
#                 calc_increase_pos = nb_Long_SEP()

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

#         if static_os.leverage_type == LeverageStrategyType.Dynamic:
#             calc_leverage = nb_CalcDynamicLeverage()
#         else:
#             calc_leverage = nb_SetStaticLeverage()

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

#         if static_os.take_profit_type == TakeProfitStrategyType.RiskReward:
#             take_profit_calculator = nb_TPRiskReward()
#             tp_checker = nb_TPHitReg()
#         elif static_os.take_profit_type == TakeProfitStrategyType.Provided:
#             take_profit_calculator = nb_TakeProfit()
#             tp_checker = nb_TPHitProvided()
#         """
#         #########################################
#         #########################################
#         #########################################
#                     Other Settings
#                     Other Settings
#                     Other Settings
#         #########################################
#         #########################################
#         #########################################
#         """
#         if strategy.candle_processing_mode == CandleProcessingType.Backtest:
#             calc_starting_bar = nb_StartBarBacktest()
#         else:
#             calc_starting_bar = nb_StartBarReal()

#         if static_os.tp_fee_type == TakeProfitFeeType.Market:
#             exit_fee_pct = exchange_settings.market_fee_pct
#         else:
#             exit_fee_pct = exchange_settings.limit_fee_pct
