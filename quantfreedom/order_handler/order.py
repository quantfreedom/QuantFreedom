from logging import getLogger
import numpy as np
from quantfreedom.enums import (
    OrderStatus,
    DynamicOrderSettings,
    ExchangeSettings,
    StaticOrderSettings,
)
from quantfreedom.order_handler.increase_position import IncreasePosition
from quantfreedom.order_handler.leverage import Leverage
from quantfreedom.order_handler.stop_loss import StopLoss
from quantfreedom.order_handler.take_profit import TakeProfit


logger = getLogger("info")


class OrderHandler:
    cach_borrowed = 0

    def __init__(
        self,
        exchange_settings_tuple: ExchangeSettings,
        long_short: str,
        static_os_tuple: StaticOrderSettings,
    ) -> None:
        # Decrease Position
        if long_short.lower() == "long":
            self.pnl_calc = self.long_pnl_calc
        elif long_short.lower() == "short":
            self.pnl_calc = self.short_pnl_calc
        else:
            raise Exception("long or short are the only options for long_short")

        self.obj_stop_loss = StopLoss(
            long_short=long_short,
            market_fee_pct=exchange_settings_tuple.market_fee_pct,
            pg_min_max_sl_bcb=static_os_tuple.pg_min_max_sl_bcb,
            price_tick_step=exchange_settings_tuple.price_tick_step,
            sl_strategy_type=static_os_tuple.sl_strategy_type,
            sl_to_be_bool=static_os_tuple.sl_to_be_bool,
            trail_sl_bool=static_os_tuple.trail_sl_bool,
            z_or_e_type=static_os_tuple.z_or_e_type,
        )
        self.obj_inc_pos = IncreasePosition(
            asset_tick_step=exchange_settings_tuple.asset_tick_step,
            increase_position_type=static_os_tuple.increase_position_type,
            long_short=long_short,
            market_fee_pct=exchange_settings_tuple.market_fee_pct,
            max_asset_size=exchange_settings_tuple.max_asset_size,
            min_asset_size=exchange_settings_tuple.min_asset_size,
            price_tick_step=exchange_settings_tuple.price_tick_step,
            sl_strategy_type=static_os_tuple.sl_strategy_type,
        )
        self.obj_leverage = Leverage(
            leverage_strategy_type=static_os_tuple.leverage_strategy_type,
            leverage_tick_step=exchange_settings_tuple.leverage_tick_step,
            long_short=long_short,
            market_fee_pct=exchange_settings_tuple.market_fee_pct,
            max_leverage=exchange_settings_tuple.max_leverage,
            min_leverage=exchange_settings_tuple.min_leverage,
            mmr_pct=exchange_settings_tuple.mmr_pct,
            price_tick_step=exchange_settings_tuple.price_tick_step,
            static_leverage=static_os_tuple.static_leverage,
        )

        if static_os_tuple.tp_fee_type.lower() == "market":
            tp_fee_pct = exchange_settings_tuple.market_fee_pct
        elif static_os_tuple.tp_fee_type.lower() == "limit":
            tp_fee_pct = exchange_settings_tuple.limit_fee_pct
        else:
            raise Exception("market or limit are the only options for tp_fee_type")

        self.obj_take_profit = TakeProfit(
            long_short=long_short,
            market_fee_pct=exchange_settings_tuple.market_fee_pct,
            price_tick_step=exchange_settings_tuple.price_tick_step,
            tp_fee_pct=tp_fee_pct,
            tp_strategy_type=static_os_tuple.tp_strategy_type,
        )

    def pass_func(self, **kwargs):
        pass

    def set_order_variables(self, equity: float):
        self.available_balance = equity
        self.average_entry = 0.0
        self.can_move_sl_to_be = False
        self.cash_borrowed = 0.0
        self.cash_used = 0.0
        self.entry_price = 0.0
        self.entry_size_asset = 0.0
        self.entry_size_usd = 0.0
        self.equity = equity
        self.exit_price = 0.0
        self.fees_paid = 0.0
        self.leverage = 0.0
        self.liq_price = 0.0
        self.order_status = 0
        self.position_size_asset = 0.0
        self.position_size_usd = 0.0
        self.total_possible_loss = 0.0
        self.realized_pnl = 0.0
        self.sl_pct = 0.0
        self.sl_price = 0.0
        self.total_trades = 0
        self.tp_pct = 0.0
        self.tp_price = 0.0

    def fill_or_exit_move(
        self,
        bar_index: int,
        dos_index: int,
        ind_set_index: int,
        order_records: np.array,
        order_status: OrderStatus,  # type: ignore
        timestamp: int,
        equity: float = np.nan,
        exit_price: float = np.nan,
        fees_paid: float = np.nan,
        realized_pnl: float = np.nan,
        sl_pct: float = np.nan,
        sl_price: float = np.nan,
    ):
        order_records["ind_set_idx"] = ind_set_index
        order_records["or_set_idx"] = dos_index
        order_records["bar_idx"] = bar_index
        order_records["timestamp"] = timestamp

        order_records["equity"] = equity
        order_records["available_balance"] = equity
        order_records["cash_borrowed"] = np.nan
        order_records["cash_used"] = np.nan

        order_records["average_entry"] = np.nan
        order_records["fees_paid"] = fees_paid
        order_records["leverage"] = np.nan
        order_records["liq_price"] = np.nan
        order_records["order_status"] = order_status
        order_records["total_possible_loss"] = 0
        order_records["total_trades"] = 0
        order_records["entry_size_asset"] = np.nan
        order_records["entry_size_usd"] = np.nan
        order_records["entry_price"] = np.nan
        order_records["exit_price"] = exit_price
        order_records["position_size_asset"] = np.nan
        order_records["position_size_usd"] = np.nan
        order_records["realized_pnl"] = realized_pnl
        order_records["sl_pct"] = sl_pct
        order_records["sl_price"] = sl_price
        order_records["tp_pct"] = np.nan
        order_records["tp_price"] = np.nan

    def fill_or_entry(
        self,
        bar_index: int,
        dos_index: int,
        ind_set_index: int,
        order_records: np.array,
        timestamp: int,
    ):
        order_records["ind_set_idx"] = ind_set_index
        order_records["or_set_idx"] = dos_index
        order_records["bar_idx"] = bar_index
        order_records["timestamp"] = timestamp

        order_records["equity"] = self.equity
        order_records["available_balance"] = self.available_balance
        order_records["cash_borrowed"] = self.cash_borrowed
        order_records["cash_used"] = self.cash_used

        order_records["average_entry"] = self.average_entry
        order_records["fees_paid"] = self.fees_paid
        order_records["leverage"] = self.leverage
        order_records["liq_price"] = self.liq_price
        order_records["order_status"] = self.order_status
        order_records["total_possible_loss"] = self.total_possible_loss
        order_records["total_trades"] = self.total_trades
        order_records["entry_size_asset"] = self.entry_size_asset
        order_records["entry_size_usd"] = self.entry_size_usd
        order_records["entry_price"] = self.entry_price
        order_records["exit_price"] = self.exit_price
        order_records["position_size_asset"] = self.position_size_asset
        order_records["position_size_usd"] = self.position_size_usd
        order_records["realized_pnl"] = self.realized_pnl
        order_records["sl_pct"] = round(self.sl_pct * 100, 3)
        order_records["sl_price"] = self.sl_price
        order_records["tp_pct"] = round(self.tp_pct * 100, 3)
        order_records["tp_price"] = self.tp_price

    def check_move_tsl(self, current_candle: np.array):
        return self.obj_stop_loss.checker_tsl(
            average_entry=self.average_entry,
            current_candle=current_candle,
            sl_price=self.sl_price,
        )

    def check_move_sl_to_be(self, current_candle: np.array):
        return self.obj_stop_loss.checker_sl_to_be(
            average_entry=self.average_entry,
            can_move_sl_to_be=self.can_move_sl_to_be,
            current_candle=current_candle,
            sl_price=self.sl_price,
        )

    def check_liq_hit(self, current_candle: np.array):
        self.obj_leverage.checker_liq_hit(
            current_candle=current_candle,
            liq_price=self.liq_price,
        )

    def check_take_profit_hit(
        self,
        current_candle: np.array,
        exit_price: float,
    ):
        self.obj_take_profit.checker_tp_hit(
            exit_price=exit_price,
            current_candle=current_candle,
            tp_price=self.tp_price,
        )

    def check_stop_loss_hit(self, current_candle: np.array):
        self.obj_stop_loss.checker_sl_hit(
            current_candle=current_candle,
            sl_price=self.sl_price,
        )

    def update_class_dos(
        self,
        dynamic_order_settings: DynamicOrderSettings,
    ):
        # take profit
        self.obj_take_profit.risk_reward = dynamic_order_settings.risk_reward

        # increase position
        self.obj_inc_pos.max_trades = dynamic_order_settings.max_trades
        self.obj_inc_pos.account_pct_risk_per_trade = dynamic_order_settings.account_pct_risk_per_trade

        # stop loss updates
        self.obj_stop_loss.sl_based_on_add_pct = dynamic_order_settings.sl_based_on_add_pct
        self.obj_stop_loss.sl_based_on_lookback = dynamic_order_settings.sl_based_on_lookback
        self.obj_stop_loss.sl_bcb_type = dynamic_order_settings.sl_bcb_type
        self.obj_stop_loss.sl_to_be_cb_type = dynamic_order_settings.sl_to_be_cb_type
        self.obj_stop_loss.sl_to_be_when_pct = dynamic_order_settings.sl_to_be_when_pct
        self.obj_stop_loss.trail_sl_bcb_type = dynamic_order_settings.trail_sl_bcb_type
        self.obj_stop_loss.trail_sl_by_pct = dynamic_order_settings.trail_sl_by_pct
        self.obj_stop_loss.trail_sl_when_pct = dynamic_order_settings.trail_sl_when_pct

    def calculate_stop_loss(
        self,
        bar_index: int,
        candles: np.array,
    ):
        sl_price = self.obj_stop_loss.sl_calculator(
            bar_index=bar_index,
            candles=candles,
        )
        logger.info(f"sl price= {sl_price}")
        return sl_price

    def calculate_increase_position(
        self,
        equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
        total_trades: int,
    ):
        (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct,
        ) = self.obj_inc_pos.inc_pos_calculator(
            equity=equity,
            average_entry=average_entry,
            entry_price=entry_price,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
            sl_price=sl_price,
            total_trades=total_trades,
        )
        logger.info(
            f"""
average_entry= {average_entry}
entry_price= {entry_price}
entry_size_asset= {entry_size_asset}
entry_size_usd= {entry_size_usd}
position_size_asset= {position_size_asset}
position_size_usd= {position_size_usd}
sl_pct= {round(sl_pct*100, 3)}"""
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            total_possible_loss,
            total_trades,
            sl_pct,
        )

    def calculate_leverage(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
        sl_price: float,
    ):
        (
            available_balance,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        ) = self.obj_leverage.lev_calculator(
            available_balance=available_balance,
            average_entry=average_entry,
            cash_borrowed=cash_borrowed,
            cash_used=cash_used,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
            sl_price=sl_price,
        )
        logger.info(
            f"""
available_balance= {available_balance}
cash_borrowed= {cash_borrowed}
cash_used= {cash_used}
leverage= {leverage}
liq_price= {liq_price}"""
        )
        return (
            available_balance,
            cash_borrowed,
            cash_used,
            leverage,
            liq_price,
        )

    def calculate_take_profit(
        self,
        average_entry: float,
        position_size_usd: float,
        total_possible_loss: float,
    ):
        (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        ) = self.obj_take_profit.tp_calculator(
            average_entry=average_entry,
            position_size_usd=position_size_usd,
            total_possible_loss=total_possible_loss,
        )
        logger.info(
            f"""
tp_price= {tp_price}
tp_pct= {round(tp_pct * 100, 3)}"""
        )
        return (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        )

    def long_pnl_calc(self, exit_price: float):
        return round((exit_price - self.average_entry) * self.position_size_asset, 3)  # math checked

    def short_pnl_calc(self, exit_price: float):
        return round((self.average_entry - exit_price) * self.position_size_asset, 3)  # math checked

    def calculate_decrease_position(
        self,
        exit_fee_pct: float,
        exit_price: float,
        equity: float,
        market_fee_pct: float,
        order_status: OrderStatus,  # type: ignore
    ):
        pnl = self.pnl_calc(exit_price=exit_price)  # math checked
        logger.debug(f"pnl= {pnl}")

        fee_open = round(self.position_size_asset * self.average_entry * market_fee_pct, 3)  # math checked
        logger.debug(f"fee_open= {fee_open}")

        fee_close = round(self.position_size_asset * exit_price * exit_fee_pct, 3)  # math checked
        logger.debug(f"fee_close= {fee_close}")

        fees_paid = round(fee_open + fee_close, 3)  # math checked
        logger.debug(f"fees_paid= {fees_paid}")

        realized_pnl = round(pnl - fees_paid, 3)  # math checked
        logger.debug(f"realized_pnl= {realized_pnl}")

        equity = round(realized_pnl + equity, 3)
        logger.debug(f"equity= {equity}")

        logger.info(
            f"""
equity= {equity}
fees_paid= {fees_paid}
order_status= {OrderStatus._fields[order_status]}
realized_pnl= {realized_pnl}"""
        )
        return (
            equity,
            fees_paid,
            realized_pnl,
        )

    def fill_order_result(
        self,
        available_balance: float,
        average_entry: float,
        can_move_sl_to_be: bool,
        cash_borrowed: float,
        cash_used: float,
        entry_price: float,
        entry_size_asset: float,
        entry_size_usd: float,
        equity: float,
        exit_price: float,
        fees_paid: float,
        leverage: float,
        liq_price: float,
        order_status: float,
        position_size_asset: float,
        position_size_usd: float,
        total_possible_loss: float,
        realized_pnl: float,
        sl_pct: float,
        sl_price: float,
        total_trades: int,
        tp_pct: float,
        tp_price: float,
    ):
        self.available_balance = available_balance
        self.average_entry = average_entry
        self.can_move_sl_to_be = can_move_sl_to_be
        self.cash_borrowed = cash_borrowed
        self.cash_used = cash_used
        self.entry_price = entry_price
        self.entry_size_asset = entry_size_asset
        self.entry_size_usd = entry_size_usd
        self.equity = equity
        self.exit_price = exit_price
        self.fees_paid = fees_paid
        self.leverage = leverage
        self.liq_price = liq_price
        self.order_status = order_status
        self.position_size_asset = position_size_asset
        self.position_size_usd = position_size_usd
        self.total_possible_loss = total_possible_loss
        self.realized_pnl = realized_pnl
        self.sl_pct = sl_pct
        self.sl_price = sl_price
        self.total_trades = total_trades
        self.tp_pct = tp_pct
        self.tp_price = tp_price
