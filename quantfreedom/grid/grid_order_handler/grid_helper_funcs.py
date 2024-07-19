import numpy as np

from quantfreedom.core.enums import CurrentFootprintCandleTuple, FootprintCandlesTuple, OrderStatus

from logging import getLogger

logger = getLogger()


class GridHelperFuncs:
    pass

    def get_current_candle(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
    ):
        current_candle = CurrentFootprintCandleTuple(
            open_timestamp=candles.candle_open_timestamps[bar_index],
            open_price=candles.candle_open_prices[bar_index],
            high_price=candles.candle_high_prices[bar_index],
            low_price=candles.candle_low_prices[bar_index],
            close_price=candles.candle_close_prices[bar_index],
        )
        return current_candle
