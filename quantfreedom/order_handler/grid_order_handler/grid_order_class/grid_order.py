import numpy as np

from logging import getLogger

from quantfreedom.core.enums import CurrentFootprintCandleTuple, OrderStatus
from quantfreedom.order_handler.grid_order_handler import *

logger = getLogger()


class GridOrderHandler:
    liq_price: float
    sl_price: float
    average_entry: float
    limit_fee_pct: float
    market_fee_pct: float
    equity: float
    price_tick_step: float
    position_size_asset: float
    position_size_usd: float
    available_balance: float

    def __init__(
        self,
    ) -> None:
        pass

        self.helpers = GridHelperFuncs()
        self.leverage_class = GridLeverage()
        self.stop_loss_class = GridStopLoss()
        self.increase_position_class = GridIncreasePosition()
        self.decrease_position_class = GridDecreasePosition()

    def check_stop_loss_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        sl_hit_exec: str,
    ):
        self.stop_loss_class.grid_check_sl_hit(
            current_candle=current_candle,
            sl_hit_exec=sl_hit_exec,
            sl_price=self.sl_price,
        )

    def check_liq_hit(
        self,
        current_candle: CurrentFootprintCandleTuple,
        liq_hit_bool_exec: str,
    ):
        self.leverage_class.check_liq_hit(
            current_candle=current_candle,
            liq_price=self.liq_price,
            liq_hit_bool_exec=liq_hit_bool_exec,
        )

    def calculate_liquidation_price(
        self,
        average_entry: float,
        leverage: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
        get_bankruptcy_price_exec: str,
        get_liq_price_exec: str,
    ):
        (
            available_balance,
            cash_borrowed,
            cash_used,
            rounded_liq_price,
        ) = self.leverage_class.calc_liq_price(
            average_entry=average_entry,
            leverage=leverage,
            og_available_balance=og_available_balance,
            og_cash_borrowed=og_cash_borrowed,
            og_cash_used=og_cash_used,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
            get_bankruptcy_price_exec=get_bankruptcy_price_exec,
            get_liq_price_exec=get_liq_price_exec,
        )
        return (
            available_balance,
            cash_borrowed,
            cash_used,
            rounded_liq_price,
        )

    def calculate_decrease_position(
        self,
        cur_datetime: str,
        exit_fee: float,
        exit_price: float,
        exit_size_asset: float,
        equity: float,
        order_status: OrderStatus,  # type: ignore
        pnl_exec: str,
    ):
        (
            equity,
            fees_paid,
            realized_pnl,
        ) = self.decrease_position_class.grid_decrease_position(
            cur_datetime=cur_datetime,
            exit_fee=exit_fee,
            exit_price=exit_price,
            exit_size_asset=exit_size_asset,
            equity=equity,
            order_status=order_status,
            pnl_exec=pnl_exec,
        )

        return (
            equity,
            fees_paid,
            realized_pnl,
        )

    def calculate_average_entry(
        self,
        order_size: float,
        entry_price: float,
    ):
        try:
            abs_position_size_usd = abs(self.position_size_usd)
            total_position_size_usd = abs_position_size_usd + order_size

            position_size_asset = abs_position_size_usd / average_entry
            order_size_asset = order_size / entry_price
            total_asset_size = position_size_asset + order_size_asset

            average_entry = total_position_size_usd / total_asset_size

        except ZeroDivisionError:
            average_entry = entry_price

        return average_entry
