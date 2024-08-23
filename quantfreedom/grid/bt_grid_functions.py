import numpy as np
from os.path import join, abspath

from logging import getLogger

from quantfreedom.core.enums import (
    DecreasePosition,
    FootprintCandlesTuple,
    OrderStatus,
    RejectedOrder,
    ExchangeSettings,
    StaticOrderSettings,
    or_dt,
)

from quantfreedom.grid.grid_order_handler.grid_order import GridOrderHandler
from quantfreedom.grid.grid_order_handler.grid_leverage.grid_lev_exec import Grid_Lev_Funcs
from quantfreedom.grid.grid_order_handler.grid_stop_loss.grid_sl_exec import Grid_SL_Funcs
from quantfreedom.grid.grid_order_handler.grid_decrease_position.grid_dp_exec import Grid_DP_Funcs


logger = getLogger()


def adding_to_position(
    average_entry_array: np.ndarray,
    bar_index: int,
    entry_price: float,
    get_bankruptcy_price: callable,
    get_liq_price: callable,
    grid_order_handler: GridOrderHandler,
    leverage: float,
    long_short: str,
    order_size_usd: float,
    temp_pos_size_usd: float,
):
    logger.debug(f"either entering or adding to a {long_short} position adding to a {long_short} position")

    average_entry = grid_order_handler.calculate_average_entry(
        entry_price=entry_price,
        order_size_usd=order_size_usd,
    )

    (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = grid_order_handler.calculate_liquidation_price(
        average_entry=average_entry,
        equity=grid_order_handler.equity,
        get_bankruptcy_price=get_bankruptcy_price,
        get_liq_price=get_liq_price,
        leverage=leverage,
        position_size_usd=temp_pos_size_usd,
    )

    average_entry_array[bar_index] = average_entry
    entry_size_asset = order_size_usd / average_entry
    entry_size_usd = order_size_usd
    equity = grid_order_handler.equity
    exit_price = np.nan
    fees_paid = np.nan
    order_status = OrderStatus.EntryFilled
    realized_pnl = np.nan

    return (
        available_balance,
        average_entry,
        cash_borrowed,
        cash_used,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        equity,
        exit_price,
        fees_paid,
        liq_price,
        order_status,
        realized_pnl,
    )


def switching_positions(
    average_entry_array: np.ndarray,
    bar_index: int,
    cur_datetime: int,
    entry_price: float,
    exit_fee: float,
    from_str: str,
    get_pnl: callable,
    get_bankruptcy_price: callable,
    get_liq_price: callable,
    grid_order_handler: GridOrderHandler,
    leverage: float,
    order_size_usd: float,
    position_size_usd: float,
    temp_pos_size_usd: float,
    to_string: str,
):
    logger.debug(f"switching from {from_str} to {to_string}")

    (
        equity,
        fees_paid,
        realized_pnl,
    ) = grid_order_handler.calculate_decrease_position(
        cur_datetime=cur_datetime,
        exit_price=entry_price,
        exit_fee=exit_fee,
        exit_size_asset=position_size_usd / average_entry,
        equity=grid_order_handler.equity,
        get_pnl=get_pnl,
        order_status=OrderStatus.TakeProfitFilled,
    )

    (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = grid_order_handler.calculate_liquidation_price(
        average_entry=entry_price,
        equity=equity,
        get_bankruptcy_price=get_bankruptcy_price,
        get_liq_price=get_liq_price,
        leverage=leverage,
        position_size_usd=temp_pos_size_usd,
    )

    average_entry = entry_price
    entry_size_asset = order_size_usd / average_entry
    entry_size_usd = order_size_usd
    exit_price = entry_price
    order_status = OrderStatus.TakeProfitFilled

    average_entry_array[bar_index] = average_entry
    
    return (
        available_balance,
        average_entry,
        cash_borrowed,
        cash_used,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        equity,
        exit_price,
        fees_paid,
        liq_price,
        order_status,
        realized_pnl,
    )

def taking_profit_or_loss():
    logger.debug("tp on short")

    get_bankruptcy_price = Grid_Lev_Funcs.short_get_bankruptcy_price
    get_liq_price = Grid_Lev_Funcs.short_get_liq_price

    (
        equity,
        fees_paid,
        realized_pnl,
    ) = grid_order_handler.calculate_decrease_position(
        cur_datetime=candles.candle_open_datetimes[bar_index],
        exit_price=buy_order,
        exit_fee=grid_order_handler.limit_fee_pct,
        exit_size_asset=order_size_usd / average_entry,
        equity=equity,
        get_pnl=Grid_DP_Funcs.short_get_pnl,
        order_status=OrderStatus.TakeProfitFilled,
    )
    average_entry = grid_order_handler.average_entry
    entry_price = buy_order
    entry_size_asset = order_size_usd / average_entry
    entry_size_usd = order_size_usd
    exit_price = buy_order
    order_status = OrderStatus.TakeProfitFilled

    (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = grid_order_handler.calculate_liquidation_price(
        average_entry=average_entry,
        equity=grid_order_handler.equity,
        get_bankruptcy_price=get_bankruptcy_price,
        get_liq_price=get_liq_price,
        leverage=leverage,
        position_size_usd=abs(temp_pos_size_usd),
    )
