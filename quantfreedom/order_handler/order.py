from logging import getLogger
import numpy as np
from quantfreedom.enums import (
    DynamicOrderSettings,
    ExchangeSettings,
    LongOrShortType,
    OrderStatus,
    StaticOrderSettings,
    TakeProfitFeeType,
)
from quantfreedom.order_handler.decrease_position import LongDecreasePosition
from quantfreedom.order_handler.increase_position import LongIncreasePosition
from quantfreedom.order_handler.leverage import LongLeverage
from quantfreedom.order_handler.stop_loss import LongStopLoss
from quantfreedom.order_handler.take_profit import LongTakeProfit

logger = getLogger("info")


class OrderHandler:
    order_available_balance: float = 0
    order_average_entry: float = 0
    order_can_move_sl_to_be: bool = False
    order_cash_borrowed: float = 0
    order_cash_used: float = 0
    order_entry_price: float = 0
    order_entry_size_asset: float = 0
    order_entry_size_usd: float = 0
    order_equity: float = 0
    order_exit_price: float = 0
    order_fees_paid: float = 0
    order_leverage: float = 0
    order_liq_price: float = 0
    order_order_status: float = 0
    order_position_size_asset: float = 0
    order_position_size_usd: float = 0
    order_possible_loss: float = 0
    order_realized_pnl: float = 0
    order_sl_pct: float = 0
    order_sl_price: float = 0
    order_total_trades: int = 0
    order_tp_pct: float = 0
    order_tp_price: float = 0

    def __init__(
        self,
        static_os: StaticOrderSettings,
        exchange_settings: ExchangeSettings,
    ) -> None:
        if static_os.long_or_short == LongOrShortType.Long:
            # Decrease Position
            self.obj_dec_position = LongDecreasePosition(
                market_fee_pct=exchange_settings.market_fee_pct,
            )

            self.obj_stop_loss = LongStopLoss(
                market_fee_pct=exchange_settings.market_fee_pct,
                pg_min_max_sl_bcb=static_os.pg_min_max_sl_bcb,
                price_tick_step=exchange_settings.price_tick_step,
                sl_strategy_type=static_os.sl_strategy_type,
                sl_to_be_bool=static_os.sl_to_be_bool,
                trail_sl_bool=static_os.trail_sl_bool,
                z_or_e_type=static_os.z_or_e_type,
            )
            self.obj_inc_pos = LongIncreasePosition(
                asset_tick_step=exchange_settings.asset_tick_step,
                increase_position_type=static_os.increase_position_type,
                market_fee_pct=exchange_settings.market_fee_pct,
                max_asset_size=exchange_settings.max_asset_size,
                min_asset_size=exchange_settings.min_asset_size,
                price_tick_step=exchange_settings.price_tick_step,
                sl_strategy_type=static_os.sl_strategy_type,
            )
            self.obj_leverage = LongLeverage(
                leverage_strategy_type=static_os.leverage_strategy_type,
                leverage_tick_step=exchange_settings.leverage_tick_step,
                market_fee_pct=exchange_settings.market_fee_pct,
                max_leverage=exchange_settings.max_leverage,
                min_leverage=exchange_settings.min_leverage,
                mmr_pct=exchange_settings.mmr_pct,
                price_tick_step=exchange_settings.price_tick_step,
            )

            if static_os.tp_fee_type == TakeProfitFeeType.Market:
                tp_fee_pct = exchange_settings.market_fee_pct
            else:
                tp_fee_pct = exchange_settings.limit_fee_pct

            self.obj_take_profit = LongTakeProfit(
                market_fee_pct=exchange_settings.market_fee_pct,
                price_tick_step=exchange_settings.price_tick_step,
                tp_fee_pct=tp_fee_pct,
                tp_strategy_type=static_os.tp_strategy_type,
            )

    def pass_func(self, **vargs):
        pass

    def set_order_variables(self, equity: float):
        self.order_available_balance = equity
        self.order_average_entry = 0.0
        self.order_can_move_sl_to_be = False
        self.order_cash_borrowed = 0.0
        self.order_cash_used = 0.0
        self.order_entry_price = 0.0
        self.order_entry_size_asset = 0.0
        self.order_entry_size_usd = 0.0
        self.order_equity = equity
        self.order_exit_price = 0.0
        self.order_fees_paid = 0.0
        self.order_leverage = 0.0
        self.order_liq_price = 0.0
        self.order_order_status = 0
        self.order_position_size_asset = 0.0
        self.order_position_size_usd = 0.0
        self.order_possible_loss = 0.0
        self.order_realized_pnl = 0.0
        self.order_sl_pct = 0.0
        self.order_sl_price = 0.0
        self.order_total_trades = 0
        self.order_tp_pct = 0.0
        self.order_tp_price = 0.0

    def fill_or_exit_move(
        self,
        bar_index: int,
        dos_index: int,
        ind_set_index: int,
        order_records: np.array,
        order_status: OrderStatus,
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
        order_records["possible_loss"] = np.nan
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

        order_records["equity"] = self.order_equity
        order_records["available_balance"] = self.order_available_balance
        order_records["cash_borrowed"] = self.order_cash_borrowed
        order_records["cash_used"] = self.order_cash_used

        order_records["average_entry"] = self.order_average_entry
        order_records["fees_paid"] = self.order_fees_paid
        order_records["leverage"] = self.order_leverage
        order_records["liq_price"] = self.order_liq_price
        order_records["order_status"] = self.order_order_status
        order_records["possible_loss"] = self.order_possible_loss
        order_records["total_trades"] = self.order_total_trades
        order_records["entry_size_asset"] = self.order_entry_size_asset
        order_records["entry_size_usd"] = self.order_entry_size_usd
        order_records["entry_price"] = self.order_entry_price
        order_records["exit_price"] = self.order_exit_price
        order_records["position_size_asset"] = self.order_position_size_asset
        order_records["position_size_usd"] = self.order_position_size_usd
        order_records["realized_pnl"] = self.order_realized_pnl
        order_records["sl_pct"] = round(self.order_sl_pct * 100, 3)
        order_records["sl_price"] = self.order_sl_price
        order_records["tp_pct"] = round(self.order_tp_pct * 100, 3)
        order_records["tp_price"] = self.order_tp_price

    def check_move_tsl(self, current_candle: np.array):
        return self.obj_stop_loss.checker_tsl(
            average_entry=self.order_average_entry,
            current_candle=current_candle,
            sl_price=self.order_sl_price,
        )

    def check_move_sl_to_be(self, current_candle: np.array):
        return self.obj_stop_loss.checker_sl_to_be(
            average_entry=self.order_average_entry,
            can_move_sl_to_be=self.order_can_move_sl_to_be,
            current_candle=current_candle,
            sl_price=self.order_sl_price,
        )

    def check_liq_hit(self, current_candle: np.array):
        self.obj_leverage.checker_liq_hit(
            current_candle=current_candle,
            liq_price=self.order_liq_price,
        )

    def check_take_profit_hit(self, current_candle: np.array):
        self.obj_take_profit.checker_tp_hit(
            current_candle=current_candle,
            tp_price=self.order_tp_price,
        )

    def check_stop_loss_hit(self, current_candle: np.array):
        self.obj_stop_loss.checker_sl_hit(
            current_candle=current_candle,
            sl_price=self.order_sl_price,
        )

    def update_class_dos(
        self,
        dynamic_order_settings: DynamicOrderSettings,
    ):
        # take profit
        self.obj_take_profit.risk_reward = dynamic_order_settings.risk_reward

        # leverage
        self.obj_leverage.static_leverage = dynamic_order_settings.static_leverage

        # increase position
        self.obj_inc_pos.max_trades = dynamic_order_settings.max_trades
        self.obj_inc_pos.risk_account_pct_size = dynamic_order_settings.risk_account_pct_size
        self.obj_inc_pos.max_equity_risk_pct = dynamic_order_settings.max_equity_risk_pct

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

    def calculate_increase_posotion(
        self,
        equity: float,
        average_entry: float,
        entry_price: float,
        position_size_asset: float,
        position_size_usd: float,
        possible_loss: float,
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
            possible_loss,
            total_trades,
            sl_pct,
        ) = self.obj_inc_pos.inc_pos_calculator(
            equity=equity,
            average_entry=average_entry,
            entry_price=entry_price,
            in_position=position_size_asset > 0,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
            possible_loss=possible_loss,
            sl_price=sl_price,
            total_trades=total_trades,
        )
        logger.info(
            f"\n\
average_entry= {average_entry}\n\
entry_price= {entry_price}\n\
entry_size_asset= {entry_size_asset}\n\
entry_size_usd= {entry_size_usd}\n\
position_size_asset= {position_size_asset}\n\
position_size_usd= {position_size_usd}\n\
possible_loss= {possible_loss}\n\
total_trades= {total_trades}\n\
sl_pct= {round(sl_pct*100, 3)}"
        )
        return (
            average_entry,
            entry_price,
            entry_size_asset,
            entry_size_usd,
            position_size_asset,
            position_size_usd,
            possible_loss,
            total_trades,
            sl_pct,
        )

    def calculate_leverage(
        self,
        available_balance: float,
        average_entry: float,
        cash_borrowed: float,
        cash_used: float,
        entry_size_usd: float,
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
            entry_size_usd=entry_size_usd,
            sl_price=sl_price,
        )
        logger.info(
            f"\n\
available_balance= {available_balance}\n\
cash_borrowed= {cash_borrowed}\n\
cash_used= {cash_used}\n\
leverage= {leverage}\n\
liq_price= {liq_price}"
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
        possible_loss: float,
    ):
        (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        ) = self.obj_take_profit.tp_calculator(
            average_entry=average_entry,
            position_size_usd=position_size_usd,
            possible_loss=possible_loss,
        )
        logger.info(f"tp_price= {tp_price} tp_pct= {round(tp_pct * 100, 3)}")
        return (
            can_move_sl_to_be,
            tp_price,
            tp_pct,
        )

    def calculate_decrease_position(
        self,
        exit_fee_pct: float,
        exit_price: float,
        order_status: OrderStatus,
    ):
        (
            equity,
            fees_paid,
            realized_pnl,
        ) = self.obj_dec_position.dec_pos_calculator(
            average_entry=self.order_average_entry,
            equity=self.order_equity,
            exit_fee_pct=exit_fee_pct,
            exit_price=exit_price,
            position_size_asset=self.order_position_size_asset,
        )
        logger.info(
            f"\n\
equity= {equity}\n\
fees_paid= {fees_paid}\n\
order_status= {OrderStatus._fields[order_status]}\n\
realized_pnl= {realized_pnl}"
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
        possible_loss: float,
        realized_pnl: float,
        sl_pct: float,
        sl_price: float,
        total_trades: int,
        tp_pct: float,
        tp_price: float,
    ):
        self.order_available_balance = available_balance
        self.order_average_entry = average_entry
        self.order_can_move_sl_to_be = can_move_sl_to_be
        self.order_cash_borrowed = cash_borrowed
        self.order_cash_used = cash_used
        self.order_entry_price = entry_price
        self.order_entry_size_asset = entry_size_asset
        self.order_entry_size_usd = entry_size_usd
        self.order_equity = equity
        self.order_exit_price = exit_price
        self.order_fees_paid = fees_paid
        self.order_leverage = leverage
        self.order_liq_price = liq_price
        self.order_order_status = order_status
        self.order_position_size_asset = position_size_asset
        self.order_position_size_usd = position_size_usd
        self.order_possible_loss = possible_loss
        self.order_realized_pnl = realized_pnl
        self.order_sl_pct = sl_pct
        self.order_sl_price = sl_price
        self.order_total_trades = total_trades
        self.order_tp_pct = tp_pct
        self.order_tp_price = tp_price
