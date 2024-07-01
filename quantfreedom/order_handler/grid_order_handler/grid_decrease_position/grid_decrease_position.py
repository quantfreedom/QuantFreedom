from logging import getLogger
from quantfreedom.order_handler.grid_order_handler.grid_order import GridOrderHandler
from quantfreedom.core.enums import OrderStatus

logger = getLogger()


class GridDecreasePosition(GridOrderHandler):

    def __init__(
        self,
        market_fee_pct: float,
        price_tick_step: float,
    ) -> None:
        self.market_fee_pct = market_fee_pct
        self.price_tick_step = price_tick_step

    def finish_decrease_position(
        self,
        cur_datetime: str,
        exit_price: float,
        equity: float,
        order_status: OrderStatus,  # type: ignore
        pnl: float,
    ):
        logger.debug(f"pnl= {pnl}")

        fee_open = round(self.position_size_asset * self.average_entry * self.limit_fee_pct, 2)  # math checked
        logger.debug(f"fee_open= {fee_open}")

        fee_close = round(self.position_size_asset * exit_price * self.limit_fee_pct, 2)  # math checked
        logger.debug(f"fee_close= {fee_close}")

        fees_paid = round(fee_open + fee_close, 2)  # math checked
        logger.debug(f"fees_paid= {fees_paid}")

        realized_pnl = round(pnl - fees_paid, 2)  # math checked
        logger.debug(f"realized_pnl= {realized_pnl}")

        equity = round(realized_pnl + equity, 2)
        logger.debug(f"equity= {equity}")

        logger.info(
            f"""
datetime= {cur_datetime}
equity= {equity}
fees_paid= {fees_paid}
order_status= {OrderStatus._fields[order_status]}
realized_pnl= {realized_pnl}
"""
        )
        return (
            equity,
            fees_paid,
            realized_pnl,
        )
