from quantfreedom.class_practice.enums import TakeProfitType


class TakeProfitLong:
    take_profit_calculator = None

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

    def calculate_risk_reward(self, **vargs):
        print("Long Order - Calculate Take Profit - calculate_risk_reward")

    def calculate_take_profit_pct(self, **vargs):
        print("Long Order - Calculate Take Profit - calculate_take_profit_pct")

    def calculate_take_profit_provided(self, **vargs):
        pass

    def check_take_profit_hit(self, **vargs):
        print("Long Order - Take Profit Checker - check_take_profit_hit")

