import numpy as np

from logging import getLogger

from quantfreedom.core.enums import CurrentFootprintCandleTuple, OrderStatus

from quantfreedom.grid.grid_order_handler.grid_ip import GridIncreasePosition
from quantfreedom.grid.grid_order_handler.grid_helper_funcs import GridHelperFuncs
from quantfreedom.grid.grid_order_handler.grid_leverage.grid_lev_class import GridLeverage
from quantfreedom.grid.grid_order_handler.grid_stop_loss.grid_sl_class import GridStopLoss
from quantfreedom.grid.grid_order_handler.grid_decrease_position.grid_dp_class import GridDecreasePosition


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

        self.market_fee_pct = 0.00075
        self.limit_fee_pct = 0.00025
        self.price_tick_step = 3
        self.mmr_pct = 0.00005

        self.helpers = GridHelperFuncs()
        self.leverage_class = GridLeverage()
        self.stop_loss_class = GridStopLoss()
        self.increase_position_class = GridIncreasePosition()
        self.decrease_position_class = GridDecreasePosition()

    def check_stop_loss_hit(
        self,
        check_sl_hit_bool: callable,
        current_candle: CurrentFootprintCandleTuple,
    ):
        self.stop_loss_class.grid_check_sl_hit(
            check_sl_hit_bool=check_sl_hit_bool,
            current_candle=current_candle,
            market_fee_pct=self.market_fee_pct,
            sl_price=self.sl_price,
        )

    def check_liq_hit(
        self,
        check_liq_hit_bool: callable,
        current_candle: CurrentFootprintCandleTuple,
    ):
        self.leverage_class.check_liq_hit(
            check_liq_hit_bool=check_liq_hit_bool,
            current_candle=current_candle,
            liq_price=self.liq_price,
            market_fee_pct=self.market_fee_pct,
        )

    def calculate_liquidation_price(
        self,
        average_entry: float,
        get_bankruptcy_price: callable,
        get_liq_price: callable,
        leverage: float,
        og_available_balance: float,
        og_cash_borrowed: float,
        og_cash_used: float,
        position_size_asset: float,
        position_size_usd: float,
    ):
        (
            available_balance,
            cash_borrowed,
            cash_used,
            rounded_liq_price,
        ) = self.leverage_class.calc_liq_price(
            average_entry=average_entry,
            get_bankruptcy_price=get_bankruptcy_price,
            get_liq_price=get_liq_price,
            leverage=leverage,
            market_fee_pct=self.market_fee_pct,
            mmr_pct=self.mmr_pct,
            og_available_balance=og_available_balance,
            og_cash_borrowed=og_cash_borrowed,
            og_cash_used=og_cash_used,
            position_size_asset=position_size_asset,
            position_size_usd=position_size_usd,
            price_tick_step=self.price_tick_step,
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
        get_pnl: callable,
        order_status: OrderStatus,  # type: ignore
    ):
        (
            equity,
            fees_paid,
            realized_pnl,
        ) = self.decrease_position_class.grid_decrease_position(
            average_entry=self.average_entry,
            cur_datetime=cur_datetime,
            exit_fee=exit_fee,
            exit_price=exit_price,
            exit_size_asset=exit_size_asset,
            equity=equity,
            get_pnl=get_pnl,
            order_status=order_status,
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

            position_size_asset = abs_position_size_usd / self.average_entry
            order_size_asset = order_size / entry_price
            total_asset_size = position_size_asset + order_size_asset

            new_average_entry = total_position_size_usd / total_asset_size

        except ZeroDivisionError:
            new_average_entry = entry_price

        return new_average_entry

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

    def set_grid_variables(
        self,
        available_balance: float,
        average_entry: float,
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
        order_status: OrderStatus,  # type: ignore
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
