from logging import getLogger
from quantfreedom.order_handler.grid_order_handler.grid_order_class.grid_order import GridOrderHandler
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    OrderStatus,
    FootprintCandlesTuple,
)

logger = getLogger()


class GridStopLoss(GridOrderHandler):

    def grid_check_sl_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_hit_exec: str,
        sl_price: float,
    ):
        sl_hit_bool: bool

        exec(sl_hit_exec)

        if sl_hit_bool:
            logger.debug(f"Stop loss hit sl_price= {sl_price}")
            raise DecreasePosition(
                exit_fee_pct=self.market_fee_pct,
                exit_price=sl_price,
                order_status=OrderStatus.StopLossFilled,
            )
        else:
            logger.debug("No hit on stop loss")
            pass
