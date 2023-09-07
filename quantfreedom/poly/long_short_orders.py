import numpy as np
import pandas as pd
from quantfreedom.poly.enums import AccountState, OrderSettings, ExchangeSettings, OrderType
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

    def instantiate(order_type : OrderType, **vargs):
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
        self.leverage = Leverage(leverage_type)
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


class LongOrder(Order):
    def calc_stop_loss(self, symbol_price_data):
        print("LongOrder::stop_loss")
        return self.stop_loss.sl_calculator(symbol_price_data=symbol_price_data)

    def calc_leverage(self):
        print("LongOrder::leverage")
        self.leverage.calculate()

    def calc_entry_size(self, **vargs):
        print("LongOrder::entry")
        self.entry_size.calculate(
            account_state_equity=self.account_state.equity,
            **vargs,
        )

    def calc_take_profit(self):
        print("LongOrder::take_profit")
        self.take_profit.calculate()
