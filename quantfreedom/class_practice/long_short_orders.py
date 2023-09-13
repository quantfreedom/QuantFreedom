import numpy as np
from quantfreedom.class_practice.increase_position import IncreasePositionLong
from quantfreedom.class_practice.leverage import LeverageLong
from quantfreedom.class_practice.stop_loss import StopLossLong
from quantfreedom.class_practice.take_profit import TakeProfitLong
from quantfreedom.class_practice.enums import (
    AccountState,
    OrderStatus,
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
    symbol_price_data = None
    exit_signals = None
    exchange_settings = None
    order_result = None
    order_settings = None

    # order result variables
    sl_price = None
    entry_size = None
    position_size = None
    entry_price = None
    average_entry = None
    possible_loss = None
    sl_pct = None
    liq_price = None
    available_balance = None
    cash_used = None
    cash_borrowed = None
    tp_pct = None
    tp_price = None
    leverage = None

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
        symbol_price_data: np.array,
        exit_signals: np.array,
    ):
        self.order_settings = order_settings
        self.account_state = account_state
        self.exchange_settings = exchange_settings
        self.order_result = order_result
        self.symbol_price_data = symbol_price_data
        self.exit_signals = exit_signals

        if self.order_settings.order_type == OrderType.Long:
            self.obj_stop_loss = StopLossLong(
                sl_based_on_add_pct=self.order_settings.sl_based_on_add_pct,
                sl_based_on_lookback=self.order_settings.sl_based_on_lookback,
                sl_candle_body_type=self.order_settings.sl_candle_body_type,
                sl_to_be_based_on_candle_body_type=self.order_settings.sl_to_be_based_on_candle_body_type,
                sl_to_be_when_pct_from_candle_body=self.order_settings.sl_to_be_when_pct_from_candle_body,
                sl_to_be_zero_or_entry=self.order_settings.sl_to_be_zero_or_entry,
                sl_type=self.order_settings.stop_loss_type,
                trail_sl_based_on_candle_body_type=self.order_settings.trail_sl_based_on_candle_body_type,
                trail_sl_by_pct=self.order_settings.trail_sl_by_pct,
                trail_sl_when_pct_from_candle_body=self.order_settings.trail_sl_when_pct_from_candle_body,
            )
            self.obj_increase_posotion = IncreasePositionLong(
                increase_position_type=self.order_settings.increase_position_type,
                stop_loss_type=self.order_settings.stop_loss_type,
                market_fee_pct=self.exchange_settings.market_fee_pct,
                max_equity_risk_pct=self.order_settings.max_equity_risk_pct,
                risk_account_pct_size=self.order_settings.risk_account_pct_size,
                max_order_size_value=self.exchange_settings.max_order_size_value,
                min_order_size_value=self.exchange_settings.min_order_size_value,
            )
            self.obj_leverage = LeverageLong(
                leverage_type=self.order_settings.leverage_type,
                sl_type=self.order_settings.stop_loss_type,
                market_fee_pct=self.exchange_settings.market_fee_pct,
                max_leverage=self.exchange_settings.max_leverage,
                static_leverage=self.order_settings.static_leverage,
                mmr_pct=self.exchange_settings.mmr_pct,
            )
            self.obj_take_profit = TakeProfitLong(
                take_profit_type=self.order_settings.take_profit_type,
                risk_reward=self.order_settings.risk_reward,
                limit_fee_pct=self.exchange_settings.limit_fee_pct,
                exit_signals=self.exit_signals,
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

    def fill_order_result_successful_entry(self, **vargs):
        self.account_state = AccountState(
            available_balance=self.available_balance,
            cash_borrowed=self.cash_borrowed,
            cash_used=self.cash_used,
            equity=self.account_state.equity,
        )
        self.order_result = OrderResult(
            average_entry=self.average_entry,
            fees_paid=0.0,
            leverage=self.leverage,
            liq_price=self.liq_price,
            order_status=OrderStatus.EntryFilled,
            possible_loss=self.possible_loss,
            entry_size=self.entry_size,
            entry_price=self.entry_price,
            exit_price=0.0,
            position_size=self.position_size,
            realized_pnl=0.0,
            sl_pct=self.sl_pct,
            sl_price=self.sl_price,
            tp_pct=self.tp_pct,
            tp_price=self.tp_price,
        )

    def fill_rejected_order_record(self, **vargs):
        print("Order - fill_rejected_order_record")

    def fill_strat_records_nb(self, **vargs):
        print("Order - fill_strat_records_nb")


class LongOrder(Order):
    def calculate_stop_loss(self, bar_index):
        self.sl_price = self.obj_stop_loss.calculate_stop_loss(
            bar_index=bar_index,
            symbol_price_data=self.symbol_price_data,
        )

    def calculate_increase_posotion(self, entry_price):
        (
            self.average_entry,
            self.entry_price,
            self.entry_size,
            self.position_size,
            self.possible_loss,
            self.sl_pct,
        ) = self.obj_increase_posotion.calculate_increase_posotion(
            account_state_equity=self.account_state.equity,
            average_entry=self.order_result.average_entry,
            entry_price=entry_price,
            in_position=self.order_result.position_size > 0,
            position_size=self.order_result.position_size,
            possible_loss=self.order_result.possible_loss,
            sl_price=self.sl_price,
        )

    def calculate_leverage(self):
        (
            self.leverage,
            self.liq_price,
            self.available_balance,
            self.cash_used,
            self.cash_borrowed,
        ) = self.obj_leverage.leverage_calculator(
            average_entry=self.average_entry,
            sl_price=self.sl_price,
            account_state=self.account_state,
            entry_size=self.entry_size,
        )

    def calculate_take_profit(self):
        (
            self.tp_price,
            self.tp_pct,
        ) = self.obj_take_profit.take_profit_calculator(
            possible_loss=self.possible_loss,
            position_size=self.position_size,
            average_entry=self.average_entry,
        )

    def check_stop_loss_hit(self, **vargs):
        self.obj_stop_loss.check_stop_loss_hit()

    def check_liq_hit(self, **vargs):
        self.obj_leverage.liq_hit_checker()

    def check_take_profit_hit(self, **vargs):
        self.obj_take_profit.tp_checker()

    def check_move_stop_loss_to_be(self, **vargs):
        self.obj_stop_loss.check_move_stop_loss_to_be()

    def check_move_trailing_stop_loss(self, **vargs):
        self.obj_stop_loss.check_move_trailing_stop_loss()
