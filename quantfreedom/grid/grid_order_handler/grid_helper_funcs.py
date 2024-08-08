import numpy as np

from quantfreedom.core.enums import CurrentFootprintCandleTuple, FootprintCandlesTuple, OrderStatus

from logging import getLogger

logger = getLogger()


class GridHelperFuncs:

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

    def fill_order_records(
        self,
        bar_index: int,
        order_records: np.ndarray,
        order_status: OrderStatus,  # type: ignore
        timestamp: int,
        set_idx: int,
        #
        #
        average_entry: float = np.nan,
        cash_borrowed: float = np.nan,
        cash_used: float = np.nan,
        entry_price: float = np.nan,
        entry_size_asset: float = np.nan,
        entry_size_usd: float = np.nan,
        equity: float = np.nan,
        exit_price: float = np.nan,
        fees_paid: float = np.nan,
        leverage: float = np.nan,
        liq_price: float = np.nan,
        position_size_asset: float = np.nan,
        position_size_usd: float = np.nan,
        total_possible_loss: float = np.nan,
        total_trades: int = -1,
        realized_pnl: float = np.nan,
        sl_pct: float = np.nan,
        sl_price: float = np.nan,
        tp_pct: float = np.nan,
        tp_price: float = np.nan,
    ):
        order_records["set_idx"] = set_idx
        order_records["bar_idx"] = bar_index
        order_records["timestamp"] = timestamp

        order_records["available_balance"] = equity
        order_records["average_entry"] = average_entry
        order_records["cash_borrowed"] = cash_borrowed
        order_records["cash_used"] = cash_used
        order_records["entry_size_asset"] = entry_size_asset
        order_records["entry_size_usd"] = entry_size_usd
        order_records["entry_price"] = entry_price
        order_records["equity"] = equity
        order_records["exit_price"] = exit_price
        order_records["fees_paid"] = fees_paid
        order_records["liq_price"] = liq_price
        order_records["leverage"] = leverage
        order_records["order_status"] = order_status
        order_records["total_possible_loss"] = total_possible_loss
        order_records["total_trades"] = total_trades
        order_records["position_size_asset"] = position_size_asset
        order_records["position_size_usd"] = position_size_usd
        order_records["realized_pnl"] = realized_pnl
        order_records["sl_pct"] = sl_pct
        order_records["sl_price"] = sl_price
        order_records["tp_pct"] = tp_pct
        order_records["tp_price"] = tp_price
