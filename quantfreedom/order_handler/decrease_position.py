from quantfreedom.enums import AccountState, LoggerFuncType, OrderResult, OrderStatus, StringerFuncType
from logging import getLogger

logger = getLogger("info")


class LongDecreasePosition:
    def __init__(
        self,
        market_fee_pct: float,
    ) -> None:
        self.market_fee_pct = market_fee_pct
        self.dec_pos_calculator = self.long_decrease_position
        pass

    def long_decrease_position(
        self,
        average_entry: float,
        equity: float,
        exit_fee_pct: float,
        exit_price: float,
        position_size_asset: float,
    ):
        pnl = round(position_size_asset * (exit_price - average_entry), 3)  # math checked
        logger.debug(f"pnl= {pnl}")

        fee_open = round(position_size_asset * average_entry * self.market_fee_pct, 3)  # math checked
        logger.debug(f"fee_open= {fee_open}")

        fee_close = round(position_size_asset * exit_price * exit_fee_pct, 3)  # math checked
        logger.debug(f"fee_close= {fee_close}")

        fees_paid = round(fee_open + fee_close, 3)  # math checked
        logger.debug(f"fees_paid= {fees_paid}")

        realized_pnl = round(pnl - fees_paid, 3)  # math checked
        logger.debug(f"realized_pnl= {realized_pnl}")

        equity = round(realized_pnl + equity, 3)
        logger.debug(f"equity= {equity}")

        return equity, fees_paid, realized_pnl
