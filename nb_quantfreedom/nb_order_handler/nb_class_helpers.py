import numpy as np
from numba.experimental import jitclass
from nb_quantfreedom.nb_custom_logger import nb_CustomLogger
from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step
import logging


class nb_PriceGetter:
    def __init__(self) -> None:
        pass

    def nb_min_max_price_getter(
        self,
        logger: nb_CustomLogger,
        bar_index: int,
        candle_body_type: int,
        candles: np.array,
        lookback: int,
    ) -> float:
        pass

    def nb_price_getter(
        self,
        logger: nb_CustomLogger,
        bar_index: int,
        candle_body_type: int,
        current_candle: np.array,
    ) -> float:
        pass


@jitclass()
class nb_GetMinPrice(nb_PriceGetter):
    def nb_min_max_price_getter(
        self,
        logger: nb_CustomLogger,
        bar_index: int,
        candles: np.array,
        candle_body_type: int,
        lookback: int,
    ) -> float:
        price = candles[lookback : bar_index + 1 :, candle_body_type].min()
        logger.debug(f"{candle_body_type} price min = {price}")
        return price


@jitclass()
class nb_GetMaxPrice(nb_PriceGetter):
    def nb_min_max_price_getter(
        self,
        logger: nb_CustomLogger,
        bar_index: int,
        candles: np.array,
        candle_body_type: int,
        lookback: int,
    ):
        price = candles[lookback : bar_index + 1 :, candle_body_type].max()
        logger.debug(f"{candle_body_type} price min = {price}")
        return price


@jitclass()
class nb_GetPrice(nb_PriceGetter):
    def nb_price_getter(
        self,
        logger: nb_CustomLogger,
        candle_body_type: int,
        current_candle: np.array,
    ):
        price = current_candle[:, candle_body_type]
        logger.debug(f"{candle_body_type} price min = {price}")
        return price


class nb_ZeroOrEntry:
    def __init__(self) -> None:
        pass

    def nb_set_sl_to_z_or_e(
        self,
        logger: nb_CustomLogger,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        pass


@jitclass()
class nb_Long_SLToZero(nb_ZeroOrEntry):
    def nb_set_sl_to_z_or_e(
        self,
        logger: nb_CustomLogger,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        sl_price = (market_fee_pct * average_entry + average_entry) / (1 - market_fee_pct)
        sl_price = nb_round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=price_tick_step,
        )
        logger.debug(f"New sl_price={sl_price}")
        return sl_price


@jitclass()
class nb_Long_SLToEntry(nb_ZeroOrEntry):
    def nb_set_sl_to_z_or_e(
        self,
        logger: nb_CustomLogger,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        sl_price = average_entry
        logger.debug(f"New sl_price={sl_price}")
        return sl_price
