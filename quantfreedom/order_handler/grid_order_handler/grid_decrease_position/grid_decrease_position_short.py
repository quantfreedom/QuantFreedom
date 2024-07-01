from logging import getLogger

from quantfreedom.order_handler.grid_order_handler.grid_decrease_position.grid_decrease_position import (
    GridDecreasePosition,
)
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    OrderStatus,
)


logger = getLogger()


class GridDecreasePositionShort(GridDecreasePosition):

    def calculate_decrease_position(
        self,
        cur_datetime: str,
        exit_price: float,
        equity: float,
        order_status: OrderStatus,  # type: ignore
    ):
        pnl = round((self.average_entry - exit_price) * self.position_size_asset, 2)  # math checked

        (
            equity,
            fees_paid,
            realized_pnl,
        ) = self.finish_decrease_position(
            cur_datetime=cur_datetime,
            exit_price=exit_price,
            equity=equity,
            order_status=order_status,
            pnl=pnl,
        )

        return (
            equity,
            fees_paid,
            realized_pnl,
        )
