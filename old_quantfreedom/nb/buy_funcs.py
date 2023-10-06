import numpy as np
from numba import njit

from old_quantfreedom._typing import Tuple
from old_quantfreedom.enums.enums import (
    AccountState,
    CandleBody,
    LeverageMode,
    OrderResult,
    OrderSettings,
    OrderStatus,
    OrderStatusInfo,
    PriceArrayTuple,
    RejectedOrderError,
    SizeType,
    StaticVariables,
)


# Long order to enter or add to a long position
@njit(cache=True)
def long_increase_nb(
    bar: int,
    prices: PriceArrayTuple,
    account_state: AccountState,
    order_settings: OrderSettings,
    order_result: OrderResult,
    static_variables_tuple: StaticVariables,
) -> Tuple[AccountState, OrderResult]:
    # new cash borrowed needs to be returned
    available_balance_new = account_state.available_balance
    cash_used_new = account_state.cash_used
    leverage_new = order_settings.leverage
    average_entry_new = order_result.average_entry
    liq_price_new = order_result.liq_price
    position_old = order_result.position

    sl_pct_new = order_settings.sl_pct
    tp_pct_new = order_settings.tp_pct

    sl_price_new = np.nan
    tp_price_new = np.nan

    if (
        static_variables_tuple.size_type == SizeType.RiskAmount
        or static_variables_tuple.size_type == SizeType.RiskPercentOfAccount
    ):
        if np.isfinite(order_settings.sl_pct):
            sl_pct_new = order_settings.sl_pct
            if static_variables_tuple.size_type == SizeType.RiskPercentOfAccount:
                size_value = account_state.equity * order_settings.size_pct / sl_pct_new

            elif static_variables_tuple.size_type == SizeType.RiskAmount:
                size_value = order_settings.size_value / sl_pct_new
                if size_value < 1:
                    raise ValueError(
                        "Risk Amount has produced a size_value values less than 1."
                    )
            temp_sl_price = prices.entry - (prices.entry * sl_pct_new)
            possible_loss = size_value * sl_pct_new

            size_value = -possible_loss / (
                temp_sl_price / prices.entry
                - 1
                - static_variables_tuple.fee_pct
                - temp_sl_price * static_variables_tuple.fee_pct / prices.entry
            )

        elif np.isfinite(order_settings.sl_based_on):
            sl_based_on = order_settings.sl_based_on
            if sl_based_on == CandleBody.low:
                sl_price_new = prices.low.min() - (
                    prices.low.min() * order_settings.sl_based_on_add_pct
                )
            elif sl_based_on == CandleBody.close:
                sl_price_new = prices.close.min() - (
                    prices.close.min() * order_settings.sl_based_on_add_pct
                )
            elif sl_based_on == CandleBody.open:
                sl_price_new = prices.open.min() - (
                    prices.open.min() * order_settings.sl_based_on_add_pct
                )
            elif sl_based_on == CandleBody.high:
                sl_price_new = prices.high.min() - (
                    prices.high.min() * order_settings.sl_based_on_add_pct
                )

            if static_variables_tuple.size_type == SizeType.RiskPercentOfAccount:
                if position_old != 0:
                    possible_loss = -(  # total possible loss on second trade
                        (
                            (order_result.position / order_result.average_entry)
                            * (order_result.sl_price - order_result.average_entry)
                        )
                        - (
                            (order_result.position / order_result.average_entry)
                            * order_result.average_entry
                            * static_variables_tuple.fee_pct
                        )
                        - (
                            (order_result.position / order_result.average_entry)
                            * order_result.sl_price
                            * static_variables_tuple.fee_pct
                        )
                        + -(account_state.equity * order_settings.size_pct)
                    )

                    size_value = (
                        -possible_loss * prices.entry * order_result.average_entry
                        + prices.entry
                        * order_result.position
                        * order_result.average_entry
                        - sl_price_new * prices.entry * order_result.position
                        + sl_price_new
                        * prices.entry
                        * order_result.position
                        * static_variables_tuple.fee_pct
                        + prices.entry
                        * order_result.position
                        * order_result.average_entry
                        * static_variables_tuple.fee_pct
                    ) / (
                        order_result.average_entry
                        * (
                            prices.entry
                            - sl_price_new
                            + prices.entry * static_variables_tuple.fee_pct
                            + sl_price_new * static_variables_tuple.fee_pct
                        )
                    )
                    if size_value < 1:
                        return account_state, OrderResult(
                            average_entry=order_result.average_entry,
                            fees_paid=np.nan,
                            leverage=order_result.leverage,
                            liq_price=order_result.liq_price,
                            moved_sl_to_be=order_result.moved_sl_to_be,
                            order_status=OrderStatus.Ignored,
                            order_status_info=OrderStatusInfo.RiskToBig,
                            order_type=static_variables_tuple.order_type,
                            pct_chg_trade=np.nan,
                            position=order_result.position,
                            price=prices.entry,
                            realized_pnl=np.nan,
                            size_value=np.nan,
                            sl_pct=order_result.sl_pct,
                            sl_price=order_result.sl_price,
                            tp_pct=order_result.tp_pct,
                            tp_price=order_result.tp_price,
                        )
                    # don't think i need this becuase it happens again later on in the code and this postion size and average entry has nothing to do with what is needed in this if
                    # position_new = position_old + size_value
                    # average_entry_new = (size_value + position_old) / (
                    #     (size_value / prices.entry) + (position_old / average_entry_new)
                    # )
                    # sl_pct_new = (average_entry_new - sl_price_new) / average_entry_new
                else:
                    sl_pct_new = (prices.entry - sl_price_new) / prices.entry
                    size_value = (
                        account_state.equity * order_settings.size_pct / sl_pct_new
                    )
                    possible_loss = size_value * sl_pct_new

                    size_value = -possible_loss / (
                        sl_price_new / prices.entry
                        - 1
                        - static_variables_tuple.fee_pct
                        - sl_price_new * static_variables_tuple.fee_pct / prices.entry
                    )

    elif static_variables_tuple.size_type == SizeType.Amount:
        size_value = order_settings.size_value
        if size_value > static_variables_tuple.max_order_size_value:
            size_value = static_variables_tuple.max_order_size_value
        elif size_value == np.inf:
            size_value = order_result.position

    # getting size_value for percent of account
    elif static_variables_tuple.size_type == SizeType.PercentOfAccount:
        size_value = account_state.equity * order_settings.size_pct  # math checked

    else:
        raise TypeError(
            "I have no clue what is wrong but something is wrong with making the size_value using size_value type"
        )

    if (
        size_value < 1
        or size_value > static_variables_tuple.max_order_size_value
        or size_value < static_variables_tuple.min_order_size_value
    ):
        raise RejectedOrderError(
            "Long Increase - Size Value is either to big or too small"
        )

    # Get average Entry
    if position_old != 0.0:
        average_entry_new = (size_value + position_old) / (
            (size_value / prices.entry) + (position_old / average_entry_new)
        )
    else:
        average_entry_new = prices.entry

    # setting new position_new
    position_new = position_old + size_value

    # Create stop loss prices if requested
    if not np.isnan(sl_pct_new):
        sl_price_new = average_entry_new - (
            average_entry_new * sl_pct_new
        )  # math checked
    else:
        sl_price_new = np.nan
        sl_pct_new = np.nan

    # Risk % check
    # checking if there is some sort of stop loss
    is_stop_loss = not np.isnan(sl_price_new) or not np.isnan(liq_price_new)

    # checking if there is some sort max equity
    is_max_risk = not np.isnan(order_settings.max_equity_risk_pct) or not np.isnan(
        order_settings.max_equity_risk_value
    )

    if is_stop_loss and is_max_risk:
        # store temp sl prices.entry
        if not np.isnan(sl_price_new):
            temp_price = sl_price_new
        elif not np.isnan(liq_price_new):
            temp_price = liq_price_new

        # calc possible loss
        coin_size = position_new / average_entry_new  # math checked
        pnl_no_fees = coin_size * (temp_price - average_entry_new)  # math checked
        open_fee = (
            coin_size * average_entry_new * static_variables_tuple.fee_pct
        )  # math checked
        close_fee = (
            coin_size * temp_price * static_variables_tuple.fee_pct
        )  # math checked
        possible_loss = -(pnl_no_fees - open_fee - close_fee)  # math checked
        possible_loss = float(int(possible_loss))

        # getting account risk amount
        if not np.isnan(order_settings.max_equity_risk_pct):
            account_risk_amount = float(
                int(account_state.equity * order_settings.max_equity_risk_pct)
            )
        elif not np.isnan(order_settings.max_equity_risk_value):
            account_risk_amount = order_settings.max_equity_risk_value

        # check if our possible loss is more than what we are willing to risk of our account
        if 0 < possible_loss > account_risk_amount:
            return account_state, OrderResult(
                average_entry=order_result.average_entry,
                fees_paid=np.nan,
                leverage=order_result.leverage,
                liq_price=order_result.liq_price,
                moved_sl_to_be=order_result.moved_sl_to_be,
                order_status=OrderStatus.Ignored,
                order_status_info=OrderStatusInfo.MaxEquityRisk,
                order_type=static_variables_tuple.order_type,
                pct_chg_trade=np.nan,
                position=order_result.position,
                price=prices.entry,
                realized_pnl=np.nan,
                size_value=np.nan,
                sl_pct=order_result.sl_pct,
                sl_price=order_result.sl_price,
                tp_pct=order_result.tp_pct,
                tp_price=order_result.tp_price,
            )

    # check if leverage_new amount is possible with size_value and free cash
    if static_variables_tuple.lev_mode == LeverageMode.LeastFreeCashUsed:
        leverage_new = -average_entry_new / (
            (sl_price_new - sl_price_new * 0.001)
            - average_entry_new  # TODO .2 is percent padding user wants
            - static_variables_tuple.mmr_pct * average_entry_new
        )  # math checked
    if leverage_new > static_variables_tuple.max_lev:
        leverage_new = static_variables_tuple.max_lev
    elif leverage_new < 1:
        leverage_new = 1

    # Getting Order Cost
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
    initial_margin = size_value / leverage_new
    fee_to_open = size_value * static_variables_tuple.fee_pct  # math checked
    possible_bankruptcy_fee = (
        size_value * (leverage_new - 1) / leverage_new * static_variables_tuple.fee_pct
    )
    cash_used_new = (
        initial_margin + fee_to_open + possible_bankruptcy_fee
    )  # math checked

    if cash_used_new > available_balance_new * leverage_new:
        raise RejectedOrderError(
            "long inrease iso lev - cash used greater than available balance * lev ... size_value is too big"
        )

    elif cash_used_new > available_balance_new:
        raise RejectedOrderError(
            "long inrease iso lev - cash used greater than available balance ... maybe increase lev"
        )

    else:
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        available_balance_new = available_balance_new - cash_used_new
        cash_used_new = account_state.cash_used + cash_used_new
        cash_borrowed_new = account_state.cash_borrowed + size_value - cash_used_new

        liq_price_new = average_entry_new * (
            1 - (1 / leverage_new) + static_variables_tuple.mmr_pct
        )  # math checked

    # Create take profits if requested
    if not np.isnan(order_settings.risk_reward):
        coin_size = size_value / average_entry_new

        loss_no_fees = coin_size * (sl_price_new - average_entry_new)

        fee_open = coin_size * average_entry_new * static_variables_tuple.fee_pct

        fee_close = coin_size * sl_price_new * static_variables_tuple.fee_pct

        loss = loss_no_fees - fee_open - fee_close

        profit = -loss * order_settings.risk_reward

        tp_price_new = (
            profit + size_value * static_variables_tuple.fee_pct + size_value
        ) * (
            average_entry_new
            / (size_value - size_value * static_variables_tuple.fee_pct)
        )  # math checked

        tp_pct_new = (
            tp_price_new - average_entry_new
        ) / average_entry_new  # math checked

    elif not np.isnan(tp_pct_new):
        tp_price_new = average_entry_new + (
            average_entry_new * tp_pct_new
        )  # math checked

    else:
        tp_pct_new = np.nan
        tp_price_new = np.nan

    # Checking if we ran out of free cash or gone over our max risk amount
    if available_balance_new < 0:
        raise RejectedOrderError("long increase - avaialbe balance < 0")

    return AccountState(
        available_balance=available_balance_new,
        cash_borrowed=cash_borrowed_new,
        cash_used=cash_used_new,
        equity=account_state.equity,
    ), OrderResult(
        average_entry=average_entry_new,
        fees_paid=np.nan,
        leverage=leverage_new,
        liq_price=liq_price_new,
        moved_sl_to_be=False,
        order_status=OrderStatus.Filled,
        order_status_info=OrderStatusInfo.HopefullyNoProblems,
        order_type=static_variables_tuple.order_type,
        pct_chg_trade=np.nan,
        position=position_new,
        price=prices.entry,
        realized_pnl=np.nan,
        size_value=size_value,
        sl_pct=sl_pct_new,
        sl_price=sl_price_new,
        tp_pct=tp_pct_new,
        tp_price=tp_price_new,
    )


@njit(cache=True)
def long_decrease_nb(
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

    pct_chg_trade = (
        order_result.price - order_result.average_entry
    ) / order_result.average_entry  # math checked

    # Set new order_result.position size_value and cash borrowed and cash used
    position_new = order_result.position - size_value
    position_pct_chg = (
        order_result.position - position_new
    ) / order_result.position  # math checked

    # profit and loss calulation
    coin_size = size_value / order_result.average_entry  # math checked
    pnl = coin_size * (order_result.price - order_result.average_entry)  # math checked
    fee_open = coin_size * order_result.average_entry * fee_pct  # math checked
    fee_close = coin_size * order_result.price * fee_pct  # math checked
    fees_paid = fee_open + fee_close  # math checked
    realized_pnl = pnl - fees_paid  # math checked

    # Setting new account_state.equity
    equity_new = account_state.equity + realized_pnl

    cash_borrowed_new = account_state.cash_borrowed - (
        account_state.cash_borrowed * position_pct_chg
    )

    cash_used_new = account_state.cash_used - (
        account_state.cash_used * position_pct_chg
    )

    available_balance_new = (
        realized_pnl
        + account_state.available_balance
        + (account_state.cash_used * position_pct_chg)
    )

    return AccountState(
        available_balance=available_balance_new,
        cash_borrowed=cash_borrowed_new,
        cash_used=cash_used_new,
        equity=equity_new,
    ), OrderResult(
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
        sl_pct=order_result.sl_pct,
        sl_price=order_result.sl_price,
        tp_pct=order_result.tp_pct,
        tp_price=order_result.tp_price,
    )
