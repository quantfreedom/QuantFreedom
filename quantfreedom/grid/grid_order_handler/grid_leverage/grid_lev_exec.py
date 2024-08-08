from typing import NamedTuple
from quantfreedom.core.enums import CandleBodyType, CurrentFootprintCandleTuple

from logging import getLogger

logger = getLogger()


class GridLevFuncs(NamedTuple):

    def long_get_bankruptcy_price(
        self,
        average_entry: float,
        leverage: float,
    ):
        bankruptcy_price = average_entry * (leverage - 1) / leverage
        logger.debug(f"bankruptcy_price= {bankruptcy_price}")

        return bankruptcy_price

    def long_get_liq_price(
        self,
        average_entry: float,
        leverage: float,
        mmr_pct: float,
    ):
        liq_price = average_entry * (1 - (1 / leverage) + mmr_pct)
        logger.debug(f"liq_price= {liq_price}")

        return liq_price

    def long_check_liq_hit_bool(
        self,
        current_candle: CurrentFootprintCandleTuple,
        liq_price: float,
    ):
        candle_low = current_candle[CandleBodyType.Low]
        logger.debug(f"candle_low= {candle_low}")

        liq_hit_bool = liq_price > candle_low
        logger.debug(f"liq_hit_bool= {liq_hit_bool}")

        return liq_hit_bool

    def short_get_bankruptcy_price(
        self,
        average_entry: float,
        leverage: float,
    ):
        bankruptcy_price = average_entry * (leverage + 1) / leverage
        logger.debug(f"bankruptcy_price= {round(bankruptcy_price, 2)}")

        return bankruptcy_price

    def short_get_liq_price(
        self,
        average_entry: float,
        leverage: float,
        mmr_pct: float,
    ):
        liq_price = average_entry * (1 + (1 / leverage) - mmr_pct)
        logger.debug(f"liq_price= {round(liq_price, 2)}")

        return liq_price

    def short_check_liq_hit_bool(
        self,
        current_candle: CurrentFootprintCandleTuple,
        liq_price: float,
    ):
        candle_high = current_candle[CandleBodyType.High]
        logger.debug(f"candle_high= {candle_high}")

        liq_hit_bool = liq_price < candle_high
        logger.debug(f"liq_hit_bool= {liq_hit_bool}")

        return liq_hit_bool


Grid_Lev_Funcs = GridLevFuncs()
