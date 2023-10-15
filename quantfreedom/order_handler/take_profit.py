import numpy as np
from quantfreedom.custom_logger import CustomLogger
from quantfreedom.enums import (
    DecreasePosition,
    OrderStatus,
    TakeProfitStrategyType,
)
import logging

from quantfreedom.helper_funcs import round_size_by_tick_step

info_logger = logging.getLogger("info")


class TakeProfitLong:
    take_profit_calculator = None
    risk_reward = None
    tp_fee_pct = None
    market_fee_pct = None
    tp_price = None

    def __init__(
        self,
        take_profit_type: TakeProfitStrategyType,
        risk_reward: float,
        tp_fee_pct: float,
        market_fee_pct: float,
        price_tick_step: float,
    ):
        self.risk_reward = risk_reward
        self.tp_fee_pct = tp_fee_pct
        self.price_tick_step = price_tick_step
        self.market_fee_pct = market_fee_pct

        if take_profit_type != TakeProfitStrategyType.Nothing:
            if take_profit_type == TakeProfitStrategyType.RiskReward:
                self.take_profit_calculator = self.calc_risk_reward_tp_price
                self.tp_checker = self.check_take_profit_hit_regular
            elif take_profit_type == TakeProfitStrategyType.TPPct:
                self.take_profit_calculator = self.calculate_take_profit_pct
                self.tp_checker = self.check_take_profit_hit_regular
            elif take_profit_type == TakeProfitStrategyType.Provided:
                self.take_profit_calculator = self.pass_fucntion
                self.tp_checker = self.check_take_profit_hit_provided
            elif take_profit_type == TakeProfitStrategyType.ProvidedandPct:
                self.take_profit_calculator = self.calculate_take_profit_pct
                self.tp_checker = self.check_take_profit_hit_provided_pct
            elif take_profit_type == TakeProfitStrategyType.ProvidedandRR:
                self.take_profit_calculator = self.calc_risk_reward_tp_price
                self.tp_checker = self.check_take_profit_hit_provided_rr

    def calculate_take_profit(self, possible_loss, position_size_usd, average_entry):
        return self.take_profit_calculator(
            possible_loss=possible_loss,
            position_size_usd=position_size_usd,
            average_entry=average_entry,
        )

    def pass_fucntion(self, **vargs):
        return np.nan, np.nan, 0

    def calc_risk_reward_tp_price(self, possible_loss, position_size_usd, average_entry):
        profit = possible_loss * self.risk_reward
        tp_price = (
            (profit * average_entry)
            + (average_entry * position_size_usd)
            + (average_entry * self.market_fee_pct * position_size_usd)
        ) / (position_size_usd * (1 - self.tp_fee_pct))
        
        self.tp_price = round_size_by_tick_step(
            user_num=tp_price,
            exchange_num=self.price_tick_step,
        )
        # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(t-e%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p

        tp_pct = round((self.tp_price - average_entry) / average_entry, 4)

        return self.tp_price, tp_pct, OrderStatus.EntryFilled

    def calculate_take_profit_pct(self, **vargs):
        pass

    def check_take_profit_hit_regular(
        self,
        current_candle: np.array,
        exit_fee_pct: float,
        **vargs,
    ):
        if current_candle["high"] > self.tp_price:
            info_logger.debug("Take Profit Hit")
            raise DecreasePosition(
                exit_price=self.tp_price,
                order_status=OrderStatus.TakeProfitFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            info_logger.debug("No tp hit")

    def check_take_profit_hit_provided(
        self,
        exit_signal: float,
        exit_fee_pct: float,
        **vargs,
    ):
        if not np.isnan(exit_signal):
            info_logger.debug("Take Profit Hit")
            raise DecreasePosition(
                exit_price=exit_signal,  # sending the close of the current candle for now as exit price
                order_status=OrderStatus.TakeProfitFilled,
                exit_fee_pct=exit_fee_pct,
            )
        else:
            info_logger.debug("tp not hit")
        pass

    def check_take_profit_hit_provided_pct(self, bar_index, exit_signal):
        pass

    def check_take_profit_hit_provided_rr(self, bar_index, exit_signal):
        pass
