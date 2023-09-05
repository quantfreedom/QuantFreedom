import numpy as np
from math import floor
from enum import Enum
from collections import namedtuple

from quantfreedom.poly.enums import OrderSettings


class StopLossType(Enum):
    SLBasedOnCandleBody = 1
    SLPct = 2


class CandleBody(Enum):
    Open = 1
    High = 2
    Low = 3
    Close = 4


class StopLossCalculator:
    calculator = None
    sl_price = None
    order_settings = None

    def __init__(
        self,
        sl_type: StopLossType,
        candle_body: CandleBody,
        order_settings: OrderSettings,
    ):
        if sl_type == StopLossType.SLBasedOnCandleBody:
            if candle_body == CandleBody.Open:
                self.calculator = self.sl_based_on_open
            elif candle_body == CandleBody.High:
                self.calculator = self.sl_based_on_high
            elif candle_body == CandleBody.Low:
                self.calculator = self.sl_based_on_low
            elif candle_body == CandleBody.Close:
                self.calculator = self.sl_based_on_close
        else:
            self.calculator = self.sl_pct_calc

        self.order_settings = order_settings

    def calculate(self, **vargs):
        return self.calculator(**vargs)

    def sl_based_on_open(self, **vargs):
        pass

    def sl_based_on_high(self, **vargs):
        pass

    def sl_based_on_low(self, **vargs):
        candle_low = vargs["price_data"].low.values.min()
        self.sl_price = floor(
            candle_low - (candle_low * self.order_settings.sl_based_on_add_pct)
        )
        print("sl price is ", self.sl_price)
        return float(self.sl_price)

    def sl_based_on_close(self, **vargs):
        pass

    def sl_pct_calc(self, **vargs):
        pass
