import numpy as np
from quantfreedom.class_practice.increase_position import IncreasePositionLong
from quantfreedom.class_practice.leverage import LeverageLong
from quantfreedom.class_practice.stop_loss import StopLossLong
from quantfreedom.class_practice.take_profit import TakeProfitLong
from quantfreedom.class_practice.enums import (
    AccountState,
    DecreasePosition,
    OrderStatus,
    OrderType,
    OrderSettings,
    ExchangeSettings,
    OrderResult,
    TakeProfitFeeType,
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
    order_settings = None
    tp_fee_pct = None

    # order result variables
    available_balance = 0.0
    cash_borrowed = 0.0
    cash_used = 0.0
    equity = 0.0
    
    average_entry = 0.0
    entry_price = 0.0
    entry_size = 0.0
    exit_price = 0.0
    fees_paid = 0.0
    leverage = 1.0
    liq_price = 0.0
    order_status = 0.0
    position_size = 0.0
    possible_loss = 0.0
    realized_pnl = 0.0
    sl_pct = 0.0
    sl_price = 0.0
    tp_pct = 0.0
    tp_price = 0.0

    # record vars
    strat_records = None
    strat_records_filled = None

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
        symbol_price_data: np.array,
        strat_records: np.array,
    ):
        self.order_settings = order_settings
        self.account_state = account_state
        self.exchange_settings = exchange_settings
        self.symbol_price_data = symbol_price_data
        self.equity = account_state.equity
        self.available_balance = account_state.equity
        self.strat_records = strat_records
        self.strat_records_filled = 0

        if self.order_settings.tp_fee_type == TakeProfitFeeType.Nothing:
            self.tp_fee_pct = 0.0
        elif self.order_settings.tp_fee_type == TakeProfitFeeType.Limit:
            self.tp_fee_pct = self.exchange_settings.limit_fee_pct
        elif self.order_settings.tp_fee_type == TakeProfitFeeType.Market:
            self.tp_fee_pct = self.exchange_settings.market_fee_pct

        if self.order_settings.order_type == OrderType.Long:
            self.obj_stop_loss = StopLossLong(
                sl_based_on_add_pct=self.order_settings.sl_based_on_add_pct,
                sl_based_on_lookback=self.order_settings.sl_based_on_lookback,
                sl_candle_body_type=self.order_settings.sl_candle_body_type,
                sl_to_be_based_on_candle_body_type=self.order_settings.sl_to_be_based_on_candle_body_type,
                sl_to_be_when_pct_from_candle_body=self.order_settings.sl_to_be_when_pct_from_candle_body,
                sl_to_be_zero_or_entry_type=self.order_settings.sl_to_be_zero_or_entry_type,
                sl_type=self.order_settings.stop_loss_type,
                trail_sl_based_on_candle_body_type=self.order_settings.trail_sl_based_on_candle_body_type,
                trail_sl_by_pct=self.order_settings.trail_sl_by_pct,
                trail_sl_when_pct_from_candle_body=self.order_settings.trail_sl_when_pct_from_candle_body,
                market_fee_pct=self.exchange_settings.market_fee_pct,
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
                tp_fee_pct=self.tp_fee_pct,
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

    def decrease_position(self, **vargs):
        pass

    def move_stop_loss(
        self,
        sl_price: float,
        order_status: int,
        bar_index: int,
        indicator_settings_index: int,
        order_settings_index: int,
        symbol_index: int,
        order_records: np.array,
        order_records_filled: np.array,
    ):
        self.sl_price = sl_price
        self.sl_pct = (self.average_entry - sl_price) / self.average_entry
        self.order_status = order_status
        self.fill_order_records(
            bar_index=bar_index,
            order_settings_index=order_settings_index,
            indicator_settings_index=indicator_settings_index,
            symbol_index=symbol_index,
            order_records=order_records,
            order_records_filled=order_records_filled,
        )

    def fill_order_records(
        self,
        bar_index: int,
        indicator_settings_index: int,
        order_settings_index: int,
        symbol_index: int,
        order_records_filled: np.array,
        order_records: np.array,
    ):
        order_records["symbol_idx"] = symbol_index
        order_records["ind_set_idx"] = indicator_settings_index
        order_records["or_set_idx"] = order_settings_index
        order_records["bar_idx"] = bar_index

        order_records["equity"] = self.equity
        order_records["available_balance"] = self.available_balance
        order_records["cash_borrowed"] = self.cash_borrowed
        order_records["cash_used"] = self.cash_used

        order_records["average_entry"] = self.average_entry
        order_records["fees_paid"] = self.fees_paid
        order_records["leverage"] = self.leverage
        order_records["liq_price"] = self.liq_price
        order_records["order_status"] = self.order_status
        order_records["possible_loss"] = self.possible_loss
        order_records["entry_size"] = self.entry_size
        order_records["entry_price"] = self.entry_price
        order_records["exit_price"] = self.exit_price
        order_records["position_size"] = self.position_size
        order_records["realized_pnl"] = self.realized_pnl
        order_records["sl_pct"] = self.sl_pct * 100
        order_records["sl_price"] = self.sl_price
        order_records["tp_pct"] = self.tp_pct * 100
        order_records["tp_price"] = self.tp_price

        order_records_filled[0] += 1

    def fill_rejected_order_record(self, **vargs):
        pass
    def fill_strat_records_nb(self, **vargs):
        pass


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
            account_state_equity=self.equity,
            average_entry=self.average_entry,
            entry_price=entry_price,
            in_position=self.position_size > 0,
            position_size=self.position_size,
            possible_loss=self.possible_loss,
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
            available_balance=self.available_balance,
            cash_used=self.cash_used,
            cash_borrowed=self.cash_borrowed,
            entry_size=self.entry_size,
        )

    def calculate_take_profit(self):
        (
            self.tp_price,
            self.tp_pct,
            self.order_status,
        ) = self.obj_take_profit.take_profit_calculator(
            possible_loss=self.possible_loss,
            position_size=self.position_size,
            average_entry=self.average_entry,
        )

    def check_stop_loss_hit(self, current_candle):
        self.obj_stop_loss.sl_hit_checker(
            sl_hit=current_candle[2] < self.sl_price,
            exit_fee_pct=self.exchange_settings.market_fee_pct,
        )

    def check_liq_hit(self, current_candle):
        self.obj_leverage.liq_hit_checker(
            liq_hit=current_candle[2] < self.liq_price,
            exit_fee_pct=self.exchange_settings.market_fee_pct,
        )

    def check_take_profit_hit(self, current_candle, exit_signal):
        self.obj_take_profit.tp_checker(
            current_candle=current_candle,
            tp_hit=current_candle[1] > self.tp_price,
            exit_signal=exit_signal,
            exit_fee_pct=self.tp_fee_pct,
        )

    def check_move_stop_loss_to_be(self, bar_index, symbol_price_data):
        self.obj_stop_loss.move_sl_to_be_checker(
            average_entry=self.average_entry,
            bar_index=bar_index,
            symbol_price_data=symbol_price_data,
        )

    def check_move_trailing_stop_loss(self, bar_index, symbol_price_data):
        self.obj_stop_loss.move_tsl_checker(
            average_entry=self.average_entry,
            bar_index=bar_index,
            symbol_price_data=symbol_price_data,
        )

    def decrease_position(
        self,
        order_status: OrderStatus,
        exit_price: float,
        exit_fee_pct: float,
        bar_index: int,
        indicator_settings_index: int,
        order_settings_index: int,
        symbol_index: int,
        order_records: np.array,
        order_records_filled: np.array,
    ):
        # profit and loss calulation
        coin_size = self.position_size / self.average_entry  # math checked
        pnl = coin_size * (exit_price - self.average_entry)  # math checked
        fee_open = (
            coin_size * self.average_entry * self.exchange_settings.market_fee_pct
        )  # math checked
        fee_close = coin_size * exit_price * exit_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.realized_pnl = pnl - self.fees_paid  # math checked

        # Setting new equity
        self.equity += self.realized_pnl

        self.available_balance = self.equity
        self.cash_borrowed = 0.0
        self.cash_used = 0.0
        self.average_entry = 0.0
        self.leverage = 0.0
        self.liq_price = 0.0
        self.order_status = order_status
        self.possible_loss = 0.0
        self.entry_size = 0.0
        self.entry_price = 0.0
        self.exit_price = exit_price
        self.position_size = 0.0
        self.sl_pct = 0.0
        self.sl_price = 0.0
        self.tp_pct = 0.0
        self.tp_price = 0.0

        self.strat_records[self.strat_records_filled]["equity"] = self.equity
        self.strat_records[self.strat_records_filled]["bar_idx"] = bar_index
        self.strat_records[self.strat_records_filled][
            "or_set_idx"
        ] = order_settings_index
        self.strat_records[self.strat_records_filled][
            "ind_set_idx"
        ] = indicator_settings_index
        self.strat_records[self.strat_records_filled]["symbol_idx"] = symbol_index
        self.strat_records[self.strat_records_filled]["real_pnl"] = round(
            self.realized_pnl, 4
        )

        self.strat_records_filled += 1
        self.fill_order_records(
            bar_index=bar_index,
            order_settings_index=order_settings_index,
            indicator_settings_index=indicator_settings_index,
            symbol_index=symbol_index,
            order_records=order_records,
            order_records_filled=order_records_filled,
        )
        self.fees_paid = 0.0
        self.realized_pnl = 0.0
        self.exit_price = 0.0
