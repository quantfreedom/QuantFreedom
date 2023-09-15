import numpy as np
from quantfreedom.class_practice.enums import (
    AccountState,
    DecreasePosition,
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

    market_fee_pct = None
    max_leverage = None
    mmr_pct = None
    static_leverage = None

    liq_price = None
    leverage = None

    def __init__(
        self,
        leverage_type: LeverageType,
        sl_type: StopLossType,
        market_fee_pct: float,
        max_leverage: float,
        mmr_pct: float,
        static_leverage: float,
    ):
        self.market_fee_pct = market_fee_pct
        self.max_leverage = max_leverage
        self.mmr_pct = mmr_pct
        self.static_leverage = static_leverage

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

    def calculate_leverage(
        self,
        account_state: AccountState,
        sl_price: float,
        average_entry: float,
        entry_size: float,
    ):
        return self.leverage_calculator(
            account_state=account_state,
            sl_price=sl_price,
            average_entry=average_entry,
            entry_size=entry_size,
        )

    def __calc_liq_price(
        self,
        entry_size: float,
        average_entry: float,
        og_available_balance: float,
        og_cash_used: float,
        og_cash_borrowed: float,
    ):
        print("Long Order - Calculate Leverage - __calc_liq_price")

        # Getting Order Cost
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
        initial_margin = entry_size / self.leverage
        fee_to_open = entry_size * self.market_fee_pct  # math checked
        possible_bankruptcy_fee = (
            entry_size * (self.leverage - 1) / self.leverage * self.mmr_pct
        )
        cash_used = (
            initial_margin + fee_to_open + possible_bankruptcy_fee
        )  # math checked

        if cash_used > og_available_balance:
            raise RejectedOrderError(order_status=OrderStatus.CashUsedExceed)

        else:
            # liq formula
            # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
            available_balance = og_available_balance - cash_used
            cash_used += og_cash_used
            cash_borrowed = og_cash_borrowed + entry_size - cash_used

            self.liq_price = average_entry * (
                1 - (1 / self.leverage) + self.mmr_pct
            )  # math checked
        print(
            f"Long Order - Calculate Leverage - leverage= {round(self.leverage,2)} liq_price= {round(self.liq_price,2)}"
        )
        print(
            f"Long Order - Calculate Leverage - available_balance= {round(available_balance,2)}"
        )
        print(
            f"Long Order - Calculate Leverage - cash_used= {round(cash_used,2)} cash_borrowed= {round(cash_borrowed,2)}"
        )
        return (
            self.leverage,
            self.liq_price,
            available_balance,
            cash_used,
            cash_borrowed,
        )

    def set_static_leverage(
        self,
        average_entry: float,
        entry_size: float,
        cash_used: float,
        available_balance: float,
        cash_borrowed: float,
        **vargs,
    ):
        print("Long Order - Calculate Leverage - set_static_leverage")
        return self.__calc_liq_price(
            entry_size=entry_size,
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
        entry_size: float,
        cash_used: float,
        available_balance: float,
        cash_borrowed: float,
    ):
        print("Long Order - Calculate Leverage - calculate_dynamic_leverage")
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
            entry_size=entry_size,
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
