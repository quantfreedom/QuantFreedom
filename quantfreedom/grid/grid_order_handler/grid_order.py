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
        self.mmr_pct = 0.5

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
            market_fee_pct=self.market_fee_pct,
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
            market_fee_pct=self.market_fee_pct,
        )

    def calculate_liquidation_price(
        self,
        average_entry: float,
        get_bankruptcy_price_exec: str,
        get_liq_price_exec: str,
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
            get_bankruptcy_price_exec=get_bankruptcy_price_exec,
            get_liq_price_exec=get_liq_price_exec,
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
        order_status: OrderStatus,  # type: ignore
        pnl_exec: str,
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
