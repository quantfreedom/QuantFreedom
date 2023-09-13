import numpy as np
from quantfreedom.class_practice.enums import (
    DecreasePosition,
    OrderStatus,
    TakeProfitType,
)


class TakeProfitLong:
    take_profit_calculator = None
    risk_reward = None
    limit_fee_pct = None

    def __init__(
        self,
        take_profit_type: TakeProfitType,
        risk_reward: float,
        limit_fee_pct: float,
        exit_signals: np.array,
    ):
        self.risk_reward = risk_reward
        self.limit_fee_pct = limit_fee_pct
        self.exit_signals = exit_signals

        if take_profit_type != TakeProfitType.Nothing:
            if take_profit_type == TakeProfitType.RiskReward:
                self.take_profit_calculator = self.calculate_risk_reward
                self.tp_checker = self.check_take_profit_hit_regular
            elif take_profit_type == TakeProfitType.TPPct:
                self.take_profit_calculator = self.calculate_take_profit_pct
                self.tp_checker = self.check_take_profit_hit_regular
            elif take_profit_type == TakeProfitType.Provided:
                self.take_profit_calculator = self.pass_fucntion
                self.tp_checker = self.check_take_profit_hit_provided
            elif take_profit_type == TakeProfitType.ProvidedandPct:
                self.take_profit_calculator = self.calculate_take_profit_pct
                self.tp_checker = self.check_take_profit_hit_provided_pct

    def calculate_take_profit(self, possible_loss, position_size, average_entry):
        return self.take_profit_calculator(
            possible_loss=possible_loss,
            position_size=position_size,
            average_entry=average_entry,
        )
    def pass_fucntion(self):
        pass
    
    def calculate_risk_reward(self, possible_loss, position_size, average_entry):
        print("Long Order - Calculate Take Profit - calculate_risk_reward")
        profit = possible_loss * self.risk_reward
        tp_price = (profit + position_size * self.limit_fee_pct + position_size) * (
            average_entry / (position_size - position_size * self.limit_fee_pct)
        )  # math checked

        tp_pct = (tp_price - average_entry) / average_entry  # math checked
        tp_pct = round(tp_pct * 100, 2)
        tp_price = round(tp_price, 2)
        print(
            f"Long Order - Calculate Take Profit - tp_price= {tp_price} tp_pct= {tp_pct}"
        )
        return (
            tp_price,
            tp_pct,
        )

    def calculate_take_profit_pct(self, **vargs):
        print("Long Order - Calculate Take Profit - calculate_take_profit_pct")

    def calculate_take_profit_provided(self, **vargs):
        pass

    def check_take_profit_hit(self, **vargs):
        return self.tp_checker()
        print("Long Order - Take Profit Checker - check_take_profit_hit")
        
    def check_take_profit_hit_provided(self, bar_index):
        if self.exit_signals[bar_index]:
            raise DecreasePosition()
        print("Long Order - Take Profit Checker - check_take_profit_hit")
        
    def check_take_profit_hit_provided_pct(self, bar_index):
        pass
        
    def check_take_profit_hit_regular(self, **vargs):
        pass
