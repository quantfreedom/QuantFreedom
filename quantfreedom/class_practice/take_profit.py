import numpy as np
from quantfreedom.class_practice.enums import (
    DecreasePosition,
    OrderStatus,
    TakeProfitType,
)


class TakeProfitLong:
    take_profit_calculator = None
    risk_reward = None
    tp_fee_pct = None
    
    tp_price = None
    tp_pct = None

    def __init__(
        self,
        take_profit_type: TakeProfitType,
        risk_reward: float,
        tp_fee_pct: float,
    ):
        self.risk_reward = risk_reward
        self.tp_fee_pct = tp_fee_pct

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
            elif take_profit_type == TakeProfitType.ProvidedandRR:
                self.take_profit_calculator = self.calculate_risk_reward
                self.tp_checker = self.check_take_profit_hit_provided_rr

    def calculate_take_profit(self, possible_loss, position_size, average_entry):
        return self.take_profit_calculator(
            possible_loss=possible_loss,
            position_size=position_size,
            average_entry=average_entry,
        )

    def pass_fucntion(self, **vargs):
        return 0.0, 0.0

    def calculate_risk_reward(self, possible_loss, position_size, average_entry):
        print("Long Order - Calculate Take Profit - calculate_risk_reward")
        profit = possible_loss * self.risk_reward
        self.tp_price = (profit + position_size * self.tp_fee_pct + position_size) * (
            average_entry / (position_size - position_size * self.tp_fee_pct)
        )  # math checked

        self.tp_pct = (self.tp_price - average_entry) / average_entry  # math checked
        self.tp_pct = round(self.tp_pct * 100, 2)
        self.tp_price = round(self.tp_price, 2)
        print(
            f"Long Order - Calculate Take Profit - tp_price= {self.tp_price} tp_pct= {self.tp_pct}"
        )
        return (
            self.tp_price,
            self.tp_pct,
        )

    def calculate_take_profit_pct(self, **vargs):
        print("Long Order - Calculate Take Profit - calculate_take_profit_pct")

    def check_take_profit_hit_regular(self, tp_hit, **vargs):
        print("Long Order - Take Profit Checker - check_take_profit_hit")
        if tp_hit:
            raise DecreasePosition(
                exit_price=self.tp_price, order_status=OrderStatus.TakeProfitFilled
            )
            
    def check_take_profit_hit_provided(self, exit_signal, **vargs):
        print("Long Order - Take Profit Checker - check_take_profit_hit_provided")
        if exit_signal:
            print("Long Order - Take Profit Checker - exit_signal=True")
        pass

    def check_take_profit_hit_provided_pct(self, bar_index, exit_signal):
        pass

    def check_take_profit_hit_provided_rr(self, bar_index, exit_signal):
        pass

