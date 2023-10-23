import numpy as np
from numba.experimental import jitclass

from nb_quantfreedom.nb_custom_logger import CustomLoggerClass
from nb_quantfreedom.nb_helper_funcs import nb_round_size_by_tick_step


class PriceGetterClass:
    def __init__(self) -> None:
        pass

    def nb_min_max_price_getter(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        candle_body_type: int,
        candles: np.array,
        lookback: int,
    ) -> float:
        pass

    def nb_price_getter(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        candle_body_type: int,
        current_candle: np.array,
    ) -> float:
        pass


@jitclass()
class PriceGetterNB(PriceGetterClass):
    def nb_min_max_price_getter(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        candle_body_type: int,
        candles: np.array,
        lookback: int,
    ) -> float:
        pass

    def nb_price_getter(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        candle_body_type: int,
        current_candle: np.array,
    ) -> float:
        pass


@jitclass()
class nb_GetMinPrice(PriceGetterClass):
    def nb_min_max_price_getter(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        candles: np.array,
        candle_body_type: int,
        lookback: int,
    ) -> float:
        price = candles[lookback : bar_index + 1 :, candle_body_type].min()
        logger.log_debug(
            "nb_class_helpers.py - nb_GetMinPrice - nb_min_max_price_getter() -"
            + " candle_body_type= "
            + logger.candle_body_str(candle_body_type)
            + " price= "
            + logger.float_to_str(price)
        )
        return price


@jitclass()
class nb_GetMaxPrice(PriceGetterClass):
    def nb_min_max_price_getter(
        self,
        logger: CustomLoggerClass,
        bar_index: int,
        candles: np.array,
        candle_body_type: int,
        lookback: int,
    ):
        price = candles[lookback : bar_index + 1 :, candle_body_type].max()
        logger.log_debug(
            "nb_class_helpers.py - nb_GetMinPrice - nb_min_max_price_getter() -"
            + " candle_body_type= "
            + logger.candle_body_str(candle_body_type)
            + " price= "
            + logger.float_to_str(price)
        )
        return price


@jitclass()
class nb_GetPrice(PriceGetterClass):
    def nb_price_getter(
        self,
        logger: CustomLoggerClass,
        candle_body_type: int,
        current_candle: np.array,
    ):
        price = current_candle[candle_body_type]
        logger.log_debug(
            "nb_class_helpers.py - nb_GetMinPrice - nb_min_max_price_getter() -"
            + " candle_body_type= "
            + logger.candle_body_str(candle_body_type)
            + " price= "
            + logger.float_to_str(price)
        )
        return price


class ZeroOrEntryClass:
    def __init__(self):
        pass

    def nb_set_sl_to_z_or_e(
        self,
        logger: CustomLoggerClass,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        pass


@jitclass
class ZeroOrEntryNB(ZeroOrEntryClass):
    def nb_set_sl_to_z_or_e(
        self,
        logger: CustomLoggerClass,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        pass


@jitclass()
class nb_Long_SLToZero(ZeroOrEntryClass):
    def nb_set_sl_to_z_or_e(
        self,
        logger: CustomLoggerClass,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        sl_price = (market_fee_pct * average_entry + average_entry) / (1 - market_fee_pct)
        sl_price = nb_round_size_by_tick_step(
            user_num=sl_price,
            exchange_num=price_tick_step,
        )
        logger.log_debug(
            "nb_class_helpers.py - nb_Long_SLToZero - nb_set_sl_to_z_or_e() - New sl_price= "
            + logger.float_to_str(sl_price)
        )
        return sl_price


@jitclass()
class nb_Long_SLToEntry(ZeroOrEntryClass):
    def nb_set_sl_to_z_or_e(
        self,
        logger: CustomLoggerClass,
        average_entry,
        market_fee_pct,
        price_tick_step,
    ):
        sl_price = average_entry
        logger.log_debug(
            "nb_class_helpers.py - nb_Long_SLToEntry - nb_set_sl_to_z_or_e() - New sl_price= "
            + logger.float_to_str(sl_price)
        )
        return sl_price
