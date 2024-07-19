from logging import getLogger
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    OrderStatus,
)

logger = getLogger()


class GridStopLoss:

    def grid_check_sl_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        market_fee_pct: float,
        sl_hit_exec: str,
        sl_price: float,
    ):
        sl_hit_bool: bool

        exec(sl_hit_exec)

        if sl_hit_bool:
            logger.debug(f"Stop loss hit sl_price= {sl_price}")
            raise DecreasePosition(
                exit_fee_pct=market_fee_pct,
                exit_price=sl_price,
                order_status=OrderStatus.StopLossFilled,
            )
        else:
            logger.debug("No hit on stop loss")
            pass
