from logging import getLogger
from quantfreedom.order_handler.grid_order_handler.grid_order import GridOrderHandler
from quantfreedom.core.enums import OrderStatus

logger = getLogger()


class GridIncreasePosition(GridOrderHandler):
    def grid_increase_position(
        self,
        cur_datetime: str,
        order_size: float,
        entry_price: float,
        order_status: OrderStatus,  # type: ignore
        pnl_exec: str,
    ):
        try:
            average_entry = (self.position_size_usd + order_size) / ((self.position_size_usd / average_entry) + (order_size / entry_price))
        except ZeroDivisionError:
            average_entry = entry_price
        return average_entry