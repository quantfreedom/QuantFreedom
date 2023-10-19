from numba.experimental import jitclass
from nb_quantfreedom.nb_custom_logger import nb_CustomLogger

from nb_quantfreedom.nb_enums import OrderResult, OrderStatus


class nb_DecreasePosition:
    def __init__(self) -> None:
        pass

    def decrease_position(
        self,
        logger: nb_CustomLogger,
        average_entry: float,
        bar_index: int,
        dos_index: int,
        equity: float,
        exit_fee_pct: float,
        exit_price: float,
        indicator_settings_index: int,
        market_fee_pct: float,
        order_status: int,
        position_size_asset: float,
        timestamp: int,
    ):
        pass


@jitclass()
class nb_Long_DP(nb_DecreasePosition):
    def decrease_position(
        self,
        logger: nb_CustomLogger,
        average_entry: float,
        equity: float,
        exit_fee_pct: float,
        exit_price: float,
        market_fee_pct: float,
        order_status: int,
        position_size_asset: float,
    ):
        pnl = position_size_asset * (exit_price - average_entry)  # math checked
        fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
        fee_close = position_size_asset * exit_price * exit_fee_pct  # math checked
        fees_paid = fee_open + fee_close  # math checked
        realized_pnl = round(pnl - fees_paid, 4)  # math checked

        # Setting new equity
        equity = round(realized_pnl + equity, 4)
        logger.debug(
            f"\n\
realized_pnl={realized_pnl}\n\
order_status= {OrderStatus._fields[order_status]}\n\
available_balance={equity}\n\
equity={equity}"
        )
        return equity, fees_paid, realized_pnl
