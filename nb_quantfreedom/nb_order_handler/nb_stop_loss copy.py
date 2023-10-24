# import numpy as np
# from numba import types
# from numba.experimental import jitclass
# from nb_quantfreedom.nb_custom_logger import CustomLoggerClass

# from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
# from nb_quantfreedom.nb_enums import (
#     AccountState,
#     CandleBodyType,
#     DecreasePosition,
#     MoveStopLoss,
#     OrderResult,
#     OrderStatus,
# )
# from nb_quantfreedom.nb_order_handler.nb_class_helpers import PGPass, ZeroOrEntryNB, nb_GetPrice


# class StopLossClass:
#     def __init__(self) -> None:
#         pass

#     def move_stop_loss(
#         self,
#         account_state: AccountState,
#         bar_index: int,
#         can_move_sl_to_be: bool,
#         dos_index: int,
#         ind_set_index: int,
#         logger: CustomLoggerClass,
#         order_result: OrderResult,
#         order_status: int,
#         sl_price: float,
#         timestamp: np.int64,
#     ):
#         pass

#     def calculate_stop_loss(
#         self,
#         bar_index: int,
#         candles: np.array,
#         logger: CustomLoggerClass,
#         price_tick_step: float,
#         sl_based_on_add_pct: float,
#         sl_based_on_lookback: int,
#         sl_bcb_price_getter: PGPass,
#         sl_bcb_type: int,
#     ):
#         pass

#     def check_stop_loss_hit(
#         self,
#         logger: CustomLoggerClass,
#         bar_index: int,
#         current_candle: np.array,
#         sl_price: float,
#     ):
#         pass

#     def check_move_stop_loss_to_be(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         can_move_sl_to_be: bool,
#         candle_body_type: int,
#         current_candle: np.array,
#         set_z_e: ZeroOrEntryNB,
#         sl_price: float,
#         sl_to_be_move_when_pct: float,
#     ):
#         pass

#     def check_move_trailing_stop_loss(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         candle_body_type: int,
#         can_move_sl_to_be: bool,
#         current_candle: np.array,
#         sl_price: float,
#         trail_sl_by_pct: float,
#         trail_sl_when_pct: float,
#     ):
#         pass


# @jitclass
# class SLPass(StopLossClass):
#     def move_stop_loss(
#         self,
#         account_state: AccountState,
#         bar_index: int,
#         can_move_sl_to_be: bool,
#         dos_index: int,
#         ind_set_index: int,
#         logger: CustomLoggerClass,
#         order_result: OrderResult,
#         order_status: int,
#         sl_price: float,
#         timestamp: np.int64,
#     ):
#         pass

#     def calculate_stop_loss(
#         self,
#         bar_index: int,
#         candles: np.array,
#         logger: CustomLoggerClass,
#         price_tick_step: float,
#         sl_based_on_add_pct: float,
#         sl_based_on_lookback: int,
#         sl_bcb_price_getter: PGPass,
#         sl_bcb_type: int,
#     ):
#         pass

#     def check_stop_loss_hit(
#         self,
#         logger: CustomLoggerClass,
#         bar_index: int,
#         current_candle: np.array,
#         sl_price: float,
#     ):
#         pass

#     def check_move_stop_loss_to_be(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         can_move_sl_to_be: bool,
#         candle_body_type: int,
#         current_candle: np.array,
#         set_z_e: ZeroOrEntryNB,
#         sl_price: float,
#         sl_to_be_move_when_pct: float,
#     ):
#         pass

#     def check_move_trailing_stop_loss(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         candle_body_type: int,
#         can_move_sl_to_be: bool,
#         current_candle: np.array,
#         sl_price: float,
#         trail_sl_by_pct: float,
#         trail_sl_when_pct: float,
#     ):
#         pass


# @jitclass
# class Long_StopLoss(StopLossClass):
#     def check_stop_loss_hit(
#         self,
#         logger: CustomLoggerClass,
#         current_candle: np.array,
#         sl_price: float,
#     ):
#         logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - Starting")
#         candle_low = nb_GetPrice().nb_price_getter(
#             logger=logger,
#             candle_body_type=CandleBodyType.Low,
#             current_candle=current_candle,
#         )
#         if sl_price > candle_low:
#             logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - Stop loss hit")
#             return True
#         else:
#             logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - No hit on stop loss")
#             return False

#     def check_move_stop_loss_to_be(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         can_move_sl_to_be: bool,
#         candle_body_type: int,
#         current_candle: np.array,
#         set_z_e: ZeroOrEntryNB,
#         sl_price: float,
#         sl_to_be_move_when_pct: float,
#     ):
#         if can_move_sl_to_be:
#             logger.log_debug(
#                 "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - Might move sl to break even"
#             )
#             # Stop Loss to break even
#             candle_low = nb_GetPrice().nb_price_getter(
#                 logger=logger,
#                 candle_body_type=candle_body_type,
#                 current_candle=current_candle,
#             )
#             pct_from_ae = (candle_low - average_entry) / average_entry
#             logger.log_debug(
#                 "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - pct_from_ae= "
#                 + logger.float_to_str(round(pct_from_ae * 100, 3))
#             )
#             move_sl = pct_from_ae > sl_to_be_move_when_pct
#             if move_sl:
#                 old_sl = sl_price
#                 sl_price = set_z_e.nb_set_sl_to_z_or_e(
#                     average_entry=average_entry,
#                 )
#                 logger.log_debug(
#                     "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - moving sl old_sl= "
#                     + logger.float_to_str(old_sl)
#                     + " new sl= "
#                     + logger.float_to_str(sl_price)
#                 )
#                 return sl_price
#             else:
#                 logger.log_debug(
#                     "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - not moving sl to be"
#                 )
#                 return -1
#         else:
#             logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - can't move sl to be")
#             return -1

#     def check_move_trailing_stop_loss(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         can_move_sl_to_be: bool,
#         candle_body_type: CandleBodyType,
#         current_candle: np.array,
#         sl_price: float,
#         trail_sl_by_pct: float,
#         trail_sl_when_pct: float,
#     ):
#         candle_low = nb_GetPrice().nb_price_getter(
#             logger=logger,
#             candle_body_type=candle_body_type,
#             current_candle=current_candle,
#         )
#         pct_from_ae = (candle_low - average_entry) / average_entry
#         logger.log_debug(
#             "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - pct_from_ae= "
#             + logger.float_to_str(round(pct_from_ae * 100, 3))
#         )
#         possible_move_tsl = pct_from_ae > trail_sl_when_pct
#         if possible_move_tsl:
#             logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Maybe move tsl")
#             temp_sl_price = candle_low - candle_low * trail_sl_by_pct
#             temp_sl_price = nb_round_size_by_tick_step(
#                 user_num=temp_sl_price,
#                 exchange_num=price_tick_step,
#             )
#             logger.log_debug(
#                 "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - temp sl= "
#                 + logger.float_to_str(temp_sl_price)
#             )
#             if temp_sl_price > sl_price:
#                 logger.log_debug(
#                     "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Moving tsl new sl= "
#                     + logger.float_to_str(temp_sl_price)
#                     + " > old sl= "
#                     + logger.float_to_str(sl_price)
#                 )
#                 return temp_sl_price
#             else:
#                 logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Wont move tsl")
#                 return -1
#         else:
#             logger.log_debug("nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Not moving tsl")
#             return -1


# @jitclass
# class Long_SLBCB(StopLossClass):
#     """
#     Stop loss based on candle body
#     """

#     def calculate_stop_loss(
#         self,
#         bar_index: int,
#         candles: np.array,
#         logger: CustomLoggerClass,
#         price_tick_step: float,
#         sl_based_on_add_pct: float,
#         sl_based_on_lookback: int,
#         sl_bcb_price_getter: PGPass,
#         sl_bcb_type: int,
#     ) -> float:
#         # lb will be bar index if sl isn't based on lookback because look back will be 0
#         lookback = max(bar_index - sl_based_on_lookback, 0)
#         logger.log_debug(
#             "nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - lookback= " + logger.float_to_str(lookback)
#         )
#         candle_body = sl_bcb_price_getter.nb_min_max_price_getter(
#             logger=logger,
#             candle_body_type=sl_bcb_type,
#             lookback=lookback,
#             bar_index=bar_index,
#             candles=candles,
#         )
#         logger.log_debug(
#             "nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - candle_body= " + logger.float_to_str(candle_body)
#         )
#         sl_price = candle_body - (candle_body * sl_based_on_add_pct)
#         sl_price = nb_round_size_by_tick_step(
#             user_num=sl_price,
#             exchange_num=price_tick_step,
#         )
#         logger.log_debug(
#             "nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - sl_price= " + logger.float_to_str(sl_price)
#         )
#         return sl_price


# @jitclass()
# class MoveSL(StopLossClass):
#     def move_stop_loss(
#         self,
#         account_state: AccountState,
#         bar_index: int,
#         can_move_sl_to_be: bool,
#         dos_index: int,
#         ind_set_index: int,
#         logger: CustomLoggerClass,
#         order_result: OrderResult,
#         order_status: int,
#         sl_price: float,
#         timestamp: int,
#     ) -> OrderResult:
#         account_state = AccountState(
#             # where we are at
#             ind_set_index=ind_set_index,
#             dos_index=dos_index,
#             bar_index=bar_index,
#             timestamp=timestamp,
#             # account info
#             available_balance=account_state.available_balance,
#             cash_borrowed=account_state.cash_borrowed,
#             cash_used=account_state.cash_used,
#             equity=account_state.equity,
#             fees_paid=account_state.fees_paid,
#             possible_loss=account_state.possible_loss,
#             realized_pnl=account_state.realized_pnl,
#             total_trades=account_state.total_trades,
#         )
#         logger.log_debug("nb_stop_loss.py - nb_MoveSL - move_stop_loss() - created account state")
#         a_e = order_result.average_entry
#         sl = sl_price
#         a_s = a_e - sl
#         sl_p = a_s / order_result.average_entry
#         sl_p_r = round(sl_p, 3)
#         sl_pct = abs(sl_p_r)
#         logger.log_debug("nb_stop_loss.py - nb_MoveSL - move_stop_loss() - sl percent= " + logger.float_to_str(sl_pct))
#         order_result = OrderResult(
#             average_entry=order_result.average_entry,
#             can_move_sl_to_be=can_move_sl_to_be,
#             entry_price=order_result.entry_price,
#             entry_size_asset=order_result.entry_size_asset,
#             entry_size_usd=order_result.entry_size_usd,
#             exit_price=order_result.exit_price,
#             leverage=order_result.leverage,
#             liq_price=order_result.liq_price,
#             order_status=order_status,
#             position_size_asset=order_result.position_size_asset,
#             position_size_usd=order_result.position_size_usd,
#             sl_pct=sl_pct,
#             sl_price=sl_price,
#             tp_pct=order_result.tp_pct,
#             tp_price=order_result.tp_price,
#         )
#         logger.log_debug("nb_stop_loss.py - nb_MoveSL - move_stop_loss() - created order result")

#         return account_state, order_result
