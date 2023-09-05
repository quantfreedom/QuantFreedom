import numpy as np
from typing import NamedTuple

from quantfreedom.poly.stop_loss import StopLossCalculator, StopLossType
from quantfreedom.poly.leverage import Leverage, LeverageType
from quantfreedom.poly.entry_size import EntrySize, EntrySizeType
from quantfreedom.poly.take_profit import TakeProfit, TakeProfitType


class Order:
    stop_loss = None
    leverage = None
    entry_size = None
    take_profit = None

    def __init__(
        self,
        sl_type: StopLossType,
        leverage_type: LeverageType,
        entry_size_type: EntrySizeType,
        tp_type: TakeProfitType,
        order_info: NamedTuple,
        current_candle: NamedTuple,
    ):
        self.stop_loss = StopLossCalculator(
            sl_type=sl_type,
            sl_pct=order_info.sl_pct,
            current_candle=current_candle,
        )
        self.leverage = Leverage(leverage_type)
        self.entry_size = EntrySize(self.stop_loss, entry_size_type)
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
    def calc_stop_loss(self):
        print("LongOrder::stop_loss")
        self.stop_loss.calculate()

    def calc_leverage(self):
        print("LongOrder::leverage")
        self.leverage.calculate(sl_price=self.stop_loss.sl_price)

    def calc_entry_size(self):
        print("LongOrder::entry")
        self.entry_size.calculate()

    def calc_take_profit(self):
        print("LongOrder::take_profit")
        self.take_profit.calculate()


class ShortOrder(Order):
    def calc_stop_loss(self):
        print("ShortOrder::stop_loss")
        self.stop_loss.calculate()

    def calc_leverage(self):
        print("ShortOrder::leverage")
        self.leverage.calculate(sl_price=self.stop_loss.sl_price)

    def calc_entry_size(self):
        print("ShortOrder::entry")
        self.entry_size.calculate()

    def calc_take_profit(self):
        print("ShortOrder::take_profit")
        self.take_profit.calculate()
