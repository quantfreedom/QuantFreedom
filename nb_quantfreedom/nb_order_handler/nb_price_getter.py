import numpy as np
from numba.experimental import jitclass


class nb_PriceGetter:
    def __init__(self) -> None:
        pass

    def nb_min_max_price_getter(
        self,
        bar_index: int,
        candle_body_type: int,
        candles: np.array,
        lookback: int,
    ) -> float:
        pass

    def nb_price_getter(
        self,
        bar_index: int,
        candle_body_type: int,
        current_candle: np.array,
    ) -> float:
        pass


@jitclass()
class nb_GetMinPrice(nb_PriceGetter):
    def nb_min_max_price_getter(
        self,
        bar_index: int,
        candles: np.array,
        candle_body_type: int,
        lookback: int,
    ) -> float:
        price = candles[lookback : bar_index + 1 :, candle_body_type].min()
        print(f"{candle_body_type} price min = {price}")
        return price


@jitclass()
class nb_GetMaxPrice(nb_PriceGetter):
    def nb_min_max_price_getter(
        self,
        bar_index: int,
        candles: np.array,
        candle_body_type: int,
        lookback: int,
    ):
        price = candles[lookback : bar_index + 1 :, candle_body_type].max()
        print(f"{candle_body_type} price min = {price}")
        return price


@jitclass()
class nb_GetPrice(nb_PriceGetter):
    def nb_price_getter(
        self,
        candle_body_type: int,
        current_candle: np.array,
    ):
        price = current_candle[:, candle_body_type]
        print(f"{candle_body_type} price min = {price}")
        return price
