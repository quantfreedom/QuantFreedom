from quantfreedom.core.enums import CurrentFootprintCandleTuple
from typing import NamedTuple
from logging import getLogger

logger = getLogger()


class GridSLFuncs(NamedTuple):
    def long_check_sl_hit_bool(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        candle_low = current_candle.low_price
        logger.debug(f"candle_low= {candle_low}")

        sl_hit_bool = sl_price > candle_low
        logger.debug(f"sl_hit_bool= {sl_hit_bool}")

        return sl_hit_bool

    def short_check_sl_hit_bool(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_price: float,
    ):
        candle_high = current_candle.high_price
        logger.debug(f"candle_high= {candle_high}")

        sl_hit_bool = sl_price < candle_high
        logger.debug(f"sl_hit_bool= {sl_hit_bool}")

        return sl_hit_bool


Grid_SL_Funcs = GridSLFuncs()
