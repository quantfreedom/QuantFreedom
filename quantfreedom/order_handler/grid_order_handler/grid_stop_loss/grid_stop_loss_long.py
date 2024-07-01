from logging import getLogger

from quantfreedom.order_handler.grid_order_handler.grid_stop_loss.grid_stop_loss import GridStopLoss

from quantfreedom.core.enums import CurrentFootprintCandleTuple


logger = getLogger()


class GridStopLossLong(GridStopLoss):

    def check_sl_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        logger.debug("Starting")
        candle_low = current_candle.low_price
        logger.debug(f"candle_low= {candle_low}")
        sl_hit_bool = sl_price > candle_low

        self.finish_sl_hit(
            sl_hit_bool=sl_hit_bool,
            sl_price=sl_price,
        )
