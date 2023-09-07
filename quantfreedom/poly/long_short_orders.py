import numpy as np
import pandas as pd
from quantfreedom.poly.enums import (
    AccountState,
    OrderSettings,
    ExchangeSettings,
    OrderType,
)
from quantfreedom.poly.stop_loss import StopLossCalculator, StopLossType, CandleBody
from quantfreedom.poly.leverage import Leverage, LeverageType
from quantfreedom.poly.entry_size import EntrySize, EntrySizeType
from quantfreedom.poly.take_profit import TakeProfit, TakeProfitType


class Order:
    stop_loss = None
    leverage = None
    entry_size = None
    take_profit = None
    account_state = None
    price_data = None
    exchange_settings = None

    def instantiate(order_type: OrderType, **vargs):
        if order_type == OrderType.Long:
            return LongOrder(**vargs)

    def __init__(
        self,
        sl_type: StopLossType,
        candle_body: CandleBody,
        leverage_type: LeverageType,
        entry_size_type: EntrySizeType,
        tp_type: TakeProfitType,
        account_state: AccountState,
        order_settings: OrderSettings,
        exchange_settings: ExchangeSettings,
    ):
        self.account_state = account_state
        self.exchange_settings = exchange_settings

        self.stop_loss = StopLossCalculator(
            sl_type=sl_type,
            candle_body=candle_body,
            order_settings=order_settings,
        )
        self.leverage = Leverage(
            leverage_type=leverage_type,
            max_leverage=exchange_settings.max_lev,
        )
        self.entry_size = EntrySize(
            entry_size_type=entry_size_type,
            order_settings=order_settings,
            exchange_settings=exchange_settings,
        )
        self.take_profit = TakeProfit(tp_type)

    def calc_stop_loss(self):
        pass

    def calc_leverage(self):
        pass

    def calc_entry_size(self):
        pass

    def calc_take_profit(self):
        pass

    def calc_average_entry(self):
        pass


class LongOrder(Order):
    def calc_stop_loss(self, symbol_price_data):
        print("LongOrder::stop_loss")
        return self.stop_loss.sl_calculator(symbol_price_data=symbol_price_data)

    def calc_leverage(self, **vargs):
        print("LongOrder::leverage")
        self.leverage.calculate(**vargs)

    def calc_entry_size(self, **vargs):
        print("LongOrder::entry")
        self.entry_size.calculate(
            account_state_equity=self.account_state.equity,
            **vargs,
        )

    def calc_take_profit(self):
        print("LongOrder::take_profit")
        self.take_profit.calculate()

    def calc_average_entry(self, average_entry):
        if position_old != 0.0:
            average_entry_new = (size_value + position_old) / (
                (size_value / prices.entry) + (position_old / average_entry_new)
            )
        else:
            average_entry_new = prices.entry
