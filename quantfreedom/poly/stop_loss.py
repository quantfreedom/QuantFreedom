import numpy as np
from enum import Enum
from collections import namedtuple


class StopLossType(Enum):
    SLBasedOnCandleBody = 1
    SLPct = 2


class CandleBody(Enum):
    Open = 1
    High = 2
    Low = 3
    Close = 4


class StopLossCalculator:
    sl_price = None
    sl_pct = None
    candles = None
    calculate_function = None
    calculators = ()

    def __init__(
        self,
        sl_type: StopLossType,
        candle_body: CandleBody = None,
        sl_pct: np.array = None,
        current_candle: NamedTuple = None,
    ):
        if sl_type == StopLossType.SLBasedOnCandleBody:
            if candle_body == CandleBody.Open:
                self.calculators[CandleBody.Open] = self.sl_based_on_open
            elif candle_body == CandleBody.High:
                self.calculators[CandleBody.High] = self.sl_based_on_high
            elif candle_body == CandleBody.Low:
                self.calculators[CandleBody.Low] = self.sl_based_on_low
            elif candle_body == CandleBody.Close:
                self.calculators[CandleBody.Close] = self.sl_based_on_close
        else:
            self.calculators[StopLossType.SLPct] = self.sl_pct_calc
        self.sl_pct = sl_pct


        try:
            self.calculate_function = self.calculators[sl_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self):
        self.calculate_function()

    def sl_based_on_open(self, candles):
        self.sl_price = candles.low.min() - (candles.low.min() * sl_based_on_add_pct)

    def sl_based_on_high(self, candles):
        self.sl_price = candles.high.min() - (candles.high.min() * sl_based_on_add_pct)

    def sl_based_on_low(self, candles):
        self.sl_price = candles.low.min() - (candles.low.min() * sl_based_on_add_pct)

    def sl_based_on_close(self, candles):
        self.sl_price = candles.close.min() - (
            candles.close.min() * sl_based_on_add_pct
        )

    def sl_pct_calc(self):
        print("Stop loss percent")
        self.sl_pct = 6
        self.sl_price = 2
