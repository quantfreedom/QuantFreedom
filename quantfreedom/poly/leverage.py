from enum import Enum


class LeverageType(Enum):
    Static = 1
    Dynamic = 2


class Leverage:
    calculators = {}
    calculate_function = None

    def __init__(self, leverage_type: LeverageType):
        self.calculators[LeverageType.Static] = self.static
        self.calculators[LeverageType.Dynamic] = self.dynamic

        try:
            self.calculate_function = self.calculators[leverage_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self, **vargs):
        self.calculate_function(**vargs)

    def static(self, sl_price):
        print("static leverage")

    def dynamic(self, sl_price):
        print("dynamic leverage and sl price is: ", sl_price)
