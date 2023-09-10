

class TakeProfitLong:
    calculators = {}
    calculate_function = None

    def __init__(self, take_profit_type: TakeProfitType):
        self.calculators[TakeProfitType.RiskReward] = self.risk_reward
        self.calculators[TakeProfitType.TPPct] = self.take_profit_pct

        try:
            self.calculate_function = self.calculators[take_profit_type]
        except KeyError as e:
            print(f"Calculator not found -> {repr(e)}")

    def calculate(self, **vargs):
        return self.calculate_function(**vargs)

    def risk_reward(self, **vargs):
        profit = vargs["possible_loss"] * vargs["risk_reward"]
        position_size = vargs["position_size"]
        limit_fee_pct = vargs["limit_fee_pct"]
        average_entry = vargs["average_entry"]

        take_profit_price = (profit + position_size * limit_fee_pct + position_size) * (
            average_entry / (position_size - position_size * limit_fee_pct)
        )  # math checked

        take_profit_pct = (
            take_profit_price - average_entry
        ) / average_entry  # math checked
        take_profit_pct = round(take_profit_pct * 100, 2)
        take_profit_price = round(take_profit_price, 2)
        return take_profit_price, take_profit_pct

    def take_profit_pct(self):
        print("Take Profit %")
