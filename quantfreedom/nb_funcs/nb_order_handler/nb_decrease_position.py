from typing import Callable
from numba import njit

from quantfreedom.enums import AccountState, LoggerFuncType, OrderResult, StringerFuncType


@njit(cache=True)
def nb_long_pnl_calc(
    average_entry: float,
    exit_price: float,
    position_size_asset: float,
):
    return round((exit_price - average_entry) * position_size_asset, 3)  # math checked


@njit(cache=True)
def nb_short_pnl_calc(
    average_entry: float,
    exit_price: float,
    position_size_asset: float,
):
    return round((average_entry - exit_price) * position_size_asset, 3)  # math checked


@njit(cache=True)
def nb_decrease_position(
    average_entry: float,
    bar_index: int,
    dos_index: int,
    equity: float,
    exit_fee_pct: float,
    exit_price: float,
    ind_set_index: int,
    logger,
    market_fee_pct: float,
    nb_pnl_calc,
    order_status: int,
    position_size_asset: float,
    stringer,
    timestamp: int,
) -> tuple[AccountState, OrderResult]:
    pnl = nb_pnl_calc(
        average_entry=average_entry,
        exit_price=exit_price,
        position_size_asset=position_size_asset,
    )  # math checked
    fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
    fee_close = position_size_asset * exit_price * exit_fee_pct  # math checked
    fees_paid = fee_open + fee_close  # math checked
    realized_pnl = round(pnl - fees_paid, 3)  # math checked

    # Setting new equity
    equity = round(realized_pnl + equity, 3)
    logger(
        "nb_decrease_position.py - nb_decrease_position() -"
        + "\nrealized_pnl= "
        + stringer[StringerFuncType.float_to_str](realized_pnl)
        + "\nequity= "
        + stringer[StringerFuncType.float_to_str](equity)
        + "\nfees_paid= "
        + stringer[StringerFuncType.float_to_str](fees_paid)
        + "\norder status= "
        + stringer[StringerFuncType.os_to_str](order_status)
    )

    account_state = AccountState(
        # where we are at
        ind_set_index=ind_set_index,
        dos_index=dos_index,
        bar_index=bar_index,
        timestamp=timestamp,
        # account info
        available_balance=equity,
        cash_borrowed=0.0,
        cash_used=0.0,
        equity=equity,
        fees_paid=fees_paid,
        possible_loss=0,
        realized_pnl=realized_pnl,
        total_trades=0,
    )
    order_result = OrderResult(
        average_entry=0.0,
        can_move_sl_to_be=False,
        entry_price=0.0,
        entry_size_asset=0.0,
        entry_size_usd=0.0,
        exit_price=exit_price,
        leverage=0.0,
        liq_price=0.0,
        order_status=order_status,
        position_size_asset=0.0,
        position_size_usd=0.0,
        sl_pct=0.0,
        sl_price=0.0,
        tp_pct=0.0,
        tp_price=0.0,
    )

    return account_state, order_result
