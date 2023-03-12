import numpy as np
from numba import njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.enums.enums import *
from quantfreedom.backtester.nb.helper_funcs import order_not_filled_nb


# Long order to enter or add to a long position
@njit(cache=True)
def long_increase_nb(
    price: float,
    order: OrderEverything,
    account_state: AccountAndTradeState,
) -> tp.Tuple[AccountAndTradeState, ResultEverything]:
    """
    How you place an order to start or increase a long position.

    Args:
        order: See [Order][quantfreedom.backtester.enums.enums.OrderEverything].

        account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].
    """

    # Setting variables
    available_balance = account_state.available_balance
    size = order.size

    # setting new position
    new_position = account_state.position + size

    # Get average Entry
    if account_state.position != 0.:
        new_average_entry = (size + account_state.position) / (
            size / price + account_state.position / account_state.average_entry)
    else:
        new_average_entry = price

    # Create stop loss prices if requested
    if not np.isnan(order.sl_pcts):
        sl_prices = (new_average_entry - new_average_entry *
                     order.sl_pcts / 100.)  # math checked
        sl_pcts = order.sl_pcts
    elif not np.isnan(order.sl_prices):
        if order.sl_prices < new_average_entry:
            sl_prices = order.sl_prices
        else:
            sl_prices = new_average_entry
        # use  tsl if you want more than this
        sl_pcts = ((new_average_entry - sl_prices) /
                   new_average_entry) * 100  # math checked
    else:
        sl_prices = np.nan
        sl_pcts = np.nan

    # Create trailing stop losses if requested
    if not np.isnan(order.tsl_pcts):
        tsl_prices = new_average_entry - (new_average_entry *
                                          order.tsl_pcts / 100.)  # math checked
        tsl_pcts = order.tsl_pcts
    elif not np.isnan(order.tsl_prices):
        # TODO figure out how to check to make sure the initial tsl price is not past the current entry
        tsl_prices = order.tsl_prices
        tsl_pcts = ((new_average_entry - tsl_prices) /
                    new_average_entry) * 100  # math checked
    else:
        tsl_prices = np.nan
        tsl_pcts = np.nan

    # Risk % check
    # checking if there is some sort of stop loss
    is_stop_loss = (not np.isnan(sl_prices) or
                    not np.isnan(tsl_prices) or
                    not np.isnan(account_state.liq_price))

    # checking if there is some sort max equity
    is_max_risk = (not np.isnan(order.max_equity_risk_pct) or
                   not np.isnan(order.max_equity_risk))

    if is_stop_loss and is_max_risk:
        # store temp sl price
        if not np.isnan(sl_prices):
            temp_price = sl_prices
        elif not np.isnan(tsl_prices):
            temp_price = tsl_prices
        elif not np.isnan(account_state.liq_price):
            temp_price = account_state.liq_price

        # calc possible loss
        coin_size = new_position / new_average_entry  # math checked
        pnl_no_fees = coin_size * \
            (temp_price - new_average_entry)  # math checked
        open_fee = coin_size * new_average_entry * \
            (account_state.fee / 100)  # math checked
        close_fee = coin_size * temp_price * \
            (account_state.fee/100)  # math checked
        possible_loss = -(pnl_no_fees - open_fee -
                          close_fee)  # math checked
        possible_loss = float(int(possible_loss))

        # getting account risk amount
        if not np.isnan(order.max_equity_risk_pct):
            account_risk_amount = (
                account_state.equity * order.max_equity_risk_pct / 100)
            account_risk_amount = float(
                int(account_risk_amount))  # math checked
        elif not np.isnan(order.max_equity_risk):
            account_risk_amount = order.max_equity_risk

        # check if our possible loss is more than what we are willing to risk of our account
        if 0 < possible_loss > account_risk_amount:
            return account_state, order_not_filled_nb(
                price=price, status=OrderStatus.Rejected,
                status_info=OrderStatusInfo.MaxEquityRisk, order=order)

    # check if leverage amount is possible with size and free cash
    if order.lev_mode == LeverageMode.Isolated:
        leverage = order.leverage
    elif order.lev_mode == LeverageMode.LeastFreeCashUsed:
        # create leverage for sl
        if not np.isnan(sl_prices):
            temp_price = sl_prices
        elif not np.isnan(tsl_prices):
            temp_price = tsl_prices

        leverage = -new_average_entry / (
            # the .001 is putting the liq price .1% below sl price
            temp_price - ((temp_price * .2) / 100) -
            new_average_entry - (
                ((account_state.mmr * new_average_entry) / 100)
            )
        )  # math checked
        if leverage > order.max_lev:
            leverage = order.max_lev
    else:
        raise RejectedOrderError(
            "Either lev mode is nan or something is wrong with the leverage or leverage mode")

    # Getting Order Cost
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
    initial_margin = size/leverage
    fee_to_open = size * (account_state.fee / 100)  # math checked
    possible_bankruptcy_fee = size * \
        (leverage - 1) / leverage * (account_state.fee / 100)
    cash_used = initial_margin + fee_to_open + \
        possible_bankruptcy_fee  # math checked

    if cash_used > available_balance * leverage:
        # raise RejectedOrderError(
        #     "long inrease iso lev - cash used greater than available balance * lev ... size is too big")
        return account_state, order_not_filled_nb(
            price=price, status=OrderStatus.Rejected,
            status_info=OrderStatusInfo.MaxSizeExceeded, order=order)

    elif cash_used > available_balance:
        # raise RejectedOrderError(
        #     "long inrease iso lev - cash used greater than available balance ... maybe increase lev")
        return account_state, order_not_filled_nb(
            price=price, status=OrderStatus.Rejected,
            status_info=OrderStatusInfo.LevToSmall, order=order)

    else:
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        new_available_balance = available_balance - cash_used
        new_cash_used = account_state.cash_used + cash_used
        cash_borrowed = size - cash_used

        new_liq_price = new_average_entry * \
            (1 - (1/leverage) + (account_state.mmr / 100))  # math checked

    # Create take profits if requested
    if not np.isnan(order.risk_rewards):
        coin_size = size / new_average_entry

        loss_no_fees = coin_size * (sl_prices - new_average_entry)

        fee_open = coin_size * new_average_entry * (account_state.fee / 100)

        fee_close = coin_size * sl_prices * (account_state.fee / 100)

        loss = loss_no_fees - fee_open - fee_close

        profit = -loss * order.risk_rewards

        tp_prices = ((profit + size * (account_state.fee/100) + size) *
                     (new_average_entry/(size - size * (account_state.fee/100))))  # math checked

        tp_pcts = ((tp_prices - new_average_entry) /
                   new_average_entry) * 100  # math checked

    elif not np.isnan(order.tp_pcts):
        tp_prices = (new_average_entry +
                     (new_average_entry * order.tp_pcts / 100.))  # math checked

        tp_pcts = order.tp_pcts

    elif not np.isnan(order.tp_prices):
        tp_prices = order.tp_prices
        tp_pcts = ((tp_prices - new_average_entry) /
                   new_average_entry) * 100  # math checked
    else:
        tp_pcts = np.nan
        tp_prices = np.nan

    # Checking if we ran out of free cash or gone over our max risk amount
    if new_available_balance < 0:
        return account_state, order_not_filled_nb(
            price=price,
            status=OrderStatus.Rejected,
            status_info=OrderStatusInfo.NewFreeCashZeroOrLower,
            order=order)

    # Return filled order
    order_result = ResultEverything(
        # required
        lev_mode=order.lev_mode,
        order_type=order.order_type,
        price=price,
        size_type=order.size_type,
        # not required
        allow_partial=order.allow_partial,
        available_balance=new_available_balance,
        average_entry=new_average_entry,
        cash_borrowed=cash_borrowed,
        cash_used=cash_used,
        equity=account_state.equity,
        fee=account_state.fee,
        fees_paid=0.,
        leverage=leverage,
        liq_price=new_liq_price,
        log=order.log,
        max_equity_risk=order.max_equity_risk,
        max_equity_risk_pct=order.max_equity_risk_pct,
        max_lev=order.max_lev,
        max_order_pct_size=order.max_order_pct_size,
        max_order_size=order.max_order_size,
        min_order_pct_size=order.min_order_pct_size,
        min_order_size=order.min_order_size,
        mmr=account_state.mmr,
        pct_chg=np.nan,
        position=new_position,
        raise_reject=order.raise_reject,
        realized_pnl=np.nan,
        reject_prob=order.reject_prob,
        risk_rewards=order.risk_rewards,
        size=size,
        size_pct=order.size_pct,
        sl_pcts=sl_pcts,
        sl_prices=sl_prices,
        slippage_pct=order.slippage_pct,
        status=OrderStatus.Filled,
        status_info=OrderStatusInfo.HopefullyNoProblems,
        tp_pcts=tp_pcts,
        tp_prices=tp_prices,
        tsl_pcts=tsl_pcts,
        tsl_prices=tsl_prices,
    )

    new_account_state = AccountAndTradeState(
        available_balance=new_available_balance,
        average_entry=new_average_entry,
        cash_borrowed=cash_borrowed,
        cash_used=new_cash_used,
        equity=account_state.equity,
        fee=account_state.fee,
        leverage=leverage,
        liq_price=new_liq_price,
        mmr=account_state.mmr,
        position=new_position,
        realized_pnl=np.nan,
    )
    return new_account_state, order_result


@ njit(cache=True)
def long_decrease_nb(
    price: float,
    order: OrderEverything,
    account_state: AccountAndTradeState,
) -> tp.Tuple[AccountAndTradeState, ResultEverything]:
    """
    This is where the long position gets decreased or closed out.

    Args:
        order: See [Order][quantfreedom.backtester.enums.enums.OrderEverything].

        account_state: See [Account_State][quantfreedom.backtester.enums.enums.AccountAndTradeState].
    """

    if order.size >= account_state.position:
        size = account_state.position
    else:
        size = order.size

    pct_chg = ((price - account_state.average_entry) /
               account_state.average_entry) * 100  # math checked

    # Set new position size and cash borrowed and cash used
    new_position = account_state.position - size
    position_pct_chg = ((account_state.position -
                         new_position) / account_state.position) * 100  # math checked

    # profit and loss calulation
    coin_size = size / account_state.average_entry  # math checked
    pnl = coin_size * \
        (price - account_state.average_entry)  # math checked
    fee_open = coin_size * account_state.average_entry * \
        (account_state.fee / 100)  # math checked
    fee_close = coin_size * price * \
        (account_state.fee / 100)  # math checked
    fees_paid = fee_open + fee_close  # math checked
    realized_pnl = pnl - fees_paid  # math checked

    # Setting new equity
    new_equity = account_state.equity + realized_pnl

    new_cash_borrowed = account_state.cash_borrowed - \
        (account_state.cash_borrowed * (position_pct_chg / 100))
    new_cash_used = account_state.cash_used - \
        (account_state.cash_used * (position_pct_chg / 100))
    new_available_balance = realized_pnl + \
        account_state.available_balance + \
        (account_state.cash_used * (position_pct_chg / 100))

    # If we close out of the trade
    if new_position <= 0:
        order_result = ResultEverything(
            # required
            lev_mode=order.lev_mode,
            order_type=order.order_type,
            price=price,
            size_type=order.size_type,
            # not required
            allow_partial=order.allow_partial,
            available_balance=new_available_balance,
            average_entry=order.average_entry,
            cash_borrowed=new_cash_borrowed,
            cash_used=new_cash_used,
            equity=new_equity,
            fee=account_state.fee,
            fees_paid=fees_paid,
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
            mmr=account_state.mmr,
            pct_chg=pct_chg,
            position=new_position,
            raise_reject=order.raise_reject,
            realized_pnl=realized_pnl,
            reject_prob=order.reject_prob,
            risk_rewards=order.risk_rewards,
            size=size,
            size_pct=order.size_pct,
            sl_pcts=order.sl_pcts,
            sl_prices=order.sl_prices,
            slippage_pct=order.slippage_pct,
            status=OrderStatus.Filled,
            status_info=OrderStatusInfo.HopefullyNoProblems,
            tp_pcts=order.tp_pcts,
            tp_prices=order.tp_prices,
            tsl_pcts=order.tsl_pcts,
            tsl_prices=order.tsl_prices,
        )
        new_account_state = AccountAndTradeState(
            available_balance=new_available_balance,
            average_entry=0.,
            cash_borrowed=0.,
            cash_used=0.,
            equity=new_equity,
            fee=account_state.fee,
            leverage=1.,
            liq_price=0.,
            mmr=account_state.mmr,
            position=0.,
            realized_pnl=realized_pnl,
        )
    else:
        order_result = ResultEverything(
            # required
            lev_mode=order.lev_mode,
            order_type=order.order_type,
            price=price,
            size_type=order.size_type,
            # not required
            allow_partial=order.allow_partial,
            available_balance=new_available_balance,
            average_entry=account_state.average_entry,
            cash_borrowed=new_cash_borrowed,
            cash_used=new_cash_used,
            equity=new_equity,
            fee=account_state.fee,
            fees_paid=fees_paid,
            leverage=account_state.leverage,
            liq_price=account_state.liq_price,
            log=order.log,
            max_equity_risk=order.max_equity_risk,
            max_equity_risk_pct=order.max_equity_risk_pct,
            max_lev=order.max_lev,
            max_order_pct_size=order.max_order_pct_size,
            max_order_size=order.max_order_size,
            min_order_pct_size=order.min_order_pct_size,
            min_order_size=order.min_order_size,
            mmr=account_state.mmr,
            pct_chg=pct_chg,
            position=new_position,
            raise_reject=order.raise_reject,
            realized_pnl=realized_pnl,
            reject_prob=order.reject_prob,
            risk_rewards=order.risk_rewards,
            size=size,
            size_pct=order.size_pct,
            sl_pcts=order.sl_pcts,
            sl_prices=order.sl_prices,
            slippage_pct=order.slippage_pct,
            status=OrderStatus.Filled,
            status_info=OrderStatusInfo.HopefullyNoProblems,
            tp_pcts=order.tp_pcts,
            tp_prices=order.tp_prices,
            tsl_pcts=order.tsl_pcts,
            tsl_prices=order.tsl_prices,
        )
        new_account_state = AccountAndTradeState(
            available_balance=new_available_balance,
            average_entry=account_state.average_entry,
            cash_borrowed=new_cash_borrowed,
            cash_used=new_cash_used,
            equity=new_equity,
            fee=account_state.fee,
            leverage=account_state.leverage,
            liq_price=account_state.liq_price,
            mmr=account_state.mmr,
            position=new_position,
            realized_pnl=realized_pnl,
        )

    return new_account_state, order_result
