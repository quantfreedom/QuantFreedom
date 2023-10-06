import numpy as np
from quantfreedom.enums import (
    DecreasePosition,
    LeverageStrategyType,
    OrderStatus,
    RejectedOrder,
    StopLossStrategyType,
)


class LeverageLong:
    leverage_calculator = None
    liq_hit_checker = None
    order_result_leverage = None
    order_result_liq_price = None

    market_fee_pct = None
    max_leverage = None
    mmr_pct = None
    static_leverage = None

    liq_price = None
    leverage = None

    def __init__(
        self,
        leverage_type: LeverageStrategyType,
        sl_type: StopLossStrategyType,
        market_fee_pct: float,
        max_leverage: float,
        mmr_pct: float,
        static_leverage: float,
    ):
        self.market_fee_pct = market_fee_pct
        self.max_leverage = max_leverage
        self.mmr_pct = mmr_pct
        self.static_leverage = static_leverage

        if leverage_type == LeverageStrategyType.Static:
            self.leverage_calculator = self.set_static_leverage
        elif leverage_type == LeverageStrategyType.Dynamic:
            self.leverage_calculator = self.calculate_dynamic_leverage

        if sl_type == StopLossStrategyType.Nothing or leverage_type == LeverageStrategyType.Nothing:
            self.liq_hit_checker = self.pass_function
        else:
            self.liq_hit_checker = self.check_liq_hit

        # if there is a stop loss then calc liq hit is pass function

    def pass_function(self, **vargs):
        pass

    def calculate_leverage(
        self,
        sl_price: float,
        average_entry: float,
        entry_size_usd: float,
    ):
        return self.leverage_calculator(
            sl_price=sl_price,
            average_entry=average_entry,
            entry_size_usd=entry_size_usd,
        )

    def __calc_liq_price(
        self,
        entry_size_usd: float,
        average_entry: float,
        og_available_balance: float,
        og_cash_used: float,
        og_cash_borrowed: float,
    ):
        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
        initial_margin = entry_size_usd / self.leverage
        fee_to_open = entry_size_usd * self.market_fee_pct  # math checked
        possible_bankruptcy_fee = entry_size_usd * (self.leverage - 1) / self.leverage * self.mmr_pct
        cash_used = initial_margin + fee_to_open + possible_bankruptcy_fee  # math checked

        if cash_used > og_available_balance:
            raise RejectedOrder(order_status=OrderStatus.CashUsedExceed)

        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance = og_available_balance - cash_used
            cash_used += og_cash_used
            cash_borrowed = og_cash_borrowed + entry_size_usd - cash_used

            self.liq_price = round(average_entry * (1 - (1 / self.leverage) + self.mmr_pct), 2)  # math checked
            can_move_sl_to_be = True

        return (
            self.leverage,
            self.liq_price,
            available_balance,
            cash_used,
            cash_borrowed,
            can_move_sl_to_be,
        )

    def set_static_leverage(
        self,
        average_entry: float,
        entry_size_usd: float,
        cash_used: float,
        available_balance: float,
        cash_borrowed: float,
        **vargs,
    ):
        return self.__calc_liq_price(
            entry_size_usd=entry_size_usd,
            leverage=self.static_leverage,
            average_entry=average_entry,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
        )

    def calculate_dynamic_leverage(
        self,
        sl_price: float,
        average_entry: float,
        entry_size_usd: float,
        cash_used: float,
        available_balance: float,
        cash_borrowed: float,
    ):
        self.leverage = -average_entry / (
            (sl_price - sl_price * 0.001)
            - average_entry
            - self.mmr_pct * average_entry
            # TODO: revisit the .001 to add to the sl if you make this backtester have the ability to go live
        )
        self.leverage = round(self.leverage, 1)
        if self.leverage > self.max_leverage:
            self.leverage = self.max_leverage
        elif self.leverage < 1:
            self.leverage = 1

        return self.__calc_liq_price(
            entry_size_usd=entry_size_usd,
            average_entry=average_entry,
            og_cash_used=cash_used,
            og_available_balance=available_balance,
            og_cash_borrowed=cash_borrowed,
        )

    def check_liq_hit(
        self,
        liq_hit: bool,
        exit_fee_pct: float,
    ):
        if liq_hit:
            raise DecreasePosition(
                exit_price=self.liq_price,
                order_status=OrderStatus.LiquidationFilled,
                exit_fee_pct=exit_fee_pct,
            )
