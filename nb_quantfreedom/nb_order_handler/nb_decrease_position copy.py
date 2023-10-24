# from numba.experimental import jitclass
# from nb_quantfreedom.nb_custom_logger import CustomLoggerClass
# from nb_quantfreedom.nb_enums import AccountState, OrderResult, OrderStatus


# class DecreasePositionClass:
#     def __init__(self) -> None:
#         pass

#     def decrease_position(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         bar_index: int,
#         dos_index: int,
#         equity: float,
#         exit_fee_pct: float,
#         exit_price: float,
#         ind_set_index: int,
#         market_fee_pct: float,
#         order_status: int,
#         position_size_asset: float,
#         timestamp: int,
#     ):
#         pass


# @jitclass()
# class DecreasePositionNB(DecreasePositionClass):
#     def decrease_position(
#         self,
#         logger: CustomLoggerClass,
#         average_entry: float,
#         bar_index: int,
#         dos_index: int,
#         equity: float,
#         exit_fee_pct: float,
#         exit_price: float,
#         ind_set_index: int,
#         market_fee_pct: float,
#         order_status: int,
#         position_size_asset: float,
#         timestamp: int,
#     ):
#         pass


# @jitclass()
# class nb_Long_DP(DecreasePositionClass):
#     def decrease_position(
#         self,
#         average_entry: float,
#         equity: float,
#         exit_fee_pct: float,
#         exit_price: float,
#         logger: CustomLoggerClass,
#         market_fee_pct: float,
#         position_size_asset: float,
#     ):
#         pnl = position_size_asset * (exit_price - average_entry)  # math checked
#         fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
#         fee_close = position_size_asset * exit_price * exit_fee_pct  # math checked
#         fees_paid = fee_open + fee_close  # math checked
#         realized_pnl = round(pnl - fees_paid, 3)  # math checked

#         # Setting new equity
#         equity = round(realized_pnl + equity, 3)
#         logger.log_debug(
#             "nb_decrease_position.py - nb_Long_DP - decrease_position() -"
#             + "\nrealized_pnl= "
#             + logger.float_to_str(realized_pnl)
#             + "\nequity= "
#             + logger.float_to_str(equity)
#             + "\nfees_paid= "
#             + logger.float_to_str(fees_paid)
#         )

#         # reset the order result
#         account_state = AccountState(
#             # where we are at
#             ind_set_index=-1,
#             dos_index=-1,
#             bar_index=-1,
#             timestamp=-1,
#             # account info
#             available_balance=equity,
#             cash_borrowed=0.0,
#             cash_used=0.0,
#             equity=equity,
#             fees_paid=0.0,
#             possible_loss=0.0,
#             realized_pnl=0.0,
#             total_trades=0,
#         )
#         order_result = OrderResult(
#             average_entry=0.0,
#             can_move_sl_to_be=False,
#             entry_price=0.0,
#             entry_size_asset=0.0,
#             entry_size_usd=0.0,
#             exit_price=0.0,
#             leverage=1.0,
#             liq_price=0.0,
#             order_status=OrderStatus.Nothing,
#             position_size_asset=0.0,
#             position_size_usd=0.0,
#             sl_pct=0.0,
#             sl_price=0.0,
#             tp_pct=0.0,
#             tp_price=0.0,
#         )

#         return (
#             account_state,
#             fees_paid,
#             order_result,
#             realized_pnl,
#         )
