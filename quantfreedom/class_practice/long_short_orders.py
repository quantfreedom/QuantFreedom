import numpy as np
from quantfreedom.class_practice.increase_position import IncreasePositionLong
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
    obj_increase_posotion = None
    obj_take_profit = None
    account_state = None
    price_data = None
    exchange_settings = None
    order_result = None
    order_settings = None

    # order result variables
    order_result_position_size = None

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
            self.obj_stop_loss = StopLossLong(
                sl_type=self.order_settings.stop_loss_type,
                sl_candle_body_type=self.order_settings.sl_candle_body_type,
                sl_to_be_based_on_candle_body_type=self.order_settings.sl_to_be_based_on_candle_body_type,
                sl_to_be_when_pct_from_candle_body=self.order_settings.sl_to_be_when_pct_from_candle_body,
                sl_to_be_zero_or_entry=self.order_settings.sl_to_be_zero_or_entry,
                trail_sl_based_on_candle_body_type=self.order_settings.trail_sl_based_on_candle_body_type,
                trail_sl_when_pct_from_candle_body=self.order_settings.trail_sl_when_pct_from_candle_body,
                trail_sl_by_pct=self.order_settings.trail_sl_by_pct,
            )
            self.obj_increase_posotion = IncreasePositionLong(
                increase_position_type=self.order_settings.increase_position_type,
                stop_loss_type=self.order_settings.stop_loss_type,
            )
            self.obj_leverage = LeverageLong(
                leverage_type=self.order_settings.leverage_type,
                sl_type=self.order_settings.stop_loss_type,
            )
            self.obj_take_profit = TakeProfitLong(
                take_profit_type=self.order_settings.take_profit_type,
            )
        elif self.order_settings.order_type == OrderType.Short:
            pass

    def calculate_stop_loss(self, **vargs):
        pass

    def calculate_leverage(self, **vargs):
        pass

    def calculate_increase_posotion(self, **vargs):
        pass

    def calculate_take_profit(self, **vargs):
        pass

    def check_stop_loss_hit(self, **vargs):
        pass

    def check_liq_hit(self, **vargs):
        pass

    def check_take_profit_hit(self, **vargs):
        pass

    def check_move_stop_loss_to_be(self, **vargs):
        pass

    def check_move_trailing_stop_loss(self, **vargs):
        pass

    def fill_order_result_entry(self, **vargs):
        self.order_result = OrderResult(position_size=self.order_result_position_size)
        print(
            "Order - fill_order_result_entry - position size =",
            self.order_result.position_size,
        )

    def fill_rejected_order_record(self, **vargs):
        print("Order - fill_rejected_order_record")

    def fill_strat_records_nb(self, **vargs):
        print("Order - fill_strat_records_nb")


class LongOrder(Order):
    def calculate_stop_loss(self, **vargs):
        self.obj_stop_loss.calculate_stop_loss()

    def calculate_increase_posotion(self, **vargs):
        self.obj_increase_posotion.calculate_increase_posotion(**vargs)

    def calculate_leverage(self, **vargs):
        self.order_result_position_size = self.obj_leverage.leverage_calculator()

    def calculate_take_profit(self, **vargs):
        self.obj_take_profit.take_profit_calculator()

    def check_stop_loss_hit(self, **vargs):
        self.obj_stop_loss.check_stop_loss_hit()

    def check_liq_hit(self, **vargs):
        self.obj_leverage.liq_hit_checker()

    def check_take_profit_hit(self, **vargs):
        self.obj_take_profit.check_take_profit_hit()

    def check_move_stop_loss_to_be(self, **vargs):
        self.obj_stop_loss.check_move_stop_loss_to_be()

    def check_move_trailing_stop_loss(self, **vargs):
        self.obj_stop_loss.check_move_trailing_stop_loss()
