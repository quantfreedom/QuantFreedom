from enum import Enum


class StopLossType(Enum):
    SLBasedOnCandleBody = 1
    SLPct = 2


class StopLossCalculator:
    sl_price = None
    calculators = {}
    calculate_function = None

    def __init__(self, sl_type: StopLossType):
        self.calculators[StopLossType.SLBasedOnCandleBody] = self.sl_based_on_calc
        self.calculators[StopLossType.SLPct] = self.sl_pct_calc

        try:
            self.calculate_function = self.calculators[sl_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self):
        self.calculate_function()

    def sl_based_on_calc(self):
        print("Stop loss based on candle body")
        self.sl_price = 1

    def sl_pct_calc(self):
        print("Stop loss percent")
        self.sl_price = 2
