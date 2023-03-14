import numpy as np
from numba import njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.enums import RejectedOrderError
from quantfreedom.backtester.enums.enums import *

@njit(cache=True)
def tester_thing(
    num: float,
):
    return num

@njit(cache=True)
def order_not_filled_nb(
    price: float,
    order: OrderEverything,
    status: float,
    status_info: float,
) -> ResultEverything:

    if order.order_type == OrderType.LongEntry:
        # Create stop loss prices if requested
        if not np.isnan(order.sl_pcts):
            sl_prices = (order.average_entry - order.average_entry *
                         order.sl_pcts / 100.)  # math checked
            sl_pcts = order.sl_pcts
        elif not np.isnan(order.sl_prices):
            if order.sl_prices < order.average_entry:
                sl_prices = order.sl_prices
            else:
                sl_prices = order.average_entry
            # use tsl if you want more than this
            sl_pcts = ((order.average_entry - sl_prices) /
                       order.average_entry) * 100  # math checked
        else:
            sl_prices = np.nan
            sl_pcts = np.nan

        # Create trailing stop losses if requested
        if not np.isnan(order.tsl_pcts):
            tsl_prices = order.average_entry - \
                (order.average_entry * order.tsl_pcts / 100)  # math checked
            tsl_pcts = order.tsl_pcts
        elif not np.isnan(order.tsl_prices):
            # TODO figure out how to check to make sure the initial tsl price is not past the current entry
            tsl_prices = order.tsl_prices
            tsl_pcts = ((order.average_entry - tsl_prices) /
                        order.average_entry) * 100  # math checked
        else:
            tsl_prices = np.nan
            tsl_pcts = np.nan

        # Create take profits if requested
        if not np.isnan(order.risk_rewards):
            coin_size = order.size / order.average_entry

            loss_no_fees = coin_size * (sl_prices - order.average_entry)

            fee_open = coin_size * order.average_entry * (order.fee / 100)

            fee_close = coin_size * sl_prices * (order.fee / 100)

            loss = loss_no_fees - fee_open - fee_close

            profit = -loss * order.risk_rewards

            tp_prices = ((profit + order.size + order.size * order.fee / 100) *
                         (order.average_entry/(order.size - order.size * order.fee / 100)))  # math checked

            tp_pcts = ((tp_prices - order.average_entry) /
                       order.average_entry) * 100  # math checked

        elif not np.isnan(order.tp_pcts):
            tp_prices = (order.average_entry +
                         (order.average_entry * order.tp_pcts / 100.))  # math checked

            tp_pcts = order.tp_pcts

        elif not np.isnan(order.tp_prices):
            tp_prices = order.tp_prices
            tp_pcts = ((tp_prices - order.average_entry) /
                       order.average_entry) * 100  # math checked
        else:
            tp_pcts = np.nan
            tp_prices = np.nan

    elif order.order_type == OrderType.ShortEntry:
        # Create stop loss prices if requested
        if not np.isnan(order.sl_pcts):
            sl_prices = (order.average_entry + order.average_entry *
                         order.sl_pcts / 100.)  # math checked
            sl_pcts = order.sl_pcts
        elif not np.isnan(order.sl_prices):
            if order.sl_prices < order.average_entry:
                sl_prices = order.sl_prices
            else:
                sl_prices = order.average_entry
            # use tsl if you want more than this
            sl_pcts = ((sl_prices - order.average_entry) /
                       order.average_entry) * 100  # math checked
        else:
            sl_prices = np.nan
            sl_pcts = np.nan

        # Create trailing stop losses if requested
        if not np.isnan(order.tsl_pcts):
            tsl_prices = order.average_entry + \
                (order.average_entry * (order.tsl_pcts / 100))  # math checked
            tsl_pcts = order.tsl_pcts
        elif not np.isnan(order.tsl_prices):
            # TODO figure out how to check to make sure the initial tsl price is not past the current entry
            tsl_prices = order.tsl_prices
            tsl_pcts = ((tsl_prices - order.average_entry) /
                        order.average_entry) * 100  # math checked
        else:
            tsl_prices = np.nan
            tsl_pcts = np.nan

        # Create take profits if requested
        if not np.isnan(order.risk_rewards):
            coin_size = order.size / order.average_entry

            loss_no_fees = coin_size * (order.average_entry - sl_prices)

            fee_open = coin_size * order.average_entry * (order.fee / 100)

            fee_close = coin_size * sl_prices * (order.fee / 100)

            loss = loss_no_fees - fee_open - fee_close

            profit = -loss * order.risk_rewards

            tp_prices = -((profit - order.size + order.size * order.fee / 100) *
                          (order.average_entry/(order.size + order.size * order.fee / 100)))  # math checked

            tp_pcts = ((order.average_entry - tp_prices) /
                       order.average_entry) * 100  # math checked

        elif not np.isnan(order.tp_pcts):
            tp_prices = (order.average_entry -
                         (order.average_entry * order.tp_pcts / 100.))  # math checked

            tp_pcts = order.tp_pcts

        elif not np.isnan(order.tp_prices):
            tp_prices = order.tp_prices
            tp_pcts = ((order.average_entry - tp_prices) /
                       order.average_entry) * 100  # math checked
        else:
            tp_pcts = np.nan
            tp_prices = np.nan

    order = ResultEverything(
        # required
        lev_mode=order.lev_mode,
        order_type=order.order_type,
        price=price,
        size_type=order.size_type,
        # not required
        allow_partial=order.allow_partial,
        available_balance=order.available_balance,
        average_entry=order.average_entry,
        cash_borrowed=order.cash_borrowed,
        cash_used=order.cash_used,
        equity=order.equity,
        fee=order.fee,
        fees_paid=order.fees_paid,
        leverage=order.leverage,
        liq_price=order.liq_price,
        log=order.log,
        max_equity_risk=order.max_equity_risk,
        max_equity_risk_pct=order.max_equity_risk_pct,
        max_lev=order.max_lev,
        max_order_pct_size=order.max_order_pct_size,
        max_order_size=order.max_order_size,
        min_order_pct_size=order.min_order_pct_size,
        min_order_size=order.min_order_size,
        mmr=order.mmr,
        pct_chg=order.pct_chg,
        position=order.position,
        raise_reject=order.raise_reject,
        realized_pnl=order.realized_pnl,
        reject_prob=order.reject_prob,
        risk_rewards=order.risk_rewards,
        size=order.size,
        size_pct=order.size_pct,
        sl_pcts=sl_pcts,
        sl_prices=sl_prices,
        slippage_pct=order.slippage_pct,
        status=status,
        status_info=status_info,
        tp_pcts=tp_pcts,
        tp_prices=tp_prices,
        tsl_pcts=tsl_pcts,
        tsl_prices=tsl_prices,
    )
    return order


# fill order records


@njit(cache=True)
def fill_order_records_nb(
    order_records: tp.Record,
    bar: int, # time stamp
    col: int, # indicator_settings
    group: int, # order settings
    order_count_id: int,
    order_result: ResultEverything,
) -> None:
    """
    Args:
        order_records: See [Order Numpy Data Type][quantfreedom.backtester.enums.enums.order_dt].
        bar: The current bar you are at in the loop of the coin (col).
        col: col usually represents the number of which coin you are in. \
        So lets say you are testing BTC and ETH, BTC would be col 0 and ETH would be col 1.
        order_count_id: The id of the order count.
        order_result: See [Order][quantfreedom.backtester.enums.enums.ResultEverything].

    !!! note
        If you want to keep track of something other than what is here in order records then i suggest doing it in log.
        Order records is mainly used for calculations for plotting and other things. Log is more for checking to make sure
        everything is working properly
    """
    # long entry
    if order_result.order_type == 0:
        order_type = 0
        coin_size = order_result.size / order_result.price

    # long stops
    elif 1 <= order_result.order_type <= 3:
        order_type = 1
        coin_size = order_result.size / order_result.average_entry

    # Short entry
    elif order_result.order_type == 5:
        order_type = 1
        coin_size = order_result.size / order_result.price

    # Short stops
    elif 6 <= order_result.order_type <= 9:
        order_type = 0
        coin_size = order_result.size / order_result.average_entry

    order_records['id'] = order_count_id
    order_records['group'] = group # order settings
    order_records['col'] = col # indicator_settings
    order_records['idx'] = bar # time stamp
    order_records['size'] = coin_size
    order_records['price'] = order_result.price
    order_records['fees'] = order_result.fees_paid
    order_records['realized_pnl'] = order_result.realized_pnl
    order_records['equity'] = order_result.equity
    order_records['sl_pct'] = order_result.sl_pcts
    order_records['rr'] = order_result.risk_rewards
    order_records['max_eq_risk_pct'] = order_result.max_equity_risk_pct
    order_records['side'] = order_type


# @njit(cache=True)
# def fill_order_records_nb(
#     order_records: tp.Record,
#     bar: int,
#     col: int,
#     order_count_id: int,
#     order_result: ResultEverything,
# ) -> None:
#     """

#     Args:
#         order_records: See [Order Numpy Data Type][quantfreedom.backtester.enums.enums.order_dt].
#         bar: The current bar you are at in the loop of the coin (col).
#         col: col usually represents the number of which coin you are in. \
#         So lets say you are testing BTC and ETH, BTC would be col 0 and ETH would be col 1.
#         order_count_id: The id of the order count.
#         order_result: See [Order][quantfreedom.backtester.enums.enums.ResultEverything].

#     !!! note
#         If you want to keep track of something other than what is here in order records then i suggest doing it in log.
#         Order records is mainly used for calculations for plotting and other things. Log is more for checking to make sure
#         everything is working properly
#     """
#     # long entry
#     if order_result.order_type == 0:
#         order_type = 0
#         coin_size = order_result.size / order_result.price

#     # long stops
#     elif 1 <= order_result.order_type <= 3:
#         order_type = 1
#         coin_size = order_result.size / order_result.average_entry

#     # Short entry
#     elif order_result.order_type == 5:
#         order_type = 1
#         coin_size = order_result.size / order_result.price

#     # Short stops
#     elif 6 <= order_result.order_type <= 9:
#         order_type = 0
#         coin_size = order_result.size / order_result.average_entry

#     order_records['id'] = order_count_id
#     order_records['col'] = col
#     order_records['idx'] = bar
#     order_records['size'] = coin_size
#     order_records['price'] = order_result.price
#     order_records['fees'] = order_result.fees_paid
#     order_records['side'] = order_type
#     order_records['realized_pnl'] = order_result.realized_pnl
#     order_records['equity'] = order_result.equity


@njit(cache=True)
def fill_log_records_nb(
    log_records: tp.Record,
    bar: int,
    col: int,
    group: int,
    log_count_id: int,
    order_count_id: int,
    order_result: ResultEverything,
    account_state: AccountAndTradeState,
    new_account_state: AccountAndTradeState,
) -> None:
    """
    Filling the log records.

    Args:
        log_records: See [log Numpy Data Type][quantfreedom.backtester.enums.enums.log_dt].
        bar: The current bar you are at in the loop of the coin (col).
        col: col usually represents the number of which coin you are in. \
        So lets say you are testing BTC and ETH, BTC would be col 0 and ETH would be col 1.
        group: If you group up your coins or anything else this will keep track of the group you are in.
        log_count_id: The id of the log count.
        order_count_id: The id of the order count.
        order_result: See [Order][quantfreedom.backtester.enums.enums.ResultEverything].
        account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].
        new_account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].

    !!! note
        if you want to create your own sections within the array to store then you need to add them here, then
        go over to the log data type and add the same thing there.

    """

    log_records['order_id'] = order_count_id
    log_records['id'] = log_count_id
    log_records['col'] = col
    log_records['idx'] = bar
    log_records['group'] = group
    log_records['leverage'] = order_result.leverage
    log_records['size'] = order_result.size
    log_records['size_usd'] = order_result.size
    log_records['price'] = order_result.price
    log_records['fees_paid'] = order_result.fees_paid
    log_records['order_type'] = order_result.order_type
    log_records['order_type'] = order_result.order_type
    log_records['avg_entry'] = order_result.average_entry
    log_records['tp_price'] = order_result.tp_prices
    log_records['sl_price'] = order_result.sl_prices
    log_records['liq_price'] = order_result.liq_price
    log_records['realized_pnl'] = order_result.realized_pnl
    log_records['equity'] = order_result.equity


@njit(cache=True)
def raise_rejected_order_nb(order: OrderEverything) -> None:
    """Raise an order error"""

    if order.status_info == OrderStatusInfo.SizeNaN:
        raise RejectedOrderError("Size is NaN")
    if order.status_info == OrderStatusInfo.PriceNaN:
        raise RejectedOrderError("Price is NaN")
    if order.status_info == OrderStatusInfo.ValPriceNaN:
        raise RejectedOrderError("Asset valuation price is NaN")
    if order.status_info == OrderStatusInfo.ValueNaN:
        raise RejectedOrderError("Asset/group value is NaN")
    if order.status_info == OrderStatusInfo.ValueZeroNeg:
        raise RejectedOrderError("Asset/group value is zero or negative")
    if order.status_info == OrderStatusInfo.SizeZero:
        raise RejectedOrderError("Size is zero")
    if order.status_info == OrderStatusInfo.NoCashShort:
        raise RejectedOrderError("Not enough cash to short")
    if order.status_info == OrderStatusInfo.NoCashLong:
        raise RejectedOrderError("Not enough cash to long")
    if order.status_info == OrderStatusInfo.NoOpenPosition:
        raise RejectedOrderError("No open position to reduce/close")
    if order.status_info == OrderStatusInfo.MaxSizeExceeded:
        raise RejectedOrderError("Size is greater than maximum allowed")
    if order.status_info == OrderStatusInfo.RandomEvent:
        raise RejectedOrderError("Random event happened")
    if order.status_info == OrderStatusInfo.CantCoverfee:
        raise RejectedOrderError("Not enough cash to cover fee")
    if order.status_info == OrderStatusInfo.MinSizeNotReached:
        raise RejectedOrderError("Final size is less than minimum allowed")
    if order.status_info == OrderStatusInfo.PartialFill:
        raise RejectedOrderError("Final size is less than requested")
    raise RejectedOrderError
