import numpy as np
from quantfreedom.class_practice.enums import (
    LeverageType,
    OrderStatus,
    RejectedOrderError,
)


class LeverageLong:
    leverage_calculator = None

    def __init__(
        self,
        leverage_type: LeverageType,
    ):
        if leverage_type != LeverageType.Nothing:
            if leverage_type == LeverageType.Static:
                self.leverage_calculator = self.set_static_leverage
            elif leverage_type == LeverageType.Dynamic:
                self.leverage_calculator = self.calculate_dynamic_leverage

    def calculate_leverage(self, **vargs):
        return self.leverage_calculator(**vargs)

    def __calc_liq_price(self, **vargs):
        print("Long Order - Calculate Leverage - __calc_liq_price")

    def set_static_leverage(self, **vargs):
        print("Long Order - Calculate Leverage - set_static_leverage")
        self.__calc_liq_price()
        return np.random.randint(4)

    def calculate_dynamic_leverage(self, **vargs):
        print("Long Order - Calculate Leverage - calculate_dynamic_leverage")
        self.__calc_liq_price()
        return np.random.randint(4)
