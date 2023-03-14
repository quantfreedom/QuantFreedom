"""
Testing the tester
"""

import numpy as np
from numba import njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.nb.buy_funcs import long_increase_nb, long_decrease_nb
from quantfreedom.backtester.nb.helper_funcs import fill_log_records_nb, fill_order_records_nb
from quantfreedom.backtester.enums.enums import (
    OrderType,
    SL_BE_andTrailBasedOn,
    TestTuple,
    RejectedOrderError,
    LeverageMode,
    SizeType,
    OrderStatus
)


@ njit(cache=True)
def check_sl_tp_nb(
    average_entry: float,
    high_price: float,
    low_price: float,
    open_price: float,
    close_price: float,
    fee_pct: float,
    order_type: int,
    sl_prices: float,
    tsl_prices: float,
    liq_price: float,
    tp_prices: float,
    want_to_record_stops_log: bool,

    moved_sl_to_be: bool,
    sl_to_be: bool,
    sl_to_be_based_on: float,
    sl_to_be_when_pct_from_avg_entry: float,
    sl_to_be_zero_or_entry: float,

    moved_tsl: bool,
    tsl_based_on: float,
    tsl_true_or_false: bool,
    tsl_when_pct_from_avg_entry: float,
    tsl_trail_by: float,

    bar: tp.Optional[int] = None,
    col: tp.Optional[int] = None,
    log_count_id: tp.Optional[int] = None,
    log_records: tp.Optional[tp.RecordArray] = None,
    log_records_filled: tp.Optional[int] = None,
    order_count_id: tp.Optional[int] = None,
) -> TestTuple:
    """
    This checks if your stop or take profit was hit.

    Args:
        high_price: The high_price of the candle
        low_price: The low_price of the candle
        order_result: See [Order Result][backtester.enums.enums.ResultEverything].

    !!! note
        Right now it only fully closes the position. But that will be changing soon once multiple stops is implimented.

    First it checks the order type and then it checks if the stop losses were hit and then checks to see if take profit was hit last.
    It defaults to checking tp last so it has a negative bias.
    """
    log_count_id_new = log_count_id
    log_records_filled_new = log_records_filled
    size_value = np.inf
    record_log_sl_moved = False

    # checking if we are in a long
    if order_type == OrderType.LongEntry:
        # Regular Stop Loss
        if low_price <= sl_prices:
            price = sl_prices
            order_type = OrderType.LongSL
        # Trailing Stop Loss
        elif low_price <= tsl_prices:
            price = tsl_prices
            order_type = OrderType.LongTSL
        # Liquidation
        elif low_price <= liq_price:
            price = liq_price
            order_type = OrderType.LongLiq
        # Take Profit
        elif high_price >= tp_prices:
            price = tp_prices
            order_type = OrderType.LongTP

        # Stop Loss to break even
        elif not moved_sl_to_be and sl_to_be:
            if sl_to_be_based_on == SL_BE_andTrailBasedOn.low_price:
                sl_to_be_based_on = low_price
            elif sl_to_be_based_on == SL_BE_andTrailBasedOn.high_price:
                sl_to_be_based_on = high_price
            elif sl_to_be_based_on == SL_BE_andTrailBasedOn.open_price:
                sl_to_be_based_on = open_price
            elif sl_to_be_based_on == SL_BE_andTrailBasedOn.close_price:
                sl_to_be_based_on = close_price

            if (sl_to_be_based_on - average_entry) / average_entry > sl_to_be_when_pct_from_avg_entry:
                if sl_to_be_zero_or_entry == 0:
                    sl_prices = (
                        fee_pct * average_entry + average_entry
                    ) / (1 - fee_pct)
                else:
                    sl_prices = average_entry
                moved_sl_to_be = True
                record_log_sl_moved = True
            order_type = OrderType.MovedSLtoBE
            price = np.nan
            size_value = np.nan

        # Trailing Stop Loss
        elif tsl_true_or_false:
            if tsl_based_on == SL_BE_andTrailBasedOn.low_price:
                tsl_based_on = low_price
            elif tsl_based_on == SL_BE_andTrailBasedOn.high_price:
                tsl_based_on = high_price
            elif tsl_based_on == SL_BE_andTrailBasedOn.open_price:
                tsl_based_on = open_price
            elif tsl_based_on == SL_BE_andTrailBasedOn.close_price:
                tsl_based_on = close_price

            # not going to adjust every candle
            if (tsl_based_on - average_entry) / average_entry > tsl_when_pct_from_avg_entry:
                temp_tsl_price = tsl_based_on - tsl_based_on * tsl_trail_by
                if temp_tsl_price > tsl_prices:
                    tsl_prices = temp_tsl_price
                    moved_tsl = True
                    record_log_sl_moved = True
                    order_type = OrderType.MovedTSL
            price = np.nan
            size_value = np.nan
        else:
            price = np.nan
            size_value = np.nan

    # Checking if we are a short entry
    elif order_type == OrderType.ShortEntry:
        # Stop Loss
        if high_price >= sl_prices:
            price = sl_prices
            order_type = OrderType.ShortSL
        # Trailing Stop Loss
        elif high_price >= tsl_prices:
            price = tsl_prices
            order_type = OrderType.ShortTSL
        # Liquidation
        elif high_price >= liq_price:
            price = liq_price
            order_type = OrderType.ShortLiq
        # Take Profit
        elif low_price <= tp_prices:
            price = tp_prices
            order_type = OrderType.ShortTP
        else:
            order_type = OrderType.ShortEntry
            price = np.nan
            size_value = np.nan
    else:
        raise RejectedOrderError(
            "Check SL TP: Something is wrong checking sl tsl tp")
    # create the order

    record_logs = (
        bar != None and
        col != None and
        log_count_id != None and
        log_records != None and
        log_records_filled != None and
        order_count_id != None
    )
    if want_to_record_stops_log:
        if record_log_sl_moved:
            if record_logs:
                fill_log_records_nb(
                    average_entry=average_entry,
                    bar=bar,
                    col=col,
                    log_count_id=log_count_id,
                    log_records=log_records,
                    order_count_id=order_count_id,
                    order_type=order_type,
                    price=np.nan,
                    realized_pnl=np.nan,
                    sl_prices=sl_prices,
                    tsl_prices=tsl_prices,
                    tp_prices=tp_prices,
                )
                log_count_id_new += 1
                log_records_filled_new += 1
            else:
                raise RejectedOrderError(
                    "You forgot something to run logs in sl checker")

    return \
        log_count_id_new, \
        log_records_filled_new, \
        moved_sl_to_be, \
        moved_tsl, \
        order_type, \
        price, \
        size_value, \
        sl_prices, \
        tsl_prices


@ njit(cache=True)
def order_checker_nb(
    available_balance: float,
    equity: float,
    fee_pct: float,
    lev_mode: int,
    leverage: float,
    max_equity_risk_pct: float,
    max_equity_risk_value: float,
    max_lev: float,
    max_order_size_pct: float,
    max_order_size_value: float,
    min_order_size_pct: float,
    min_order_size_value: float,
    mmr: float,
    order_type: int,
    position: float,
    price: float,
    risk_rewards: float,
    size_pct: float,
    size_type: int,
    size_value: float,
    sl_be_then_trail: bool,
    sl_pcts: float,
    sl_prices: float,
    sl_to_be: bool,
    sl_to_be_zero_or_entry: float,
    slippage_pct: float,
    tp_pcts: float,
    tp_prices: float,
    tsl_based_on: float,
    tsl_pcts: float,
    tsl_prices: float,
):
    """
    This goes through and checks your order for all types of different value errors.

    Args:
        order: See [Order][backtester.enums.enums.OrderEverything].

        account_state: See [Account_State][backtester.enums.enums.AccountAndTradeState].

    It also sets the leverage and size for specific size_types

    !!! note
        All math is based on bybit pnl calculations and order cost and everything. You can see everything
        [here](https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_SubCategories?id=a005g000031FzWkAAK&language=en_US&subTopic=USDT_Perpetual_Contract)
    """

    ''' ############################## Account ############################## '''
    ''' ############################## Account ############################## '''
    ''' ############################## Account ############################## '''
    ''' ############################## Account ############################## '''

    # Lets see if you even have any money
    if available_balance < 0 or not np.isfinite(available_balance) or (
            not np.isfinite(equity)) or equity <= 0:
        raise ValueError("YOU HAVE NO MONEY!!!! You Broke!!!!")

    if not np.isfinite(fee_pct):
        raise ValueError("fee_pct must be finite")

    if not np.isfinite(mmr):
        raise ValueError("mmr must be finite")

    ''' ############################## Position ############################## '''
    ''' ############################## Position ############################## '''
    ''' ############################## Position ############################## '''
    ''' ############################## Position ############################## '''

    # Are we even in a position?
    if position < 0:
        raise RejectedOrderError("You aren't in a position")

    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''

    if not np.isnan(size_value) and size_value < 1:
        raise ValueError("size_value must be greater than 1.")

    if not np.isfinite(min_order_size_value) or min_order_size_value < 1:
        raise ValueError(
            "min_order_size_value must be finite or 0 or greater")

    if not np.isnan(size_value) and size_value < min_order_size_value:
        raise ValueError("size_value is less than min_order_size_value")

    if np.isnan(max_order_size_value) or max_order_size_value < 1:
        raise ValueError("max_order_size_value must be greater than 1")

    if not np.isnan(size_value) and size_value > max_order_size_value:
        raise ValueError("size_value is greater than max_order_size_value")

    ''' ############################## Order Size pct ############################## '''
    ''' ############################## Order Size pct ############################## '''
    ''' ############################## Order Size pct ############################## '''
    ''' ############################## Order Size pct ############################## '''

    if np.isinf(size_pct) or size_pct <= 0:
        raise ValueError("size_pct must not be inf or greater than 0.")

    if not np.isfinite(min_order_size_pct) or min_order_size_pct < 0:
        raise ValueError(
            "min_order_size_pct must be finite or greater than zero")

    if size_pct < min_order_size_pct:
        raise ValueError("size_pct is less than min_order_size_pct")

    if np.isnan(max_order_size_pct) or max_order_size_pct < 0:
        raise ValueError("max_order_size_pct must be greater than 0")

    if size_pct > max_order_size_pct:
        raise ValueError("size_pct is greater than max_order_size_pct")

    ''' ############################## price ############################## '''
    ''' ############################## price ############################## '''
    ''' ############################## price ############################## '''
    ''' ############################## price ############################## '''

    if np.isinf(price) or price <= 0:
        raise ValueError("price must be np.nan or greater than 0")

    if np.isinf(slippage_pct) or slippage_pct < 0:
        raise ValueError(
            "slippage_pct must be np.nan or greater than zero")
    elif not np.isnan(slippage_pct):
        price = price * (1.0 + slippage_pct)

    ''' ############################## Stops ############################## '''
    ''' ############################## Stops ############################## '''
    ''' ############################## Stops ############################## '''
    ''' ############################## Stops ############################## '''

    if np.isinf(sl_pcts) or sl_pcts < 0:
        raise ValueError(
            "sl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(sl_prices) or sl_prices < 0:
        raise ValueError(
            "sl_prices has to be nan or greater than 0 and not inf")

    if np.isinf(tsl_pcts) or tsl_pcts < 0:
        raise ValueError(
            "tsl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(tsl_prices) or tsl_prices < 0:
        raise ValueError(
            "tsl_prices has to be nan or greater than 0 and not inf")

    if np.isinf(tp_pcts) or tp_pcts < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(tp_prices) or tp_prices < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    check_sl_tsl_for_nan = (
        np.isnan(sl_pcts) and np.isnan(sl_prices) and (
            np.isnan(tsl_pcts) and np.isnan(tsl_prices)))

    ''' ############################## Leverage ############################## '''
    ''' ############################## Leverage ############################## '''
    ''' ############################## Leverage ############################## '''
    ''' ############################## Leverage ############################## '''

    # checking if leverage mode is out of range
    if (0 > lev_mode > len(LeverageMode)) or np.isinf(lev_mode):
        raise ValueError("Leverage mode is out of range or inf")

    # if leverage is too big or too small
    if lev_mode == LeverageMode.Isolated:
        if not np.isfinite(leverage) or 1 > leverage > max_lev:
            raise ValueError("Leverage needs to be between 1 and max lev")

    # checking to make sure you have a sl or tsl with least free cash used
    elif lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise RejectedOrderError(
                "When using Least Free Cash Used set a proper sl or tsl > 0")
        else:
            leverage = np.nan
    else:
        leverage = np.nan

    ''' ############################## Risk Reward ############################## '''
    ''' ############################## Risk Reward ############################## '''
    ''' ############################## Risk Reward ############################## '''
    ''' ############################## Risk Reward ############################## '''

    # making sure we have a number greater than 0 for rr
    if np.isinf(risk_rewards) or risk_rewards < 0:
        raise ValueError(
            "Risk Rewards has to be greater than 0 or np.nan")

    # check if RR has sl pct / price or tsl pct / price
    elif not np.isnan(risk_rewards) and check_sl_tsl_for_nan:
        raise RejectedOrderError(
            "When risk to reward is set you have to have a sl or tsl > 0")

    elif risk_rewards > 0 and (tp_pcts > 0 or tp_prices > 0):
        raise RejectedOrderError(
            "You can't have take profits set when using Risk to reward")

    ''' ############################## Max Risk ############################## '''
    ''' ############################## Max Risk ############################## '''
    ''' ############################## Max Risk ############################## '''
    ''' ############################## Max Risk ############################## '''

    if np.isinf(max_equity_risk_pct) or max_equity_risk_pct < 0:
        raise ValueError(
            "Max equity risk percent has to be greater than 0 or np.nan")
    elif np.isinf(max_equity_risk_value) or max_equity_risk_value < 0:
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    ''' ############################## Two conflicting settings ############################## '''
    ''' ############################## Two conflicting settings ############################## '''
    ''' ############################## Two conflicting settings ############################## '''
    ''' ############################## Two conflicting settings ############################## '''

    if not np.isnan(max_equity_risk_pct) and not np.isnan(max_equity_risk_value):
        raise ValueError(
            "You can't have max risk pct and max risk both set at the same time.")
    elif not np.isnan(sl_pcts) and not np.isnan(sl_prices):
        raise ValueError(
            "You can't have sl pct and sl price both set at the same time.")
    elif not np.isnan(tsl_pcts) and not np.isnan(tsl_prices):
        raise ValueError(
            "You can't have tsl pct and tsl price both set at the same time.")
    elif not np.isnan(tp_pcts) and not np.isnan(tp_prices):
        raise ValueError(
            "You can't have tp pct and tp price both set at the same time.")
    elif not np.isnan(size_value) and not np.isnan(size_pct):
        raise ValueError(
            "You can't have size and size pct set at the same time.")

    ''' ############################## Setting Order Size or pct size Type ############################## '''
    ''' ############################## Setting Order Size or pct size Type ############################## '''
    ''' ############################## Setting Order Size or pct size Type ############################## '''
    ''' ############################## Setting Order Size or pct size Type ############################## '''

    # simple check if order size type is valid
    if 0 > order_type > len(OrderType) or not np.isfinite(order_type):
        raise ValueError("order_type is invalid")

    # Getting the right size for Size Type Amount
    if size_type == SizeType.Amount:
        if size_value < 1 or np.isnan(size_value):
            raise ValueError(
                "With SizeType as amount, size_value must be 1 or greater.")
        elif size_value > max_order_size_value:
            size_value = max_order_size_value
        elif size_value == np.inf:
            size_value = position

    # getting size for percent of account
    elif size_type == SizeType.PercentOfAccount:
        if np.isnan(size_pct):
            raise ValueError(
                "You need size_pct to be > 0 if using percent of account.")
        else:
            size_value = equity * size_pct  # math checked

    # checking to see if you set a stop loss for risk based size types
    elif size_type == SizeType.RiskAmount or (
            size_type == SizeType.RiskPercentOfAccount) and check_sl_tsl_for_nan:
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl or tsl > 0")

    # setting risk amount size
    elif np.isfinite(sl_pcts) or np.isfinite(tsl_pcts):
        if np.isfinite(sl_pcts):
            sl_or_tsl_pcts = sl_pcts
        else:
            sl_or_tsl_pcts = tsl_pcts
        if size_type == SizeType.RiskAmount:
            size_value = size_value / sl_or_tsl_pcts
            if size_value < 1:
                raise ValueError(
                    "Risk Amount has produced a size values less than 1.")

        # setting risk percent size
        elif size_type == SizeType.RiskPercentOfAccount:
            if np.isnan(size_pct):
                raise ValueError(
                    "You need size_pct to be > 0 if using risk percent of account.")
            # TODO need to check for avg entry for multiple sl and also check to see if it is a tsl
            else:
                # get size of account at risk 100 / .01 = 1
                account_at_risk = equity * size_pct
                # get size needed to risk account at risk 1 / .01 = 100
                size_value = account_at_risk / sl_or_tsl_pcts
        else:
            raise TypeError(
                "I have no clue what is wrong but something is wrong with making the size using size type")

    # create the right size_value if there is a sl pct or price
    is_entry_not_amount = (order_type == OrderType.LongEntry or
                           order_type == OrderType.ShortEntry) and \
        size_type != SizeType.Amount

    if np.isfinite(sl_pcts) and is_entry_not_amount:
        sl_prices = price - (price * sl_pcts)
        possible_loss = size_value * (sl_pcts)

        size_value = -possible_loss / (((sl_prices/price) - 1) - (fee_pct) -
                                       ((sl_prices * (fee_pct))/price))

    elif np.isfinite(sl_prices) and is_entry_not_amount:
        sl_prices = sl_prices
        sl_pcts = abs((price - sl_prices) / price) * 100
        possible_loss = size_value * (sl_pcts)

        size_value = -possible_loss / (((sl_prices/price) - 1) - (fee_pct) -
                                       ((sl_prices * (fee_pct))/price))
    elif np.isfinite(tsl_pcts) and is_entry_not_amount:
        tsl_prices = price - (price * tsl_pcts)
        possible_loss = size_value * (tsl_pcts)

        size_value = -possible_loss / (((tsl_prices/price) - 1) - (fee_pct) -
                                       ((tsl_prices * (fee_pct))/price))

    elif np.isfinite(tsl_prices) and is_entry_not_amount:
        tsl_prices = tsl_prices
        tsl_pcts = abs((price - tsl_prices) / price) * 100
        possible_loss = size_value * (tsl_pcts)

        size_value = -possible_loss / (((tsl_prices/price) - 1) - (fee_pct) -
                                       ((tsl_prices * (fee_pct))/price))

    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''
    ''' ############################## Order Size ############################## '''

    if size_value < 1:
        raise ValueError("size_value must be greater than 1.")

    if size_value < min_order_size_value:
        raise ValueError("size_value is less than min order size")

    if size_value > max_order_size_value:
        raise ValueError("size_value is greater than max order size")

    return \
        leverage, \
        price, \
        size_value


@ njit(cache=True)
def process_order_nb(
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    equity: float,
    fee_pct: float,
    lev_mode: int,
    leverage: float,
    liq_price: float,
    max_equity_risk_pct: float,
    max_equity_risk_value: float,
    max_lev: float,
    max_order_size_pct: float,
    max_order_size_value: float,
    min_order_size_pct: float,
    min_order_size_value: float,
    mmr: float,
    order_type: int,
    position: float,
    price: float,
    risk_rewards: float,
    size_pct: float,
    size_type: int,
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
    tsl_based_on: float,
    moved_sl_to_be: bool,
    moved_tsl: bool,

    sl_pcts_order_result: float,
    sl_prices_order_result: float,
    tp_pcts_order_result: float,
    tp_prices_order_result: float,
    tsl_pcts_order_result: float,
    tsl_prices_order_result: float,

    bar: int,
    col: int,
    indicator_settings_counter: int,
    order_settings_counter: int,

    order_records_filled: int,
    order_count_id: int,
    order_records: tp.RecordArray,

    group: int = 0,

    log_count_id: tp.Optional[int] = None,
    log_records: tp.Optional[tp.RecordArray] = None,
    log_records_filled: tp.Optional[int] = None,
) -> tp.Tuple[TestTuple]:

    average_entry_new = average_entry
    price_new = price
    order_count_id_new = order_count_id
    order_records_filled_new = order_records_filled
    log_count_id_new = log_count_id
    log_records_filled_new = log_records_filled

    # Check the order for errors and other things
    if order_type == OrderType.LongEntry:
        # TODO why am i sending size_pct back
        leverage_new, \
            price_new, \
            size_value_new, \
            = order_checker_nb(
                available_balance=available_balance,
                equity=equity,
                fee_pct=fee_pct,
                lev_mode=lev_mode,
                leverage=leverage,
                max_equity_risk_pct=max_equity_risk_pct,
                max_equity_risk_value=max_equity_risk_value,
                max_lev=max_lev,
                max_order_size_pct=max_order_size_pct,
                max_order_size_value=max_order_size_value,
                min_order_size_pct=min_order_size_pct,
                min_order_size_value=min_order_size_value,
                mmr=mmr,
                order_type=order_type,
                position=position,
                price=price,
                risk_rewards=risk_rewards,
                size_value=size_value,
                size_pct=size_pct,
                size_type=size_type,
                sl_be_then_trail=sl_be_then_trail,
                sl_pcts=sl_pcts,
                sl_prices=sl_prices,
                sl_to_be=sl_to_be,
                sl_to_be_zero_or_entry=sl_to_be_zero_or_entry,
                slippage_pct=slippage_pct,
                tp_pcts=tp_pcts,
                tp_prices=tp_prices,
                tsl_based_on=tsl_based_on,
                tsl_pcts=tsl_pcts,
                tsl_prices=tsl_prices,
            )
        available_balance_new, \
            average_entry_new, \
            cash_borrowed_new, \
            cash_used_new, \
            leverage_new, \
            liq_price_new, \
            order_status, \
            order_status_info, \
            position_new, \
            sl_pcts_new, \
            sl_prices_new, \
            tp_pcts_new, \
            tp_prices_new, \
            tsl_pcts_new, \
            tsl_prices_new, \
            = long_increase_nb(
                available_balance=available_balance,
                average_entry=average_entry,
                cash_borrowed=cash_borrowed,
                cash_used=cash_used,
                equity=equity,
                fee_pct=fee_pct,
                lev_mode=lev_mode,
                leverage=leverage_new,
                liq_price=liq_price,
                max_equity_risk_pct=max_equity_risk_pct,
                max_equity_risk_value=max_equity_risk_value,
                max_lev=max_lev,
                mmr=mmr,
                position=position,
                price=price_new,
                risk_rewards=risk_rewards,
                size_value=size_value_new,
                slippage_pct=slippage_pct,

                sl_pcts=sl_pcts,
                sl_prices=sl_prices,
                tp_pcts=tp_pcts,
                tp_prices=tp_prices,
                tsl_pcts=tsl_pcts,
                tsl_prices=tsl_prices,

                sl_be_then_trail=sl_be_then_trail,
                sl_to_be=sl_to_be,
                sl_to_be_zero_or_entry=sl_to_be_zero_or_entry,

                sl_pcts_order_result=sl_pcts_order_result,
                sl_prices_order_result=sl_prices_order_result,
                tp_pcts_order_result=tp_pcts_order_result,
                tp_prices_order_result=tp_prices_order_result,
                tsl_pcts_order_result=tsl_pcts_order_result,
                tsl_prices_order_result=tsl_prices_order_result,
            )

    elif OrderType.LongLiq <= order_type <= OrderType.LongTSL:
        available_balance_new, \
            cash_borrowed_new, \
            cash_used_new, \
            equity_new, \
            fees_paid, \
            liq_price, \
            order_status_info, \
            order_status, \
            position_new, \
            realized_pnl, \
            size_value, \
            = long_decrease_nb(
                available_balance=available_balance,
                average_entry=average_entry,
                cash_borrowed=cash_borrowed,
                cash_used=cash_used,
                equity=equity,
                fee_pct=fee_pct,
                liq_price=liq_price,
                position=position,
                price=price,
                size_value=size_value,
            )

    if order_status == OrderStatus.Filled:
        fill_order_records_nb(
            average_entry=average_entry_new,
            bar=bar,
            col=col,
            equity=equity,
            fees_paid=0.,
            indicator_settings_counter=indicator_settings_counter,
            max_equity_risk_pct=max_equity_risk_pct,
            order_count_id=order_count_id,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_type=order_type,
            price=price_new,
            realized_pnl=np.nan,
            risk_rewards=risk_rewards,
            size_value=size_value_new,
            sl_pcts=sl_pcts_new,
        )
        order_count_id_new += 1
        order_records_filled_new += 1
        moved_sl_to_be = False
        moved_tsl = False

    if log_count_id != None:
        if order_status == OrderStatus.Filled:
            fill_log_records_nb(
                average_entry=average_entry_new,
                bar=bar,
                col=col,
                log_count_id=log_count_id,
                log_records=log_records,
                order_count_id=order_count_id,
                order_type=order_type,
                price=price_new,
                realized_pnl=np.nan,
                sl_prices=sl_prices_new,
                tsl_prices=tsl_prices_new,
                tp_prices=tp_prices_new,
            )
            log_count_id_new += 1
            log_records_filled_new += 1

    return \
        available_balance_new, \
        average_entry_new, \
        cash_borrowed_new, \
        cash_used_new, \
        leverage_new, \
        liq_price_new, \
        log_count_id_new, \
        log_records_filled_new, \
        moved_sl_to_be, \
        moved_tsl, \
        order_count_id_new, \
        order_records_filled_new, \
        order_status_info, \
        order_status, \
        position_new, \
        sl_pcts_new, \
        sl_prices_new, \
        tp_pcts_new, \
        tp_prices_new, \
        tsl_pcts_new, \
        tsl_prices_new


@ njit(cache=True)
def process_stops_nb(
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    equity: float,
    fee_pct: float,
    liq_price: int,
    max_equity_risk_pct: float,
    order_type: int,
    position: float,
    price: float,
    risk_rewards: float,
    size_value: float,
    sl_pcts: float,
    sl_prices: float,
    tp_prices: float,
    tsl_prices: float,

    bar: int,
    col: int,
    indicator_settings_counter: int,
    order_settings_counter: int,

    order_count_id: int,
    order_records_filled: int,
    order_records: tp.RecordArray,

    group: int = 0,
    log_count_id: tp.Optional[int] = None,
    log_records_filled: tp.Optional[int] = None,
    log_records: tp.Optional[tp.RecordArray] = None,
) -> tp.Tuple[TestTuple]:

    order_count_id_new = order_count_id
    order_records_filled_new = order_records_filled
    log_count_id_new = log_count_id
    log_records_filled_new = log_records_filled

    if OrderType.LongLiq <= order_type <= OrderType.LongTSL:
        available_balance_new, \
            cash_borrowed_new, \
            cash_used_new, \
            equity_new, \
            fees_paid, \
            liq_price, \
            order_status_info, \
            order_status, \
            position_new, \
            realized_pnl, \
            size_value, \
            = long_decrease_nb(
                available_balance=available_balance,
                average_entry=average_entry,
                cash_borrowed=cash_borrowed,
                cash_used=cash_used,
                equity=equity,
                fee_pct=fee_pct,
                liq_price=liq_price,
                position=position,
                price=price,
                size_value=size_value,
            )

    # Start the order filling process
    if order_status == OrderStatus.Filled:
        fill_order_records_nb(
            average_entry=average_entry,
            bar=bar,
            col=col,
            equity=equity_new,
            fees_paid=fees_paid,
            indicator_settings_counter=indicator_settings_counter,
            max_equity_risk_pct=max_equity_risk_pct,
            order_count_id=order_count_id,
            order_records=order_records,
            order_settings_counter=order_settings_counter,
            order_type=order_type,
            price=price,
            realized_pnl=realized_pnl,
            risk_rewards=risk_rewards,
            size_value=size_value,
            sl_pcts=sl_pcts,
        )
        order_count_id_new += 1
        order_records_filled_new += 1

    if log_count_id != None:
        if order_status == OrderStatus.Filled:
            fill_log_records_nb(
                average_entry=average_entry,
                bar=bar,
                col=col,
                log_count_id=log_count_id,
                log_records=log_records,
                order_count_id=order_count_id,
                order_type=order_type,
                price=price,
                realized_pnl=realized_pnl,
                sl_prices=sl_prices,
                tsl_prices=tsl_prices,
                tp_prices=tp_prices,
            )
            log_count_id_new += 1
            log_records_filled_new += 1

    return available_balance_new, \
        cash_borrowed_new, \
        cash_used_new, \
        equity_new, \
        fees_paid, \
        liq_price, \
        log_count_id_new, \
        log_records_filled_new, \
        order_count_id_new, \
        order_records_filled_new, \
        order_status_info, \
        order_status, \
        position_new, \
        realized_pnl
