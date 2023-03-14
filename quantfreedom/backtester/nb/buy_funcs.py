import numpy as np
from numba import njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.enums.enums import *
from quantfreedom.backtester.nb.helper_funcs import order_not_filled_nb


# Long order to enter or add to a long position
@njit(cache=True)
def long_increase_nb(
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    equity: float,
    fee_pct: float,
    lev_mode: float,
    leverage: float,
    liq_price: float,
    max_equity_risk_pct: float,
    max_equity_risk_value: float,
    max_lev: float,
    mmr: float,
    position: float,
    price: float,
    risk_rewards: float,
    size_value: float,
    slippage_pct: float,

    sl_pcts: float,
    sl_prices: float,
    tp_pcts: float,
    tp_prices: float,
    tsl_pcts: float,
    tsl_prices: float,

    sl_be_then_trail: bool,
    sl_to_be_zero_or_entry: float,
    sl_to_be: bool,

    sl_pcts_order_result: float,
    sl_prices_order_result: float,
    tp_pcts_order_result: float,
    tp_prices_order_result: float,
    tsl_pcts_order_result: float,
    tsl_prices_order_result: float,

) -> tp.Tuple[TestTuple]:
    """
    How you place an order to start or increase a long position.

    Args:
        order: See [Order][backtester.enums.enums.OrderEverything].

        account_state: See [Account_State][backtester.enums.enums.AccountAndTradeState].
    """

    # new cash borrowed needs to be returned
    available_balance_new = available_balance
    average_entry_new = average_entry
    cash_used_new = cash_used
    leverage_new = leverage
    liq_price_new = liq_price
    position_new = position
    sl_pcts_new = sl_pcts
    sl_prices_new = sl_prices
    tp_pcts_new = tp_pcts
    tp_prices_new = tp_prices
    tsl_pcts_new = tsl_pcts
    tsl_prices_new = tsl_prices

    # Get average Entry
    if position_new != 0.:
        average_entry_new = (size_value + position_new) / (
            (size_value / price) + (position_new / average_entry_new))
    else:
        average_entry_new = price

    # setting new position_new
    position_new = position_new + size_value

    # Create stop loss prices if requested
    if not np.isnan(sl_pcts_new):
        sl_prices_new = average_entry_new - \
            (average_entry_new * sl_pcts_new)  # math checked
    elif not np.isnan(sl_prices_new):
        if sl_prices_new >= average_entry_new:
            sl_prices_new = average_entry_new
        # use  tsl if you want more than this
        sl_pcts_new = (average_entry_new - sl_prices_new) / \
            average_entry_new  # math checked
    else:
        sl_prices_new = np.nan
        sl_pcts_new = np.nan

    # Create trailing stop losses if requested
    if not np.isnan(tsl_pcts_new):
        tsl_prices_new = average_entry_new - \
            (average_entry_new * tsl_pcts_new)  # math checked
    elif not np.isnan(tsl_prices_new):
        # TODO figure out how to check to make sure the initial tsl price is not past the current entry
        tsl_pcts_new = (average_entry_new - tsl_prices_new) / \
            average_entry_new  # math checked
    else:
        tsl_prices_new = np.nan
        tsl_pcts_new = np.nan

    # Risk % check
    # checking if there is some sort of stop loss
    is_stop_loss = (not np.isnan(sl_prices_new) or
                    not np.isnan(tsl_prices_new) or
                    not np.isnan(liq_price_new))

    # checking if there is some sort max equity
    is_max_risk = (not np.isnan(max_equity_risk_pct) or
                   not np.isnan(max_equity_risk_value))

    if is_stop_loss and is_max_risk:
        # store temp sl price
        if not np.isnan(sl_prices_new):
            temp_price = sl_prices_new
        elif not np.isnan(tsl_prices_new):
            temp_price = tsl_prices_new
        elif not np.isnan(liq_price_new):
            temp_price = liq_price_new

        # calc possible loss
        coin_size = position_new / average_entry_new  # math checked
        pnl_no_fees = coin_size * \
            (temp_price - average_entry_new)  # math checked
        open_fee = coin_size * average_entry_new * \
            fee_pct  # math checked
        close_fee = coin_size * temp_price * \
            fee_pct  # math checked
        possible_loss = -(pnl_no_fees - open_fee -
                          close_fee)  # math checked
        possible_loss = float(int(possible_loss))

        # getting account risk amount
        if not np.isnan(max_equity_risk_pct):
            account_risk_amount = float(int(equity * max_equity_risk_pct))
        elif not np.isnan(max_equity_risk_value):
            account_risk_amount = max_equity_risk_value

        # check if our possible loss is more than what we are willing to risk of our account
        if 0 < possible_loss > account_risk_amount:
            return available_balance, \
                average_entry, \
                cash_borrowed, \
                cash_used, \
                leverage, \
                liq_price, \
                OrderStatus.Ignored, \
                OrderStatusInfo.MaxEquityRisk, \
                position, \
                sl_pcts_order_result, \
                sl_prices_order_result, \
                tp_pcts_order_result, \
                tp_prices_order_result, \
                tsl_pcts_order_result, \
                tsl_prices_order_result

    # check if leverage_new amount is possible with size_value and free cash
    if lev_mode == LeverageMode.LeastFreeCashUsed:
        # create leverage_new for sl
        if not np.isnan(sl_prices_new):
            temp_price = sl_prices_new
        elif not np.isnan(tsl_prices_new):
            temp_price = tsl_prices_new

        leverage_new = -average_entry_new / \
            (temp_price - temp_price * (.2 / 100) -  # TODO .2 is percent padding user wants
             average_entry_new - mmr * average_entry_new)  # math checked
        if leverage_new > max_lev:
            leverage_new = max_lev
    else:
        raise RejectedOrderError(
            "Long Increase - Either lev mode is nan or something is wrong with the leverage_new or leverage_new mode")

    # Getting Order Cost
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
    initial_margin = size_value/leverage_new
    fee_to_open = size_value * fee_pct  # math checked
    possible_bankruptcy_fee = size_value * \
        (leverage_new - 1) / leverage_new * fee_pct
    cash_used_new = initial_margin + fee_to_open + \
        possible_bankruptcy_fee  # math checked

    if cash_used_new > available_balance_new * leverage_new:
        raise RejectedOrderError(
            "long inrease iso lev - cash used greater than available balance * lev ... size_value is too big")

    elif cash_used_new > available_balance_new:
        raise RejectedOrderError(
            "long inrease iso lev - cash used greater than available balance ... maybe increase lev")

    else:
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        available_balance_new = available_balance_new - cash_used_new
        cash_used_new = cash_used + cash_used_new
        cash_borrowed_new = cash_borrowed + size_value - cash_used_new

        liq_price_new = average_entry_new * \
            (1 - (1/leverage_new) + mmr)  # math checked

    # Create take profits if requested
    if not np.isnan(risk_rewards):
        if np.isfinite(sl_prices_new):
            sl_or_tsl_prices = sl_prices_new
        elif np.isfinite(tsl_prices_new):
            sl_or_tsl_prices = tsl_prices_new

        coin_size = size_value / average_entry_new

        loss_no_fees = coin_size * (sl_or_tsl_prices - average_entry_new)

        fee_open = coin_size * average_entry_new * fee_pct

        fee_close = coin_size * sl_or_tsl_prices * fee_pct

        loss = loss_no_fees - fee_open - fee_close

        profit = -loss * risk_rewards

        tp_prices_new = ((profit + size_value * fee_pct + size_value) *
                         (average_entry_new/(size_value - size_value * fee_pct)))  # math checked

        tp_pcts_new = ((tp_prices_new - average_entry_new) /
                       average_entry_new)  # math checked

    elif not np.isnan(tp_pcts_new):
        tp_prices_new = (average_entry_new +
                         (average_entry_new * tp_pcts_new))  # math checked

    elif not np.isnan(tp_prices_new):
        tp_pcts_new = ((tp_prices_new - average_entry_new) /
                       average_entry_new)  # math checked
    else:
        tp_pcts_new = np.nan
        tp_prices_new = np.nan

    # Checking if we ran out of free cash or gone over our max risk amount
    if available_balance_new < 0:
        raise RejectedOrderError("long increase - avaialbe balance < 0")

    return available_balance_new,\
        average_entry_new,\
        cash_borrowed_new,\
        cash_used_new,\
        leverage_new,\
        liq_price_new,\
        OrderStatus.Filled,\
        OrderStatusInfo.HopefullyNoProblems,\
        position_new,\
        sl_pcts_new,\
        sl_prices_new,\
        tp_pcts_new,\
        tp_prices_new,\
        tsl_pcts_new,\
        tsl_prices_new


@ njit(cache=True)
def long_decrease_nb(
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    equity: float,
    fee_pct: float,
    liq_price: float,
    position: float,
    price: float,
    size_value: float,
) -> TestTuple:
    """
    This is where the long position gets decreased or closed out.
    """

    if size_value >= position:
        size_value = position

    pct_chg = (price - average_entry) / average_entry  # math checked

    # Set new position size_value and cash borrowed and cash used
    position_new = position - size_value
    position_pct_chg = (position - position_new) / position  # math checked

    # profit and loss calulation
    coin_size = size_value / average_entry  # math checked
    pnl = coin_size * (price - average_entry)  # math checked
    fee_open = coin_size * average_entry * fee_pct   # math checked
    fee_close = coin_size * price * fee_pct   # math checked
    fees_paid = fee_open + fee_close  # math checked
    realized_pnl = pnl - fees_paid  # math checked

    # Setting new equity
    equity_new = equity + realized_pnl

    cash_borrowed_new = cash_borrowed - (cash_borrowed * position_pct_chg)

    cash_used_new = cash_used - (cash_used * position_pct_chg)

    available_balance_new = realized_pnl + \
        available_balance + (cash_used * position_pct_chg)

    if position <= 0:
        liq_price = np.nan

    return available_balance_new,\
        cash_borrowed_new,\
        cash_used_new,\
        equity_new,\
        fees_paid,\
        liq_price, \
        OrderStatus.Filled, \
        OrderStatusInfo.HopefullyNoProblems, \
        position_new,\
        realized_pnl, \
        size_value
