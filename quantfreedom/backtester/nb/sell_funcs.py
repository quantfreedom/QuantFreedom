import numpy as np
from numba import njit

from quantfreedom._typing import Tuple

from quantfreedom.backtester.enums.enums import (
    AccountState,
    EntryOrder,
    OrderResult,
    OrderStatus,
    OrderStatusInfo,
    RejectedOrderError,
    LeverageMode,
    StaticVariables,
    SizeType,
)


# Long order to enter or add to a long position
@njit(cache=True)
def short_increase_nb(
    price: float,

    account_state: AccountState,
    entry_order: EntryOrder,
    order_result: OrderResult,
    static_variables: StaticVariables,
) -> Tuple[AccountState, OrderResult]:

    # new cash borrowed needs to be returned
    available_balance_new = account_state.available_balance
    cash_used_new = account_state.cash_used
    leverage_new = entry_order.leverage
    average_entry_new = order_result.average_entry
    liq_price_new = order_result.liq_price
    position_new = order_result.position

    sl_pcts_new = entry_order.sl_pcts
    tp_pcts_new = entry_order.tp_pcts
    tsl_pcts_init_new = entry_order.tsl_pcts_init

    # sl_prices_new = order_result.sl_prices
    # tsl_prices_new = order_result.tsl_prices
    # tp_prices_new = order_result.tp_prices

    sl_prices_new = np.nan
    tsl_prices_new = np.nan
    tp_prices_new = np.nan

    if static_variables.size_type != SizeType.Amount and \
            static_variables.size_type != SizeType.PercentOfAccount:

        if np.isfinite(sl_pcts_new):
            if static_variables.size_type == SizeType.RiskPercentOfAccount:
                size_value = account_state.equity * entry_order.size_pct / sl_pcts_new

            elif static_variables.size_type == SizeType.RiskAmount:
                size_value = entry_order.size_value / sl_pcts_new
                if size_value < 1:
                    raise ValueError(
                        "Risk Amount has produced a size_value values less than 1.")
            temp_sl_price = price + (price * sl_pcts_new)
            possible_loss = size_value * sl_pcts_new

            size_value = -possible_loss / \
                (1 - temp_sl_price / price - static_variables.fee_pct -
                 temp_sl_price * static_variables.fee_pct / price)

        elif np.isfinite(tsl_pcts_init_new):
            if static_variables.size_type == SizeType.RiskPercentOfAccount:
                size_value = account_state.equity * entry_order.size_pct / tsl_pcts_init_new

            elif static_variables.size_type == SizeType.RiskAmount:
                size_value = entry_order.size_value / tsl_pcts_init_new
                if size_value < 1:
                    raise ValueError(
                        "Risk Amount has produced a size_value values less than 1.")
            temp_tsl_price = price + (price * tsl_pcts_init_new)
            possible_loss = size_value * (tsl_pcts_init_new)

            size_value = -possible_loss / \
                (1 - temp_tsl_price / price - static_variables.fee_pct -
                 temp_tsl_price * static_variables.fee_pct / price)

    elif static_variables.size_type == SizeType.Amount:
        size_value = entry_order.size_value
        if size_value > static_variables.max_order_size_value:
            size_value = static_variables.max_order_size_value
        elif size_value == np.inf:
            size_value = order_result.position

    # getting size_value for percent of account
    elif static_variables.size_type == SizeType.PercentOfAccount:
        size_value = account_state.equity * entry_order.size_pct  # math checked

    else:
        raise TypeError(
            "I have no clue what is wrong but something is wrong with making the size_value using size_value type")

    # TODO talk to someone who would want to use set prices for sl and trailing sl
    # if np.isfinite(sl_prices_new):
    #     sl_prices_new = price - sl_prices_new
    #     sl_pcts_new = (price - sl_prices_new) / price
    #     possible_loss = size_value * sl_pcts_new

    #     size_value = -possible_loss / \
    #         ((sl_prices_new/price - 1) - static_variables.fee_pct -
    #             (sl_prices_new * static_variables.fee_pct / price))

    # elif np.isfinite(tsl_prices_new):
    #     tsl_pcts_init_new = (price - tsl_prices_new) / price
    #     possible_loss = size_value * tsl_pcts_init_new

    #     size_value = -possible_loss / \
    #         ((tsl_prices_new/price - 1) - static_variables.fee_pct -
    #             (tsl_prices_new * static_variables.fee_pct / price))

    if size_value < 1 or \
            size_value > static_variables.max_order_size_value or \
            size_value < static_variables.min_order_size_value:
        raise RejectedOrderError(
            "Long Increase - Size Value is either to big or too small"
        )

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
        sl_prices_new = average_entry_new + \
            (average_entry_new * sl_pcts_new)  # math checked
    else:
        sl_prices_new = np.nan
        sl_pcts_new = np.nan

    # Create trailing stop losses if requested
    if not np.isnan(tsl_pcts_init_new):
        tsl_prices_new = average_entry_new + \
            (average_entry_new * tsl_pcts_init_new)  # math checked
    else:
        tsl_prices_new = np.nan
        tsl_pcts_init_new = np.nan

    # Risk % check
    # checking if there is some sort of stop loss
    is_stop_loss = (not np.isnan(sl_prices_new) or
                    not np.isnan(tsl_prices_new) or
                    not np.isnan(liq_price_new))

    # checking if there is some sort max equity
    is_max_risk = (not np.isnan(entry_order.max_equity_risk_pct) or
                   not np.isnan(entry_order.max_equity_risk_value))

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
            (average_entry_new - temp_price)  # math checked

        open_fee = coin_size * average_entry_new * \
            static_variables.fee_pct  # math checked

        close_fee = coin_size * temp_price * \
            static_variables.fee_pct  # math checked

        possible_loss = -(pnl_no_fees - open_fee -
                          close_fee)  # math checked

        possible_loss = float(int(possible_loss))

        # getting account risk amount
        if not np.isnan(entry_order.max_equity_risk_pct):
            account_risk_amount = float(
                int(account_state.equity * entry_order.max_equity_risk_pct)
            )
        elif not np.isnan(entry_order.max_equity_risk_value):
            account_risk_amount = entry_order.max_equity_risk_value

        # check if our possible loss is more than what we are willing to risk of our account
        if 0 < possible_loss > account_risk_amount:
            return account_state, \
                OrderResult(
                    average_entry=order_result.average_entry,
                    fees_paid=np.nan,
                    leverage=order_result.leverage,
                    liq_price=order_result.liq_price,
                    moved_sl_to_be=order_result.moved_sl_to_be,
                    order_status=OrderStatus.Ignored,
                    order_status_info=OrderStatusInfo.MaxEquityRisk,
                    order_type=entry_order.order_type,
                    pct_chg_trade=np.nan,
                    position=order_result.position,
                    price=price,
                    realized_pnl=np.nan,
                    size_value=np.nan,
                    sl_pcts=order_result.sl_pcts,
                    sl_prices=order_result.sl_prices,
                    tp_pcts=order_result.tp_pcts,
                    tp_prices=order_result.tp_prices,
                    tsl_pcts_init=order_result.tsl_pcts_init,
                    tsl_prices=order_result.tsl_prices,
                )

    # check if leverage_new amount is possible with size_value and free cash
    # TODO add in info for leverage iso
    if static_variables.lev_mode == LeverageMode.LeastFreeCashUsed:
        # create leverage_new for sl
        if not np.isnan(sl_prices_new):
            temp_price = sl_prices_new
        elif not np.isnan(tsl_prices_new):
            temp_price = tsl_prices_new

        leverage_new = average_entry_new / \
            (temp_price + temp_price * .002 -  # TODO .2 is percent padding user wants
             average_entry_new + static_variables.mmr * average_entry_new)  # math checked

        if leverage_new > static_variables.max_lev:
            leverage_new = static_variables.max_lev
    else:
        raise RejectedOrderError(
            "Long Increase - Either lev mode is nan or something is wrong with the leverage_new or leverage_new mode")

    # Getting Order Cost
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
    initial_margin = size_value/leverage_new
    fee_to_open = size_value * static_variables.fee_pct  # math checked

    possible_bankruptcy_fee = size_value * \
        (leverage_new + 1) / leverage_new * static_variables.fee_pct

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
        cash_used_new = account_state.cash_used + cash_used_new
        cash_borrowed_new = account_state.cash_borrowed + size_value - cash_used_new

        liq_price_new = average_entry_new * \
            (1 + (1/leverage_new) - static_variables.mmr)  # math checked

    # Create take profits if requested
    if not np.isnan(entry_order.risk_rewards):
        if np.isfinite(sl_prices_new):
            sl_or_tsl_prices = sl_prices_new
        elif np.isfinite(tsl_prices_new):
            sl_or_tsl_prices = tsl_prices_new

        coin_size = size_value / average_entry_new

        loss_no_fees = coin_size * (average_entry_new - sl_or_tsl_prices)

        fee_open = coin_size * average_entry_new * static_variables.fee_pct

        fee_close = coin_size * sl_or_tsl_prices * static_variables.fee_pct

        loss = loss_no_fees - fee_open - fee_close

        profit = -loss * entry_order.risk_rewards

        tp_prices_new = -((profit - size_value + size_value * static_variables.fee_pct) *
                          (average_entry_new/(size_value + size_value * static_variables.fee_pct)))  # math checked

        tp_pcts_new = (average_entry_new - tp_prices_new) / \
            average_entry_new  # math checked

    elif not np.isnan(tp_pcts_new):
        tp_prices_new = average_entry_new - \
            average_entry_new * tp_pcts_new  # math checked

    else:
        tp_pcts_new = np.nan
        tp_prices_new = np.nan

    # Checking if we ran out of free cash or gone over our max risk amount
    if available_balance_new < 0:
        raise RejectedOrderError("long increase - avaialbe balance < 0")

    return \
        AccountState(
            available_balance=available_balance_new,
            cash_borrowed=cash_borrowed_new,
            cash_used=cash_used_new,
            equity=account_state.equity,
        ), \
        OrderResult(
            average_entry=average_entry_new,
            fees_paid=np.nan,
            leverage=leverage_new,
            liq_price=liq_price_new,
            moved_sl_to_be=False,
            order_status=OrderStatus.Filled,
            order_status_info=OrderStatusInfo.HopefullyNoProblems,
            order_type=entry_order.order_type,
            pct_chg_trade=np.nan,
            position=position_new,
            price=price,
            realized_pnl=np.nan,
            size_value=size_value,
            sl_pcts=sl_pcts_new,
            sl_prices=sl_prices_new,
            tp_pcts=tp_pcts_new,
            tp_prices=tp_prices_new,
            tsl_pcts_init=tsl_pcts_init_new,
            tsl_prices=tsl_prices_new,
        )


@ njit(cache=True)
def short_decrease_nb(
    fee_pct: float,

    order_result: OrderResult,
    account_state: AccountState,
):
    """
    This is where the long position gets decreased or closed out.
    """

    if order_result.size_value >= order_result.position:
        size_value = order_result.position
    else:
        size_value = order_result.size_value

    pct_chg_trade = (order_result.average_entry - order_result.price) / \
        order_result.average_entry  # math checked

    # Set new order_result.position size_value and cash borrowed and cash used
    position_new = order_result.position - size_value
    position_pct_chg = (order_result.position - position_new) / \
        order_result.position  # math checked

    # profit and loss calulation
    coin_size = size_value / order_result.average_entry  # math checked
    pnl = coin_size * (order_result.average_entry -
                       order_result.price)  # math checked
    fee_open = coin_size * order_result.average_entry * fee_pct   # math checked
    fee_close = coin_size * order_result.price * fee_pct   # math checked
    fees_paid = fee_open + fee_close  # math checked
    realized_pnl = pnl - fees_paid  # math checked

    # Setting new account_state.equity
    equity_new = account_state.equity + realized_pnl

    cash_borrowed_new = account_state.cash_borrowed - \
        (account_state.cash_borrowed * position_pct_chg)

    cash_used_new = account_state.cash_used - \
        (account_state.cash_used * position_pct_chg)

    available_balance_new = realized_pnl + \
        account_state.available_balance + \
        (account_state.cash_used * position_pct_chg)

    return AccountState(
        available_balance=available_balance_new,
        cash_borrowed=cash_borrowed_new,
        cash_used=cash_used_new,
        equity=equity_new,
    ), \
        OrderResult(
        average_entry=order_result.average_entry,
        fees_paid=fees_paid,
        leverage=order_result.leverage,
        liq_price=order_result.liq_price,
        moved_sl_to_be=order_result.moved_sl_to_be,
        order_status=OrderStatus.Filled,
        order_status_info=OrderStatusInfo.HopefullyNoProblems,
        order_type=order_result.order_type,
        pct_chg_trade=pct_chg_trade,
        position=position_new,
        price=order_result.price,
        realized_pnl=realized_pnl,
        size_value=size_value,
        sl_pcts=order_result.sl_pcts,
        sl_prices=order_result.sl_prices,
        tp_pcts=order_result.tp_pcts,
        tp_prices=order_result.tp_prices,
        tsl_pcts_init=order_result.tsl_pcts_init,
        tsl_prices=order_result.tsl_prices,
    )