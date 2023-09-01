from enum import Enum


class TakeProfitType(Enum):
    RiskReward = 1
    TPPct = 2


class TakeProfit:
    calculators = {}
    calculate_function = None

    def __init__(self, take_profit_type: TakeProfitType):
        self.calculators[TakeProfitType.RiskReward] = self.risk_reward
        self.calculators[TakeProfitType.TPPct] = self.take_profit_pct

        try:
            self.calculate_function = self.calculators[take_profit_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self):
        self.calculate_function()

    def risk_reward(self):
        print("Take Profit Risk Reward")

    def take_profit_pct(self):
        print("Take Profit %")
