import numpy as np

from quantfreedom.poly.enums import (
    AccountState,
    OrderSettings,
    ExchangeSettings,
    OrderType,
    OrderResult,
    OrderStatus,
)
from quantfreedom.poly.stop_loss import StopLossCalculator, StopLossType, CandleBody
from quantfreedom.poly.leverage import Leverage, LeverageType
from quantfreedom.poly.entry_size import EntrySize, EntrySizeType
from quantfreedom.poly.take_profit import TakeProfit, TakeProfitType


class Order:
    obj_stop_loss = None
    obj_leverage = None
    obj_entry_size = None
    obj_take_profit = None
    account_state = None
    price_data = None
    exchange_settings = None

    leverage = None
    liq_price = None
    take_profit = None
    entry_size = None
    entry_price = None
    possible_loss = None
    sl_price = None
    sl_pct = None
    average_entry = None
    position_size = None
    account_state_available_balance = None
    account_state_cash_used = None
    account_state_cash_borrowed = None
    take_profit_price = None
    take_profit_pct = None

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
        order_result: OrderResult,
    ):
        self.account_state = account_state
        self.exchange_settings = exchange_settings
        self.order_settings = order_settings
        self.order_result = order_result

        self.obj_stop_loss = StopLossCalculator(
            sl_type=sl_type,
            candle_body=candle_body,
            order_settings=order_settings,
        )
        self.obj_leverage = Leverage(
            leverage_type=leverage_type,
            max_leverage=exchange_settings.max_lev,
        )
        self.obj_entry_size = EntrySize(
            entry_size_type=entry_size_type,
            order_settings=order_settings,
            exchange_settings=exchange_settings,
        )
        self.obj_take_profit = TakeProfit(tp_type)

    def calc_stop_loss(self):
        pass

    def calc_leverage(self):
        pass

    def calc_entry_size(self):
        pass

    def calc_take_profit(self):
        pass

    def fill_order_result_entry(self):
        self.account_state = AccountState(
            available_balance=self.account_state_available_balance,
            cash_borrowed=self.account_state_cash_borrowed,
            cash_used=self.account_state_cash_used,
            equity=self.account_state.equity,
        )
        self.order_result = OrderResult(
            average_entry=self.average_entry,
            fees_paid=np.nan,
            leverage=self.leverage,
            liq_price=self.liq_price,
            order_status=OrderStatus.Filled,
            possible_loss=self.possible_loss,
            pct_chg_trade=np.nan,
            entry_size=self.entry_size,
            entry_price=self.entry_price,
            position_size=self.position_size,
            realized_pnl=np.nan,
            sl_pct=self.sl_pct,
            sl_price=self.sl_price,
            tp_pct=self.take_profit_pct,
            tp_price=self.take_profit_price,
        )

    def fill_ignored_order_result_entry(self, order_status: OrderStatus):
        # self.account_state = AccountState(
        #     available_balance=self.account_state.available_balance,
        #     cash_borrowed=self.account_state.cash_borrowed,
        #     cash_used=self.account_state.cash_used,
        #     equity=self.account_state.equity,
        # )
        # self.order_result = OrderResult(
        #     average_entry=self.order_result.average_entry,
        #     fees_paid=self.order_result.fees_paid,
        #     leverage=self.order_result.leverage,
        #     liq_price=self.order_result.liq_price,
        #     order_status=order_status,
        #     possible_loss=self.order_result.possible_loss,
        #     pct_chg_trade=self.order_result.pct_chg_trade,
        #     entry_size=self.order_result.entry_size,
        #     entry_price=self.order_result.entry_price,
        #     position_size=self.order_result.position_size,
        #     realized_pnl=self.order_result.realized_pnl,
        #     sl_pct=self.order_result.sl_pct,
        #     sl_price=self.order_result.sl_price,
        #     tp_pct=self.order_result.tp_pct,
        #     tp_price=self.order_result.tp_price,
        # )
        self.order_result.order_status = order_status

class LongOrder(Order):
    def calc_stop_loss(self, **vargs):
        self.sl_price = self.obj_stop_loss.sl_calculator(
            symbol_price_data=vargs["symbol_price_data"],
            bar_index=vargs["bar_index"],
        )
        return self.sl_price

    def calc_entry_size(self, **vargs):
        print("LongOrder::entry")
        (
            self.entry_size,
            self.position_size,
            self.entry_price,
            self.average_entry,
            self.possible_loss,
            self.sl_pct,
        ) = self.obj_entry_size.calculate(
            account_state_equity=self.account_state.equity,
            sl_price=self.sl_price,
            in_position=self.order_result.position_size > 0,
            possible_loss=self.order_result.possible_loss,
            average_entry=self.order_result.average_entry,
            position_size=self.order_result.position_size,
            entry_price=vargs["entry_price"],
        )
        return self.entry_size, self.average_entry, self.possible_loss

    def calc_leverage(self, **vargs):
        print("LongOrder::leverage")
        (
            self.leverage,
            self.liq_price,
            self.account_state_available_balance,
            self.account_state_cash_used,
            self.account_state_cash_borrowed,
        ) = self.obj_leverage.calculate(
            average_entry=self.average_entry,
            sl_price=self.sl_price,
            market_fee_pct=self.exchange_settings.market_fee_pct,
            entry_size=self.entry_size,
            leverage=self.leverage,
            account_state_available_balance=self.account_state.available_balance,
            account_state_cash_used=self.account_state.cash_used,
            account_state_cash_borrowed=self.account_state.cash_borrowed,
            exchange_settings_mmr_pct=self.exchange_settings.mmr_pct,
        )

    def calc_take_profit(self):
        print("LongOrder::take_profit")
        self.take_profit_price, self.take_profit_pct = self.obj_take_profit.calculate(
            possible_loss=self.possible_loss,
            risk_reward=self.order_settings.risk_reward,
            position_size=self.position_size,
            limit_fee_pct=self.exchange_settings.limit_fee_pct,
            average_entry=self.average_entry,
        )
