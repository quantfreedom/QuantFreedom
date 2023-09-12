import numpy as np
from quantfreedom.class_practice.enums import DecreasePosition, OrderStatus, TakeProfitType


class TakeProfitLong:
    take_profit_calculator = None
    order_result_tp_price = None

    def __init__(
        self,
        take_profit_type: TakeProfitType,
    ):
        if take_profit_type != TakeProfitType.Nothing:
            if take_profit_type == TakeProfitType.RiskReward:
                self.take_profit_calculator = self.calculate_risk_reward
            elif take_profit_type == TakeProfitType.TPPct:
                self.take_profit_calculator = self.calculate_take_profit_pct

    def calculate_take_profit(self, **vargs):
        self.take_profit_calculator(**vargs)
        self.order_result_tp_price = np.random.randint(20)

    def calculate_risk_reward(self, **vargs):
        print("Long Order - Calculate Take Profit - calculate_risk_reward")

    def calculate_take_profit_pct(self, **vargs):
        print("Long Order - Calculate Take Profit - calculate_take_profit_pct")

    def calculate_take_profit_provided(self, **vargs):
        pass

    def check_take_profit_hit(self, **vargs):
        print("Long Order - Take Profit Checker - check_take_profit_hit")
        rand_num = np.random.randint(10)
        if self.order_result_tp_price <= rand_num:
            print(
                f"Long Order - Liqidation Hit Checker - Liq Hit {self.order_result_tp_price} <= {rand_num}"
            )
            raise DecreasePosition(order_status=OrderStatus.LiquidationFilled)

