import numpy as np

from quantfreedom.order_handler.grid_order_handler.grid_order_class.grid_order import GridOrderHandler
from quantfreedom.core.enums import CurrentFootprintCandleTuple, FootprintCandlesTuple, OrderStatus

from logging import getLogger

logger = getLogger()


class GridHelperFuncs(GridOrderHandler):
    def get_current_candle(
        self,
        bar_index: int,
        candles: FootprintCandlesTuple,
    ):
        current_candle = CurrentFootprintCandleTuple(
            open_timestamp=candles.candle_open_timestamps[bar_index],
            open_price=candles.candle_open_prices[bar_index],
            high_price=candles.candle_high_prices[bar_index],
            low_price=candles.candle_low_prices[bar_index],
            close_price=candles.candle_close_prices[bar_index],
        )
        return current_candle

    def reset_grid_order_variables(
        self,
        equity: float,
    ):
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

    def fill_order_record_exit(
        self,
        bar_index: int,
        order_records: np.ndarray,
        order_status: OrderStatus,  # type: ignore
        timestamp: int,
        set_idx: int,
        equity: float = np.nan,
        exit_price: float = np.nan,
        fees_paid: float = np.nan,
        liq_price: float = np.nan,
        realized_pnl: float = np.nan,
        sl_price: float = np.nan,
    ):
        order_records["set_idx"] = set_idx
        order_records["bar_idx"] = bar_index
        order_records["timestamp"] = timestamp

        order_records["equity"] = equity
        order_records["available_balance"] = equity
        order_records["cash_borrowed"] = np.nan
        order_records["cash_used"] = np.nan

        order_records["average_entry"] = np.nan
        order_records["fees_paid"] = fees_paid
        order_records["leverage"] = np.nan
        order_records["liq_price"] = liq_price
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
        order_records["sl_pct"] = np.nan
        order_records["sl_price"] = sl_price
        order_records["tp_pct"] = np.nan
        order_records["tp_price"] = np.nan

    def fill_order_record_entry(
        self,
        bar_index: int,
        set_idx: int,
        order_records: np.ndarray,
        timestamp: int,
    ):
        order_records["set_idx"] = set_idx
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
        order_records["sl_pct"] = round(self.sl_pct * 100, 2)
        order_records["sl_price"] = self.sl_price
        order_records["tp_pct"] = round(self.tp_pct * 100, 2)
        order_records["tp_price"] = self.tp_price

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
