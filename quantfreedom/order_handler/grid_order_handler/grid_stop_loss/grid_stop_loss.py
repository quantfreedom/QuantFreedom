from logging import getLogger
from quantfreedom.order_handler.grid_order_handler.grid_order import GridOrderHandler
from quantfreedom.core.enums import (
    CurrentFootprintCandleTuple,
    DecreasePosition,
    OrderStatus,
    FootprintCandlesTuple,
)

logger = getLogger()


class GridStopLoss(GridOrderHandler):

    def __init__(
        self,
        market_fee_pct: float,
        price_tick_step: float,
    ) -> None:
        self.market_fee_pct = market_fee_pct
        self.price_tick_step = price_tick_step

    def finish_sl_hit(
        self,
        sl_hit_bool: bool,
        sl_price: float,
    ):
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

    def min_price_getter(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
        lookback: int,
        candle_body_type: int,
    ) -> float:
        the_prices = candles[candle_body_type]
        lb_the_prices = the_prices[lookback : bar_index + 1]
        final_the_prices = lb_the_prices.min()
        return final_the_prices

    def max_price_getter(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
        lookback: int,
        candle_body_type: int,
    ) -> float:
        the_prices = candles[candle_body_type]
        lb_the_prices = the_prices[lookback : bar_index + 1]
        final_the_prices = lb_the_prices.max()
        return final_the_prices
