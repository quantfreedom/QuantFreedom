from decimal import Decimal
from typing import Optional
import numpy as np
from quantfreedom.enums import (
    DecreasePosition,
    OrderStatus,
    LongOrShortType,
    OrderSettings,
    ExchangeSettings,
    OrderResult,
    TakeProfitFeeType,
)
from quantfreedom.order_handler.increase_position import IncreasePositionLong
from quantfreedom.order_handler.leverage import LeverageLong
from quantfreedom.order_handler.stop_loss import StopLossLong
from quantfreedom.order_handler.take_profit import TakeProfitLong


class Order:
    obj_stop_loss = None
    obj_leverage = None
    obj_increase_posotion = None
    obj_take_profit = None
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
    entry_size_usd = 0.0
    exit_price = 0.0
    fees_paid = 0.0
    leverage = 1.0
    liq_price = 0.0
    order_status = 0.0
    position_size_usd = 0.0
    possible_loss = 0.0
    realized_pnl = 0.0
    sl_pct = 0.0
    sl_price = 0.0
    tp_pct = 0.0
    tp_price = 0.0
    can_move_sl_to_be = False

    # record vars
    strat_records = None
    strat_records_filled = None

    def instantiate(long_or_short: LongOrShortType, **vargs):  # TODO: we should only have to do this once not everytime
        if long_or_short == LongOrShortType.Long:
            return LongOrder(**vargs)

    def __init__(
        self,
        equity: float,
        order_settings: OrderSettings,
        exchange_settings: ExchangeSettings,
        strat_records: Optional[np.array] = None,
        order_records: Optional[np.array] = None,
        total_order_records_filled: Optional[int] = None,
    ):
        self.order_settings = order_settings
        self.exchange_settings = exchange_settings
        self.equity = equity
        self.available_balance = equity

        # this is not effecient ... this will not change
        if strat_records is None:
            self.strat_filler = self.pass_func
        else:
            self.strat_filler = self.fill_strat_records
            self.strat_records = strat_records
            self.strat_records_filled = 0

        # this is not effecient ... this will not change
        if order_records is None:
            self.or_filler = self.pass_func
        else:
            self.or_filler = self.fill_order_records
            self.order_records = order_records
            self.total_order_records_filled = total_order_records_filled

        if self.order_settings.tp_fee_type == TakeProfitFeeType.Nothing:
            self.tp_fee_pct = 0.0
        elif self.order_settings.tp_fee_type == TakeProfitFeeType.Limit:
            self.tp_fee_pct = self.exchange_settings.limit_fee_pct
        elif self.order_settings.tp_fee_type == TakeProfitFeeType.Market:
            self.tp_fee_pct = self.exchange_settings.market_fee_pct

        if self.order_settings.long_or_short == LongOrShortType.Long:
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
                max_asset_size=self.exchange_settings.max_asset_size,
                min_asset_size=self.exchange_settings.min_asset_size,
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
        elif self.order_settings.long_or_short == LongOrShortType.Short:
            pass

    def pass_func(self, **vargs):
        pass

    def calculate_stop_loss(self, **vargs):
        pass

    def calculate_increase_posotion(self, **vargs):
        pass

    def check_move_stop_loss_to_be(self, **vargs):
        pass

    def check_move_trailing_stop_loss(self, **vargs):
        pass

    def calculate_leverage(self):
        pass

    def calculate_take_profit(self):
        pass

    def round_size_by_tick_step(self, user_num: float, exchange_num: float) -> float:
        user_num = str(user_num)
        exchange_num = str(exchange_num)
        int_num = int(Decimal(user_num) / Decimal(exchange_num))
        float_num = float(Decimal(int_num) * Decimal(exchange_num))
        return float_num

    def move_stop_loss(
        self,
        sl_price: float,
        order_status: int,
        bar_index: int,
        indicator_settings_index: int,
        order_settings_index: int,
    ) -> None:
        self.sl_price = sl_price
        self.sl_pct = (self.average_entry - sl_price) / self.average_entry
        self.order_status = order_status
        self.can_move_sl_to_be = False

        self.or_filler(
            order_result=OrderResult(
                indicator_settings_index=indicator_settings_index,
                order_settings_index=order_settings_index,
                bar_index=bar_index,
                order_status=self.order_status,
                sl_price=self.sl_price,
            ),
        )

    def update_stop_loss_live_trading(
        self,
        sl_price: float,
    ):
        self.sl_price = sl_price
        self.sl_pct = (self.average_entry - sl_price) / self.average_entry
        self.can_move_sl_to_be = False

    def fill_order_records(
        self,
        order_result: OrderResult,
    ):
        self.order_records[self.total_order_records_filled]["ind_set_idx"] = order_result.indicator_settings_index
        self.order_records[self.total_order_records_filled]["or_set_idx"] = order_result.order_settings_index
        self.order_records[self.total_order_records_filled]["bar_idx"] = order_result.bar_index

        self.order_records[self.total_order_records_filled]["equity"] = order_result.equity
        self.order_records[self.total_order_records_filled]["available_balance"] = order_result.available_balance
        self.order_records[self.total_order_records_filled]["cash_borrowed"] = order_result.cash_borrowed
        self.order_records[self.total_order_records_filled]["cash_used"] = order_result.cash_used

        self.order_records[self.total_order_records_filled]["average_entry"] = order_result.average_entry
        self.order_records[self.total_order_records_filled]["fees_paid"] = order_result.fees_paid
        self.order_records[self.total_order_records_filled]["leverage"] = order_result.leverage
        self.order_records[self.total_order_records_filled]["liq_price"] = order_result.liq_price
        self.order_records[self.total_order_records_filled]["order_status"] = order_result.order_status
        self.order_records[self.total_order_records_filled]["possible_loss"] = order_result.possible_loss
        self.order_records[self.total_order_records_filled]["entry_size_usd"] = order_result.entry_size_usd
        self.order_records[self.total_order_records_filled]["entry_price"] = order_result.entry_price
        self.order_records[self.total_order_records_filled]["exit_price"] = order_result.exit_price
        self.order_records[self.total_order_records_filled]["position_size_usd"] = order_result.position_size_usd
        self.order_records[self.total_order_records_filled]["realized_pnl"] = order_result.realized_pnl
        self.order_records[self.total_order_records_filled]["sl_pct"] = order_result.sl_pct * 100
        self.order_records[self.total_order_records_filled]["sl_price"] = order_result.sl_price
        self.order_records[self.total_order_records_filled]["tp_pct"] = order_result.tp_pct * 100
        self.order_records[self.total_order_records_filled]["tp_price"] = order_result.tp_price

        self.total_order_records_filled += 1

    def fill_strat_records(self, bar_index, order_settings_index, indicator_settings_index):
        self.strat_records[self.strat_records_filled]["bar_idx"] = bar_index
        self.strat_records[self.strat_records_filled]["or_set_idx"] = order_settings_index
        self.strat_records[self.strat_records_filled]["ind_set_idx"] = indicator_settings_index
        self.strat_records[self.strat_records_filled]["equity"] = self.equity
        self.strat_records[self.strat_records_filled]["real_pnl"] = round(self.realized_pnl, 4)

        self.strat_records_filled += 1


class LongOrder(Order):
    def calculate_stop_loss(self, bar_index, candles):
        self.sl_price = self.obj_stop_loss.calculator(
            bar_index=bar_index,
            candles=candles,
        )

    def calculate_increase_posotion(self, entry_price):
        (
            self.average_entry,
            self.entry_price,
            self.entry_size_usd,
            self.position_size_usd,
            self.possible_loss,
            self.sl_pct,
        ) = self.obj_increase_posotion.calculate_increase_posotion(
            account_state_equity=self.equity,
            average_entry=self.average_entry,
            entry_price=entry_price,
            in_position=self.position_size_usd > 0,
            position_size_usd=self.position_size_usd,
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
            self.can_move_sl_to_be,
        ) = self.obj_leverage.leverage_calculator(
            average_entry=self.average_entry,
            sl_price=self.sl_price,
            available_balance=self.available_balance,
            cash_used=self.cash_used,
            cash_borrowed=self.cash_borrowed,
            entry_size_usd=self.entry_size_usd,
        )

    def calculate_take_profit(self):
        (
            self.tp_price,
            self.tp_pct,
            self.order_status,
        ) = self.obj_take_profit.take_profit_calculator(
            possible_loss=self.possible_loss,
            position_size_usd=self.position_size_usd,
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
            exit_signal=exit_signal,
            exit_fee_pct=self.tp_fee_pct,
        )

    def check_move_stop_loss_to_be(self, bar_index, candles):
        self.obj_stop_loss.move_sl_to_be_checker(
            average_entry=self.average_entry,
            bar_index=bar_index,
            candles=candles,
            can_move_sl_to_be=self.can_move_sl_to_be,
        )

    def check_move_trailing_stop_loss(self, bar_index, candles):
        self.obj_stop_loss.move_tsl_checker(
            average_entry=self.average_entry,
            bar_index=bar_index,
            candles=candles,
        )

    def decrease_position(
        self,
        order_status: OrderStatus,
        exit_price: float,
        exit_fee_pct: float,
        bar_index: int,
        indicator_settings_index: int,
        order_settings_index: int,
    ):
        self.exit_price = exit_price
        self.order_status = order_status
        # profit and loss calulation
        coin_size = self.position_size_usd / self.average_entry  # math checked
        pnl = coin_size * (self.exit_price - self.average_entry)  # math checked
        fee_open = coin_size * self.average_entry * self.exchange_settings.market_fee_pct  # math checked
        fee_close = coin_size * self.exit_price * exit_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.realized_pnl = pnl - self.fees_paid  # math checked

        # Setting new equity
        self.equity += self.realized_pnl
        self.available_balance = self.equity

        self.strat_filler(
            bar_index=bar_index,
            order_settings_index=order_settings_index,
            indicator_settings_index=indicator_settings_index,
        )

        self.or_filler(
            order_result=OrderResult(
                indicator_settings_index=indicator_settings_index,
                order_settings_index=order_settings_index,
                bar_index=bar_index,
                equity=self.equity,
                available_balance=self.available_balance,
                fees_paid=self.fees_paid,
                order_status=self.order_status,
                exit_price=self.exit_price,
                realized_pnl=self.realized_pnl,
            )
        )

        self.cash_borrowed = 0.0
        self.cash_used = 0.0
        self.average_entry = 0.0
        self.leverage = 0.0
        self.liq_price = 0.0
        self.possible_loss = 0.0
        self.entry_size_usd = 0.0
        self.entry_price = 0.0
        self.position_size_usd = 0.0
        self.sl_pct = 0.0
        self.sl_price = 0.0
        self.tp_pct = 0.0
        self.tp_price = 0.0
        self.fees_paid = 0.0
        self.realized_pnl = 0.0
        self.exit_price = 0.0
