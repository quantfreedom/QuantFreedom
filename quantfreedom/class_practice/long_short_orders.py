import numpy as np
from quantfreedom.class_practice.entry_size import EntrySizeLong
from quantfreedom.class_practice.leverage import LeverageLong
from quantfreedom.class_practice.stop_loss import StopLossLong
from quantfreedom.class_practice.take_profit import TakeProfitLong
from quantfreedom.class_practice.enums import (
    AccountState,
    OrderType,
    OrderSettings,
    ExchangeSettings,
    OrderResult,
)


class Order:
    obj_stop_loss = None
    obj_leverage = None
    obj_entry_size = None
    obj_take_profit = None
    account_state = None
    price_data = None
    exchange_settings = None
    order_result = None
    order_settings = None

    def instantiate(
        order_type: OrderType, **vargs
    ):  # TODO: we should only have to do this once not everytime
        if order_type == OrderType.Long:
            return LongOrder(**vargs)

    def __init__(
        self,
        account_state: AccountState,
        order_settings: OrderSettings,
        exchange_settings: ExchangeSettings,
        order_result: OrderResult,
    ):
        self.order_settings = order_settings
        self.account_state = account_state
        self.exchange_settings = exchange_settings
        self.order_result = order_result

        if self.order_settings.order_type == OrderType.Long:
            self.obj_stop_loss = StopLossLong()
            self.obj_entry_size = EntrySizeLong()
            self.obj_leverage = LeverageLong()
            self.obj_take_profit = TakeProfitLong()
        elif self.order_settings.order_type == OrderType.Short:
            pass

    def calc_stop_loss(self):
        pass

    def calc_leverage(self):
        pass

    def calc_entry_size(self):
        pass

    def calc_take_profit(self):
        pass

    def check_stop_loss(self):
        pass

    def fill_order_result_entry(self, **vargs):
        print("Order - fill_order_result_entry")

    def fill_rejected_order_record(self, **vargs):
        print("Order - fill_rejected_order_record")

    def fill_strat_records_nb(self, **vargs):
        print("Order - fill_strat_records_nb")


class LongOrder(Order):
    def calc_stop_loss(self, **vargs):
        print("Long Order - calc_stop_loss")

    def calc_entry_size(self, **vargs):
        print("Long Order - calc_entry_size")

    def calc_leverage(self, **vargs):
        print("Long Order - calc_leverage")

    def calc_take_profit(self, **vargs):
        print("Long Order - calc_take_profit")
