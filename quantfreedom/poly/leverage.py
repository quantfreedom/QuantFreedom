from quantfreedom.poly.enums import LeverageType


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

    def calculate(self):
        self.calculate_function()

    def static(self):
        print("static leverage")

    def dynamic(self):
        print("dynamic leverage and sl price is: ")
