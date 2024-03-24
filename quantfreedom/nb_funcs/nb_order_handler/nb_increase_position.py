from typing import Callable, NamedTuple
from numba import njit

from quantfreedom.enums import LoggerFuncType, RejectedOrder, StringerFuncType
from quantfreedom.nb_funcs.nb_helper_funcs import nb_round_size_by_tick_step


class AccExOther(NamedTuple):
    equity: float
    asset_tick_step: float
    market_fee_pct: float
    max_asset_size: float
    min_asset_size: float
    total_possible_loss: float
    price_tick_step: float
    total_trades: int


class OrderInfo(NamedTuple):
    average_entry: float
    entry_price: float
    in_position: bool
    max_equity_risk_pct: float
    max_trades: int
    position_size_asset: float
    position_size_usd: float
    account_pct_risk_per_trade: float
    sl_price: float


@njit(cache=True)
def nb_long_entry_size_p(
    average_entry: float,
    entry_price: float,
    market_fee_pct: float,
    position_size_usd: float,
    total_possible_loss: float,
    sl_price: float,
):
    # math https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(n%20-%20%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Cright)%5Cright)-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%20n%5Ccdot%20m%5Cright)%20%5Cright)%3D-f?or=input

    return round(
        -(
            (
                entry_price * average_entry * total_possible_loss
                - entry_price * sl_price * position_size_usd
                + entry_price * sl_price * market_fee_pct * position_size_usd
                + entry_price * average_entry * position_size_usd
                + entry_price * market_fee_pct * average_entry * position_size_usd
            )
            / (average_entry * (-sl_price + entry_price + sl_price * market_fee_pct + entry_price * market_fee_pct))
        ),
        3,
    )


@njit(cache=True)
def nb_long_entry_size_np(
    entry_price: float,
    market_fee_pct: float,
    total_possible_loss: float,
    sl_price: float,
):
    # math https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%5Cleft(x%20-%20e%5Cright)%5Cright)-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20e%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20x%5Ccdot%20m%5Cright)%20%5Cright)%3Dp?or=input

    return round(
        entry_price
        * -total_possible_loss
        / (-sl_price + entry_price + entry_price * market_fee_pct + market_fee_pct * sl_price),
        3,
    )


@njit(cache=True)
def nb_short_entry_size_p(
    average_entry: float,
    entry_price: float,
    market_fee_pct: float,
    position_size_usd: float,
    total_possible_loss: float,
    sl_price: float,
):
    # math https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)-n%5Cright)%5Cright)-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%5Cleft(%5Cfrac%7B%5Cleft(p%2Bu%5Cright)%7D%7B%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%7D%5Cright)%5Ccdot%20%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bp%7D%7Ba%7D%2B%5Cfrac%7Bu%7D%7Be%7D%5Cright)%5Ccdot%20%20n%5Ccdot%20%20m%5Cright)%20%5Cright)%3D-f?or=input

    return round(
        -(
            (
                entry_price * average_entry * total_possible_loss
                - entry_price * average_entry * position_size_usd
                + entry_price * sl_price * position_size_usd
                + entry_price * sl_price * market_fee_pct * position_size_usd
                + entry_price * market_fee_pct * average_entry * position_size_usd
            )
            / (average_entry * (sl_price - entry_price + sl_price * market_fee_pct + entry_price * market_fee_pct))
        ),
        3,
    )


@njit(cache=True)
def nb_short_entry_size_np(
    entry_price: float,
    market_fee_pct: float,
    total_possible_loss: float,
    sl_price: float,
):
    # math https://www.symbolab.com/solver/simplify-calculator/solve%20for%20u%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%5Cleft(e%20-%20x%5Cright)%5Cright)-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20e%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cfrac%7Bu%7D%7Be%7D%5Ccdot%20x%5Ccdot%20m%5Cright)%20%5Cright)%3Dp?or=input
    return -round(
        entry_price
        * -total_possible_loss
        / (-entry_price + sl_price + entry_price * market_fee_pct + market_fee_pct * sl_price),
        3,
    )


@njit(cache=True)
def nb_c_too_b_s(
    entry_size_asset: float,
    logger,
    max_asset_size: float,
    min_asset_size: float,
    stringer,
):
    """
    Check if the asset size is too big or too small
    """
    if entry_size_asset < min_asset_size:
        logger(
            "nb_increase_position.py - nb_c_too_b_s() - 42 - entry size too small "
            + "entry_size_asset= "
            + stringer[StringerFuncType.float_to_str](entry_size_asset)
            + " < min_asset_size= "
            + stringer[StringerFuncType.float_to_str](min_asset_size)
        )
        raise RejectedOrder
    elif entry_size_asset > max_asset_size:
        logger(
            "nb_increase_position.py - nb_c_too_b_s() - 50 - entry size too big"
            + "entry_size_asset= "
            + stringer[StringerFuncType.float_to_str](entry_size_asset)
            + " > max_asset_size= "
            + stringer[StringerFuncType.float_to_str](max_asset_size)
        )
        raise RejectedOrder

    logger(
        "nb_increase_position.py - nb_c_too_b_s() - Entry size is fine"
        + "entry_size_asset= "
        + stringer[StringerFuncType.float_to_str](entry_size_asset)
    )


@njit(cache=True)
def nb_c_pl_ra_ps(
    equity: float,
    logger,
    max_equity_risk_pct: float,
    total_possible_loss: float,
    account_pct_risk_per_trade: float,
    total_trades: int,
):
    """
    Possible loss risk account percent size
    """
    logger("nb_increase_position.py - nb_c_pl_ra_ps() - Inside")
    total_possible_loss = int(total_possible_loss - equity * account_pct_risk_per_trade)
    logger("nb_increase_position.py - nb_c_pl_ra_ps() -" + " total_possible_loss= " + str(total_possible_loss))
    max_equity_risk = -round(equity * max_equity_risk_pct, 0)
    logger("nb_increase_position.py - nb_c_pl_ra_ps() -" + " max_equity_risk= " + str(int(max_equity_risk)))
    if total_possible_loss < max_equity_risk:
        logger(
            "nb_increase_position.py - nb_c_pl_ra_ps() - Too big"
            + " total_possible_loss= "
            + str(int(total_possible_loss))
            + " max risk= "
            + str(int(max_equity_risk))
        )
        raise RejectedOrder
    total_trades += 1
    logger(
        "nb_increase_position.py - nb_c_pl_ra_ps() - PL is fine"
        + " total_possible_loss= "
        + str(int(total_possible_loss))
        + " max risk= "
        + str(int(max_equity_risk))
        + " total trades= "
        + str(int(total_trades))
    )
    return total_possible_loss, total_trades


@njit(cache=True)
def nb_c_total_trades(
    average_entry: float,
    logger,
    market_fee_pct: float,
    max_trades: int,
    position_size_asset: float,
    total_possible_loss: float,
    sl_price: float,
    stringer,
    total_trades: int,
):
    """
    Checking the total trades
    """
    pnl = -abs(average_entry - sl_price) * position_size_asset  # math checked
    fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
    fee_close = position_size_asset * sl_price * market_fee_pct  # math checked
    fees_paid = fee_open + fee_close  # math checked
    total_possible_loss = int(pnl - fees_paid)
    logger("nb_increase_position.py - nb_c_total_trades() -" + " total_possible_loss= " + str(total_possible_loss))
    total_trades += 1
    if total_trades > max_trades:
        logger(
            "nb_increase_position.py - nb_c_total_trades() - Max trades reached"
            + " total trades= "
            + str(total_trades)
            + " max trades= "
            + str(max_trades)
            + " total_possible_loss= "
            + str(total_possible_loss)
        )
        raise RejectedOrder
    logger(
        "nb_increase_position.py - nb_c_total_trades() - Max trades reached "
        + " total trades= "
        + str(total_trades)
        + " max trades= "
        + str(max_trades)
        + " total_possible_loss= "
        + str(total_possible_loss)
    )
    return total_possible_loss, total_trades


@njit(cache=True)
def nb_rpa_slbcb(
    acc_ex_other: AccExOther,
    logger,
    nb_entry_calc_np,
    nb_entry_calc_p,
    order_info: OrderInfo,
    stringer,
):
    """
    Risking percent of your account while also having your stop loss based open high low or close of a candle
    """
    if order_info.in_position:
        logger("nb_increase_position.py - nb_long_rpa_slbcb() - We are in a position")
        return nb_rpa_slbcb_p(
            acc_ex_other=acc_ex_other,
            logger=logger,
            nb_entry_calc_p=nb_entry_calc_p,
            order_info=order_info,
            stringer=stringer,
        )
    else:
        logger("nb_increase_position.py - nb_long_rpa_slbcb() - Not in a position")
        return nb_rpa_slbcb_np(
            acc_ex_other=acc_ex_other,
            logger=logger,
            nb_entry_calc_np=nb_entry_calc_np,
            order_info=order_info,
            stringer=stringer,
        )


@njit(cache=True)
def nb_rpa_slbcb_p(
    acc_ex_other: AccExOther,
    logger,
    nb_entry_calc_p,
    order_info: OrderInfo,
    stringer,
):
    equity = acc_ex_other.equity
    asset_tick_step = acc_ex_other.asset_tick_step
    logger = logger
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    total_possible_loss = acc_ex_other.total_possible_loss
    price_tick_step = acc_ex_other.price_tick_step
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_equity_risk_pct = order_info.max_equity_risk_pct
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    account_pct_risk_per_trade = order_info.account_pct_risk_per_trade
    sl_price = order_info.sl_price

    logger("nb_increase_position.py - nb_long_rpa_slbcb_p() - Calculating")
    total_possible_loss, total_trades = nb_c_pl_ra_ps(
        equity=equity,
        logger=logger,
        max_equity_risk_pct=max_equity_risk_pct,
        total_possible_loss=total_possible_loss,
        account_pct_risk_per_trade=account_pct_risk_per_trade,
        total_trades=total_trades,
    )

    entry_size_usd = nb_entry_calc_p(
        average_entry=average_entry,
        entry_price=entry_price,
        market_fee_pct=market_fee_pct,
        position_size_usd=position_size_usd,
        total_possible_loss=total_possible_loss,
        sl_price=sl_price,
    )

    logger(
        "nb_increase_position.py - nb_long_rpa_slbcb_p() - "
        + "entry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
    )

    entry_size_asset = nb_round_size_by_tick_step(
        exchange_num=asset_tick_step,
        user_num=entry_size_usd / entry_price,
    )
    nb_c_too_b_s(
        entry_size_asset=entry_size_asset,
        logger=logger,
        max_asset_size=max_asset_size,
        min_asset_size=min_asset_size,
        stringer=stringer,
    )

    position_size_asset = nb_round_size_by_tick_step(
        exchange_num=asset_tick_step,
        user_num=position_size_asset + entry_size_asset,
    )
    logger(
        "nb_increase_position.py - nb_long_rpa_slbcb_p() - "
        + "position_size_asset= "
        + stringer[StringerFuncType.float_to_str](position_size_asset)
    )

    position_size_usd = round(entry_size_usd + position_size_usd, 3)
    logger(
        "nb_increase_position.py - nb_long_rpa_slbcb_p() - "
        + "position_size_usd= "
        + stringer[StringerFuncType.float_to_str](position_size_usd)
    )

    average_entry = (entry_size_usd + position_size_usd) / (
        (entry_size_usd / entry_price) + (position_size_usd / average_entry)
    )
    average_entry = nb_round_size_by_tick_step(
        exchange_num=price_tick_step,
        user_num=average_entry,
    )
    logger(
        "nb_increase_position.py - nb_long_rpa_slbcb_p() - "
        + "average_entry= "
        + stringer[StringerFuncType.float_to_str](average_entry)
    )

    sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
    logger(
        "nb_increase_position.py - nb_long_rpa_slbcb_p() - "
        + "sl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
    )

    logger(
        "nb_increase_position.py - nb_long_rpa_slbcb_p() - "
        + "\naverage_entry= "
        + stringer[StringerFuncType.float_to_str](average_entry)
        + "\nentry_price= "
        + stringer[StringerFuncType.float_to_str](entry_price)
        + "\nentry_size_asset= "
        + stringer[StringerFuncType.float_to_str](entry_size_asset)
        + "\nentry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
        + "\nposition_size_asset= "
        + stringer[StringerFuncType.float_to_str](position_size_asset)
        + "\nposition_size_usd= "
        + stringer[StringerFuncType.float_to_str](position_size_usd)
        + "\ntotal_possible_loss= "
        + stringer[StringerFuncType.float_to_str](total_possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        total_possible_loss,
        total_trades,
        sl_pct,
    )


@njit(cache=True)
def nb_rpa_slbcb_np(
    acc_ex_other: AccExOther,
    logger,
    nb_entry_calc_np,
    order_info: OrderInfo,
    stringer,
):
    equity = acc_ex_other.equity
    asset_tick_step = acc_ex_other.asset_tick_step
    logger = logger
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    total_possible_loss = acc_ex_other.total_possible_loss
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_equity_risk_pct = order_info.max_equity_risk_pct
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    account_pct_risk_per_trade = order_info.account_pct_risk_per_trade
    sl_price = order_info.sl_price

    logger("nb_increase_position.py - nb_rpa_slbcb_np() - Calculating")
    total_possible_loss, total_trades = nb_c_pl_ra_ps(
        equity=equity,
        logger=logger,
        max_equity_risk_pct=max_equity_risk_pct,
        total_possible_loss=total_possible_loss,
        account_pct_risk_per_trade=account_pct_risk_per_trade,
        total_trades=total_trades,
    )

    entry_size_usd = position_size_usd = nb_entry_calc_np(
        entry_price=entry_price,
        market_fee_pct=market_fee_pct,
        total_possible_loss=total_possible_loss,
        sl_price=sl_price,
    )
    logger(
        "nb_increase_position.py - nb_rpa_slbcb_np() - "
        + "entry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
    )
    entry_size_asset = position_size_asset = nb_round_size_by_tick_step(
        exchange_num=asset_tick_step,
        user_num=entry_size_usd / entry_price,
    )
    nb_c_too_b_s(
        entry_size_asset=entry_size_asset,
        logger=logger,
        max_asset_size=max_asset_size,
        min_asset_size=min_asset_size,
        stringer=stringer,
    )

    average_entry = entry_price

    sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
    logger(
        "nb_increase_position.py - nb_rpa_slbcb_np() - "
        + "sl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
    )

    logger(
        "nb_increase_position.py - nb_rpa_slbcb_np() - "
        + "\naverage_entry= "
        + stringer[StringerFuncType.float_to_str](average_entry)
        + "\nentry_price= "
        + stringer[StringerFuncType.float_to_str](entry_price)
        + "\nentry_size_asset= "
        + stringer[StringerFuncType.float_to_str](entry_size_asset)
        + "\nentry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
        + "\nposition_size_asset= "
        + stringer[StringerFuncType.float_to_str](position_size_asset)
        + "\nposition_size_usd= "
        + stringer[StringerFuncType.float_to_str](position_size_usd)
        + "\ntotal_possible_loss= "
        + stringer[StringerFuncType.float_to_str](total_possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        total_possible_loss,
        total_trades,
        sl_pct,
    )


@njit(cache=True)
def nb_min_asset_amount(
    acc_ex_other: AccExOther,
    logger,
    nb_entry_calc_np,
    nb_entry_calc_p,
    order_info: OrderInfo,
    stringer,
):
    """
    Setting your position size to the min amount the exchange will allow

    """
    if order_info.in_position:
        logger("nb_increase_position.py - nb_long_min_amount() - We are in a position")
        return nb_min_amount_p(
            acc_ex_other=acc_ex_other,
            logger=logger,
            order_info=order_info,
            stringer=stringer,
        )
    else:
        logger("nb_increase_position.py - nb_long_min_amount() - Not in a position")
        return nb_min_amount_np(
            acc_ex_other=acc_ex_other,
            logger=logger,
            order_info=order_info,
            stringer=stringer,
        )


@njit(cache=True)
def nb_min_amount_p(
    acc_ex_other: AccExOther,
    logger,
    order_info: OrderInfo,
    stringer,
):
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    total_possible_loss = acc_ex_other.total_possible_loss
    price_tick_step = acc_ex_other.price_tick_step
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_trades = order_info.max_trades
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    sl_price = order_info.sl_price

    logger("nb_increase_position.py - nb_long_min_amount_p() - Calculating")

    position_size_asset += min_asset_size
    entry_size_asset = min_asset_size
    logger(
        "nb_increase_position.py - nb_long_min_amount_p() - entry_size_asset position_size_asset{entry_size_asset, position_size_asset}"
    )

    entry_size_usd = round(min_asset_size * entry_price, 3)
    logger("nb_increase_position.py - nb_long_min_amount_p() - entry_size_usd entry_size_usd}")

    average_entry = (entry_size_usd + position_size_usd) / (
        (entry_size_usd / entry_price) + (position_size_usd / average_entry)
    )
    average_entry = nb_round_size_by_tick_step(
        exchange_num=price_tick_step,
        user_num=average_entry,
    )
    logger("nb_increase_position.py - nb_long_min_amount_p() - average_entry average_entry}")

    sl_pct = round((average_entry - sl_price) / average_entry, 3)
    logger("nb_increase_position.py - nb_long_min_amount_p() - sl_pct={round(sl_pct*100, 3))")

    position_size_usd = round(entry_size_usd + position_size_usd, 3)
    logger("nb_increase_position.py - nb_long_min_amount_p() - position_size_usd position_size_usd}")

    total_possible_loss, total_trades = nb_c_total_trades(
        average_entry=average_entry,
        logger=logger,
        market_fee_pct=market_fee_pct,
        max_trades=max_trades,
        position_size_asset=position_size_asset,
        total_possible_loss=total_possible_loss,
        sl_price=sl_price,
        stringer=stringer,
        total_trades=total_trades,
    )
    logger(
        "nb_increase_position.py - nb_long_min_amount_p() - total_possible_loss, total_trades {total_possible_loss, total_trades}"
    )

    nb_c_too_b_s(
        entry_size_asset=entry_size_asset,
        logger=logger,
        max_asset_size=max_asset_size,
        min_asset_size=min_asset_size,
        stringer=stringer,
    )
    logger(
        "nb_increase_position.py - nb_rpa_slbcb_np() - "
        + "\naverage_entry= "
        + stringer[StringerFuncType.float_to_str](average_entry)
        + "\nentry_price= "
        + stringer[StringerFuncType.float_to_str](entry_price)
        + "\nentry_size_asset= "
        + stringer[StringerFuncType.float_to_str](entry_size_asset)
        + "\nentry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
        + "\nposition_size_asset= "
        + stringer[StringerFuncType.float_to_str](position_size_asset)
        + "\nposition_size_usd= "
        + stringer[StringerFuncType.float_to_str](position_size_usd)
        + "\ntotal_possible_loss= "
        + stringer[StringerFuncType.float_to_str](total_possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        total_possible_loss,
        total_trades,
        sl_pct,
    )


@njit(cache=True)
def nb_min_amount_np(
    acc_ex_other: AccExOther,
    logger,
    order_info: OrderInfo,
    stringer,
):
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    total_possible_loss = acc_ex_other.total_possible_loss
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_trades = order_info.max_trades
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    sl_price = order_info.sl_price

    logger("nb_increase_position.py - nb_long_min_amount_np() - Calculating")
    entry_size_asset = position_size_asset = min_asset_size
    logger("entry_size_asset position_size_asset{entry_size_asset, position_size_asset}")

    entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 3)
    logger("entry_size_usd position_size_usd {entry_size_usd, position_size_usd}")

    average_entry = entry_price
    logger("average_entry average_entry}")
    sl_pct = round((average_entry - sl_price) / average_entry, 3)
    logger("sl_pct={round(sl_pct*100, 3))")

    total_possible_loss, total_trades = nb_c_total_trades(
        average_entry=average_entry,
        logger=logger,
        market_fee_pct=market_fee_pct,
        max_trades=max_trades,
        position_size_asset=position_size_asset,
        total_possible_loss=total_possible_loss,
        sl_price=sl_price,
        stringer=stringer,
        total_trades=total_trades,
    )
    logger("total_possible_loss, total_trades {total_possible_loss, total_trades}")

    nb_c_too_b_s(
        entry_size_asset=entry_size_asset,
        logger=logger,
        max_asset_size=max_asset_size,
        min_asset_size=min_asset_size,
        stringer=stringer,
    )
    logger(
        "nb_increase_position.py - nb_rpa_slbcb_np() - "
        + "\naverage_entry= "
        + stringer[StringerFuncType.float_to_str](average_entry)
        + "\nentry_price= "
        + stringer[StringerFuncType.float_to_str](entry_price)
        + "\nentry_size_asset= "
        + stringer[StringerFuncType.float_to_str](entry_size_asset)
        + "\nentry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
        + "\nposition_size_asset= "
        + stringer[StringerFuncType.float_to_str](position_size_asset)
        + "\nposition_size_usd= "
        + stringer[StringerFuncType.float_to_str](position_size_usd)
        + "\ntotal_possible_loss= "
        + stringer[StringerFuncType.float_to_str](total_possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        total_possible_loss,
        total_trades,
        sl_pct,
    )
