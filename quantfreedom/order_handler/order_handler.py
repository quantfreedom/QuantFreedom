from typing import Optional
import numpy as np
from quantfreedom.custom_logger import CustomLogger
from quantfreedom.enums import (
    OrderStatus,
    LongOrShortType,
    OrderSettings,
    ExchangeSettings,
    OrderResult,
    TakeProfitFeeType,
    CandleBodyType,
    IncreasePositionType,
    LeverageStrategyType,
    LongOrShortType,
    OrderSettings,
    SLToBeZeroOrEntryType,
    StopLossStrategyType,
    TakeProfitFeeType,
    TakeProfitStrategyType,
)

from quantfreedom.order_handler.increase_position import IncreasePositionLong
from quantfreedom.order_handler.leverage import LeverageLong
from quantfreedom.order_handler.stop_loss import StopLossLong
from quantfreedom.order_handler.take_profit import TakeProfitLong
import logging

info_logger = logging.getLogger("info")


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
    entry_size_asset = 0.0
    entry_size_usd = 0.0
    exit_price = 0.0
    fees_paid = 0.0
    leverage = 1.0
    liq_price = 0.0
    order_status = 0.0
    position_size_asset = 0.0
    position_size_usd = 0.0
    possible_loss = 0.0
    realized_pnl = 0.0
    sl_pct = 0.0
    sl_price = 0.0
    total_trades = 0
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
        order_settings = order_settings
        exchange_settings = exchange_settings
        self.equity = equity
        self.available_balance = equity
        self.market_fee_pct = exchange_settings.market_fee_pct

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

        if order_settings.tp_fee_type == TakeProfitFeeType.Nothing:
            self.tp_fee_pct = 0.0
        elif order_settings.tp_fee_type == TakeProfitFeeType.Limit:
            self.tp_fee_pct = exchange_settings.limit_fee_pct
        elif order_settings.tp_fee_type == TakeProfitFeeType.Market:
            self.tp_fee_pct = exchange_settings.market_fee_pct

        if order_settings.long_or_short == LongOrShortType.Long:
            self.obj_stop_loss = StopLossLong(
                sl_based_on_add_pct=order_settings.sl_based_on_add_pct,
                sl_based_on_lookback=order_settings.sl_based_on_lookback,
                sl_candle_body_type=order_settings.sl_candle_body_type,
                sl_to_be_based_on_candle_body_type=order_settings.sl_to_be_based_on_candle_body_type,
                sl_to_be_when_pct_from_candle_body=order_settings.sl_to_be_when_pct_from_candle_body,
                sl_to_be_zero_or_entry_type=order_settings.sl_to_be_zero_or_entry_type,
                sl_type=order_settings.stop_loss_type,
                trail_sl_based_on_candle_body_type=order_settings.trail_sl_based_on_candle_body_type,
                trail_sl_by_pct=order_settings.trail_sl_by_pct,
                trail_sl_when_pct_from_candle_body=order_settings.trail_sl_when_pct_from_candle_body,
                market_fee_pct=exchange_settings.market_fee_pct,
                price_tick_step=exchange_settings.price_tick_step,
            )
            self.obj_increase_posotion = IncreasePositionLong(
                increase_position_type=order_settings.increase_position_type,
                stop_loss_type=order_settings.stop_loss_type,
                market_fee_pct=exchange_settings.market_fee_pct,
                max_equity_risk_pct=order_settings.max_equity_risk_pct,
                risk_account_pct_size=order_settings.risk_account_pct_size,
                max_asset_size=exchange_settings.max_asset_size,
                min_asset_size=exchange_settings.min_asset_size,
                entry_size_asset=order_settings.entry_size_asset,
                max_trades=order_settings.max_trades,
                price_tick_step=exchange_settings.price_tick_step,
                asset_tick_step=exchange_settings.asset_tick_step,
            )
            self.obj_leverage = LeverageLong(
                leverage_type=order_settings.leverage_type,
                sl_type=order_settings.stop_loss_type,
                market_fee_pct=exchange_settings.market_fee_pct,
                max_leverage=exchange_settings.max_leverage,
                static_leverage=order_settings.static_leverage,
                mmr_pct=exchange_settings.mmr_pct,
                price_tick_step=exchange_settings.price_tick_step,
                leverage_tick_step=exchange_settings.leverage_tick_step,
            )
            self.obj_take_profit = TakeProfitLong(
                take_profit_type=order_settings.take_profit_type,
                risk_reward=order_settings.risk_reward,
                tp_fee_pct=self.tp_fee_pct,
                price_tick_step=exchange_settings.price_tick_step,
                market_fee_pct=exchange_settings.market_fee_pct,
            )
        elif order_settings.long_or_short == LongOrShortType.Short:
            pass

        info_logger.info(
            f"\nOrder Settings:\n\
long_or_short = {LongOrShortType._fields[order_settings.long_or_short]}\n\
increase_position_type = {IncreasePositionType._fields[order_settings.increase_position_type]}\n\
risk_account_pct_size = {round(order_settings.risk_account_pct_size*100,2)}\n\
max_equity_risk_pct = {round(order_settings.max_equity_risk_pct*100,2)}\n\
stop_loss_type = {StopLossStrategyType._fields[order_settings.stop_loss_type]}\n\
sl_candle_body_type = {CandleBodyType._fields[order_settings.sl_candle_body_type]}\n\
sl_based_on_add_pct = {round(order_settings.sl_based_on_add_pct*100,2)}\n\
sl_based_on_lookback = {order_settings.sl_based_on_lookback}\n\
sl_to_be_based_on_candle_body_type = {CandleBodyType._fields[order_settings.sl_to_be_based_on_candle_body_type]}\n\
sl_to_be_when_pct_from_candle_body = {order_settings.sl_to_be_when_pct_from_candle_body}\n\
sl_to_be_zero_or_entry_type = {SLToBeZeroOrEntryType._fields[order_settings.sl_to_be_zero_or_entry_type]}\n\
trail_sl_based_on_candle_body_type = {CandleBodyType._fields[order_settings.trail_sl_based_on_candle_body_type]}\n\
trail_sl_when_pct_from_candle_body = {round(order_settings.trail_sl_when_pct_from_candle_body*100,2)}\n\
trail_sl_by_pct = {round(order_settings.trail_sl_by_pct*100,2)}\n\
take_profit_type = {TakeProfitStrategyType._fields[order_settings.take_profit_type]}\n\
risk_reward = {order_settings.risk_reward}\n\
tp_fee_type = {TakeProfitFeeType._fields[order_settings.tp_fee_type]}\n\
leverage_type = {LeverageStrategyType._fields[order_settings.leverage_type]}\n\
static_leverage = {order_settings.static_leverage}\n\
num_candles = {order_settings.num_candles}\n\
entry_size_asset = {order_settings.entry_size_asset}\n\
max_trades = {order_settings.max_trades}"
        )

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

    def calculate_leverage(self, **vargs):
        pass

    def calculate_take_profit(self, **vargs):
        pass

    def move_stop_loss(self, **vargs):
        pass

    def update_stop_loss_live_trading(self, **vargs):
        pass

    def fill_order_records(
        self,
        order_result: OrderResult,
    ):
        self.order_records[self.total_order_records_filled]["ind_set_idx"] = order_result.indicator_settings_index
        self.order_records[self.total_order_records_filled]["or_set_idx"] = order_result.order_settings_index
        self.order_records[self.total_order_records_filled]["bar_idx"] = order_result.bar_index
        self.order_records[self.total_order_records_filled]["timestamp"] = order_result.timestamp

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
        self.order_records[self.total_order_records_filled]["total_trades"] = order_result.total_trades
        self.order_records[self.total_order_records_filled]["entry_size_asset"] = order_result.entry_size_asset
        self.order_records[self.total_order_records_filled]["entry_size_usd"] = order_result.entry_size_usd
        self.order_records[self.total_order_records_filled]["entry_price"] = order_result.entry_price
        self.order_records[self.total_order_records_filled]["exit_price"] = order_result.exit_price
        self.order_records[self.total_order_records_filled]["position_size_asset"] = order_result.position_size_asset
        self.order_records[self.total_order_records_filled]["position_size_usd"] = order_result.position_size_usd
        self.order_records[self.total_order_records_filled]["realized_pnl"] = order_result.realized_pnl
        self.order_records[self.total_order_records_filled]["sl_pct"] = order_result.sl_pct * 100
        self.order_records[self.total_order_records_filled]["sl_price"] = order_result.sl_price
        self.order_records[self.total_order_records_filled]["tp_pct"] = order_result.tp_pct * 100
        self.order_records[self.total_order_records_filled]["tp_price"] = order_result.tp_price
        self.total_order_records_filled += 1
        info_logger.debug(f"Filled or and total or={self.total_order_records_filled}")

    def fill_strat_records(self, bar_index, order_settings_index, indicator_settings_index):
        self.strat_records[self.strat_records_filled]["bar_idx"] = bar_index
        self.strat_records[self.strat_records_filled]["or_set_idx"] = order_settings_index
        self.strat_records[self.strat_records_filled]["ind_set_idx"] = indicator_settings_index
        self.strat_records[self.strat_records_filled]["equity"] = self.equity
        self.strat_records[self.strat_records_filled]["real_pnl"] = round(self.realized_pnl, 4)

        self.strat_records_filled += 1
        info_logger.debug(f"Filled strat rec and total strat rec={self.strat_records_filled}")


class LongOrder(Order):
    def calculate_stop_loss(self, bar_index, candles):
        self.sl_price = self.obj_stop_loss.calculator(
            bar_index=bar_index,
            candles=candles,
        )
        info_logger.info(f"Sl_price={self.sl_price}")

    def calculate_increase_posotion(self, entry_price):
        (
            self.average_entry,
            self.entry_price,
            self.entry_size_asset,
            self.entry_size_usd,
            self.position_size_asset,
            self.position_size_usd,
            self.possible_loss,
            self.total_trades,
            self.sl_pct,
        ) = self.obj_increase_posotion.calculate_increase_posotion(
            account_state_equity=self.equity,
            average_entry=self.average_entry,
            entry_price=entry_price,
            in_position=self.position_size_usd > 0,
            position_size_asset=self.position_size_asset,
            position_size_usd=self.position_size_usd,
            possible_loss=self.possible_loss,
            sl_price=self.sl_price,
            total_trades=self.total_trades,
        )
        info_logger.info(
            f"\n\
average_entry={self.average_entry:,}\n\
entry_price={self.entry_price:,}\n\
entry_size_asset={self.entry_size_asset:,}\n\
entry_size_usd={self.entry_size_usd:,}\n\
position_size_asset={self.position_size_asset:,}\n\
position_size_usd={self.position_size_usd:,}\n\
possible_loss={self.possible_loss:,}\n\
total_trades={self.total_trades:,}\n\
sl_pct={round(self.sl_pct*100,2):,}"
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
        info_logger.info(
            f"\n\
leverage={self.leverage}\n\
liq_price={self.liq_price:,}\n\
available_balance={self.available_balance:,}\n\
cash_used={self.cash_used:,}\n\
cash_borrowed={self.cash_borrowed:,}\n\
can_move_sl_to_be= {self.can_move_sl_to_be}"
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
        info_logger.info(f"tp_price={self.tp_price:,} tp_pct={round(self.tp_pct*100,2)}")

    def check_stop_loss_hit(self, current_candle):
        self.obj_stop_loss.sl_hit_checker(
            sl_hit=current_candle["low"] < self.sl_price,
            exit_fee_pct=self.market_fee_pct,
        )

    def check_liq_hit(self, current_candle):
        self.obj_leverage.liq_hit_checker(
            liq_hit=current_candle["low"] < self.liq_price,
            exit_fee_pct=self.market_fee_pct,
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

    def move_stop_loss(
        self,
        sl_price: float,
        order_status: int,
        bar_index: int,
        timestamp: int,
        indicator_settings_index: int,
        order_settings_index: int,
    ) -> None:
        self.sl_price = sl_price
        self.sl_pct = round((self.average_entry - sl_price) / self.average_entry, 4)
        self.order_status = order_status
        self.can_move_sl_to_be = False

        self.or_filler(
            order_result=OrderResult(
                indicator_settings_index=indicator_settings_index,
                order_settings_index=order_settings_index,
                bar_index=bar_index,
                timestamp=timestamp,
                order_status=self.order_status,
                sl_price=self.sl_price,
            ),
        )
        info_logger.debug(f"Filled order result")

    def update_stop_loss_live_trading(
        self,
        sl_price: float,
    ):
        self.sl_price = sl_price
        self.sl_pct = round((self.average_entry - sl_price) / self.average_entry, 4)
        self.can_move_sl_to_be = False

    def decrease_position(
        self,
        order_status: OrderStatus,
        exit_price: float,
        exit_fee_pct: float,
        bar_index: int,
        timestamp: int,
        indicator_settings_index: int,
        order_settings_index: int,
    ):
        self.exit_price = exit_price
        self.order_status = order_status
        # profit and loss calulation
        coin_size = self.position_size_usd / self.average_entry  # math checked
        pnl = coin_size * (self.exit_price - self.average_entry)  # math checked
        fee_open = coin_size * self.average_entry * self.market_fee_pct  # math checked
        fee_close = coin_size * self.exit_price * exit_fee_pct  # math checked
        self.fees_paid = fee_open + fee_close  # math checked
        self.realized_pnl = round(pnl - self.fees_paid, 4)  # math checked

        # Setting new equity
        self.equity = round(self.realized_pnl + self.equity, 4)
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
                timestamp=timestamp,
                bar_index=bar_index,
                equity=self.equity,
                available_balance=self.available_balance,
                fees_paid=self.fees_paid,
                order_status=self.order_status,
                exit_price=self.exit_price,
                realized_pnl=self.realized_pnl,
            )
        )
        info_logger.info(
            f"\n\
realized_pnl={self.realized_pnl}\n\
order_status= {OrderStatus._fields[self.order_status]}\n\
available_balance={self.available_balance}\n\
equity={self.equity}"
        )
        self.cash_borrowed = 0.0
        self.cash_used = 0.0
        self.average_entry = 0.0
        self.leverage = 0.0
        self.liq_price = 0.0
        self.possible_loss = 0.0
        self.total_trades = 0
        self.entry_size_asset = 0.0
        self.entry_size_usd = 0.0
        self.entry_price = 0.0
        self.position_size_asset = 0.0
        self.position_size_usd = 0.0
        self.sl_pct = 0.0
        self.sl_price = 0.0
        self.tp_pct = 0.0
        self.tp_price = 0.0
        self.fees_paid = 0.0
        self.realized_pnl = 0.0
        self.exit_price = 0.0
