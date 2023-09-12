import numpy as np
from quantfreedom.class_practice.enums import (
    LeverageType,
    OrderStatus,
    RejectedOrderError,
    StopLossType,
)


class LeverageLong:
    leverage_calculator = None
    liq_hit_checker = None
    order_result_leverage = None
    order_result_liq_price = None
    

    def __init__(
        self,
        leverage_type: LeverageType,
        sl_type: StopLossType,
    ):
        if leverage_type == LeverageType.Static:
            self.leverage_calculator = self.set_static_leverage
        elif leverage_type == LeverageType.Dynamic:
            self.leverage_calculator = self.calculate_dynamic_leverage
        
        if sl_type == StopLossType.Nothing or leverage_type == LeverageType.Nothing:
            self.liq_hit_checker = self.pass_function
        else:
            self.liq_hit_checker = self.check_liq_hit
            
        # if there is a stop loss then calc liq hit is pass function

    def pass_function(self, **vargs):
        print("Long Order - Liqidation checker - pass_function")
        pass

    def calculate_leverage(self, **vargs):
        return self.leverage_calculator(**vargs)

    def __calc_liq_price(self, **vargs):
        print("Long Order - Calculate Leverage - __calc_liq_price")
        return np.random.randint(5)


    def set_static_leverage(self, **vargs):
        print("Long Order - Calculate Leverage - set_static_leverage")
        self.__calc_liq_price()
        return np.random.randint(4)

    def calculate_dynamic_leverage(self, **vargs):
        print("Long Order - Calculate Leverage - calculate_dynamic_leverage")
        self.__calc_liq_price()
        return np.random.randint(4)

    def check_liq_hit(self, **vargs):
        print("Long Order - Liqidation checker - check_liq_hit")
