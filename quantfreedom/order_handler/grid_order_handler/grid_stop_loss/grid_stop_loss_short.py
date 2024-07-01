from logging import getLogger

from quantfreedom.order_handler.grid_order_handler.grid_stop_loss.grid_stop_loss import GridStopLoss

from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    OrderStatus,
)


logger = getLogger()


class GridStopLossShort(GridStopLoss):
    def check_sl_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        logger.debug("Starting")
        candle_high = current_candle.high_price
        logger.debug(f"candle_high= {candle_high}")
        sl_hit_bool = sl_price < candle_high

        if sl_hit_bool:
            logger.debug(f"Long Stop loss hit sl_price= {sl_price}")
            raise DecreasePosition(
                exit_fee_pct=self.market_fee_pct,
                exit_price=sl_price,
                order_status=OrderStatus.StopLossFilled,
            )
        else:
            logger.debug("Long No hit on stop loss")
            pass