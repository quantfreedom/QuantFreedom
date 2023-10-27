from typing import NamedTuple

from quantfreedom.enums import LoggerFuncType, RejectedOrder, StringerFuncType
from quantfreedom.helper_funcs import round_size_by_tick_step


class AccExOther(NamedTuple):
    account_state_equity: float
    asset_tick_step: float
    market_fee_pct: float
    max_asset_size: float
    min_asset_size: float
    possible_loss: float
    price_tick_step: float
    total_trades: int


class OrderInfo(NamedTuple):
    average_entry: float
    entry_price: float
    in_position: float
    max_equity_risk_pct: float
    max_trades: int
    position_size_asset: float
    position_size_usd: float
    risk_account_pct_size: float
    sl_price: float


def c_too_b_s(
    entry_size_asset: float,
    min_asset_size: float,
    max_asset_size: float,
    logger,
    stringer,
):
    """
    Check if the asset size is too big or too small
    """
    if entry_size_asset < min_asset_size:
        logger[LoggerFuncType.Warning](
            "increase_position.py - c_too_b_s() - entry size too small "
            + "entry_size_asset= "
            + stringer[StringerFuncType.float_to_str](entry_size_asset)
            + " < min_asset_size= "
            + stringer[StringerFuncType.float_to_str](min_asset_size)
        )
        raise RejectedOrder
    elif entry_size_asset > max_asset_size:
        logger[LoggerFuncType.Warning](
            "increase_position.py - c_too_b_s() - entry size too big"
            + "entry_size_asset= "
            + stringer[StringerFuncType.float_to_str](entry_size_asset)
            + " > max_asset_size= "
            + stringer[StringerFuncType.float_to_str](max_asset_size)
        )
        raise RejectedOrder

    logger[LoggerFuncType.Debug](
        "increase_position.py - c_too_b_s() - Entry size is fine"
        + "entry_size_asset= "
        + stringer[StringerFuncType.float_to_str](entry_size_asset)
    )


def c_pl_ra_ps(
    logger,
    account_state_equity: float,
    possible_loss: float,
    total_trades: int,
    risk_account_pct_size: float,
    max_equity_risk_pct: float,
):
    """
    Possible loss risk account percent size
    """
    logger[LoggerFuncType.Debug]("increase_position.py - c_pl_ra_ps() - Inside")
    possible_loss = round(possible_loss + account_state_equity * risk_account_pct_size, 0)
    logger[LoggerFuncType.Debug]("increase_position.py - c_pl_ra_ps() -" + " possible_loss= " + str(int(possible_loss)))
    max_equity_risk = round(account_state_equity * max_equity_risk_pct)
    logger[LoggerFuncType.Debug](
        "increase_position.py - c_pl_ra_ps() -" + " max_equity_risk= " + str(int(max_equity_risk))
    )
    if possible_loss > max_equity_risk:
        logger[LoggerFuncType.Warning](
            "increase_position.py - c_pl_ra_ps() - Too big"
            + " possible_loss= "
            + str(int(possible_loss))
            + " max risk= "
            + str(int(max_equity_risk))
        )
        raise RejectedOrder
    total_trades += 1
    logger[LoggerFuncType.Debug](
        "increase_position.py - c_pl_ra_ps() - PL is fine"
        + " possible_loss= "
        + str(int(possible_loss))
        + " max risk= "
        + str(int(max_equity_risk))
        + " total trades= "
        + str(int(total_trades))
    )
    return possible_loss, total_trades


def c_total_trades(
    logger,
    average_entry: float,
    possible_loss: float,
    position_size_asset: float,
    sl_price: float,
    total_trades: int,
    market_fee_pct: float,
    max_trades: int,
    stringer,
):
    """
    Checking the total trades
    """
    pnl = position_size_asset * (sl_price - average_entry)  # math checked
    fee_open = position_size_asset * average_entry * market_fee_pct  # math checked
    fee_close = position_size_asset * sl_price * market_fee_pct  # math checked
    fees_paid = fee_open + fee_close  # math checked
    possible_loss = round(-(pnl - fees_paid), 4)
    logger[LoggerFuncType.Debug](
        "increase_position.py - c_total_trades() -" + " possible_loss= " + str(int(possible_loss))
    )
    total_trades += 1
    if total_trades > max_trades:
        logger[LoggerFuncType.Warning](
            "increase_position.py - c_total_trades() - Max trades reached"
            + " total trades= "
            + str(int(total_trades))
            + " max trades= "
            + str(int(max_trades))
            + " possible_loss= "
            + stringer[StringerFuncType.float_to_str](possible_loss)
        )
        raise RejectedOrder
    logger[LoggerFuncType.Debug](
        "increase_position.py - c_total_trades() - Max trades reached "
        + "total trades= "
        + str(int(total_trades))
        + " max trades= "
        + str(int(max_trades))
        + " possible_loss= "
        + stringer[StringerFuncType.float_to_str](possible_loss)
    )
    return possible_loss, total_trades


def long_rpa_slbcb(
    acc_ex_other: AccExOther,
    order_info: OrderInfo,
    logger,
    stringer,
):
    """
    Risking percent of your account while also having your stop loss based open high low or close of a candle
    """
    if order_info.in_position:
        logger[LoggerFuncType.Debug]("increase_position.py - long_rpa_slbcb() - We are in a position")
        return long_rpa_slbcb_p(
            acc_ex_other=acc_ex_other,
            order_info=order_info,
            logger=logger,
            stringer=stringer,
        )
    else:
        logger[LoggerFuncType.Debug]("increase_position.py - long_rpa_slbcb() - Not in a position")
        return long_rpa_slbcb_np(
            acc_ex_other=acc_ex_other,
            order_info=order_info,
            logger=logger,
            stringer=stringer,
        )


def long_rpa_slbcb_p(
    acc_ex_other: AccExOther,
    order_info: OrderInfo,
    logger,
    stringer,
):
    account_state_equity = acc_ex_other.account_state_equity
    asset_tick_step = acc_ex_other.asset_tick_step
    logger = logger
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    possible_loss = acc_ex_other.possible_loss
    price_tick_step = acc_ex_other.price_tick_step
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_equity_risk_pct = order_info.max_equity_risk_pct
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    risk_account_pct_size = order_info.risk_account_pct_size
    sl_price = order_info.sl_price

    logger[LoggerFuncType.Debug]("increase_position.py - long_rpa_slbcb_p() - Calculating")
    possible_loss, total_trades = c_pl_ra_ps(
        logger=logger,
        possible_loss=possible_loss,
        account_state_equity=account_state_equity,
        total_trades=total_trades,
        risk_account_pct_size=risk_account_pct_size,
        max_equity_risk_pct=max_equity_risk_pct,
    )

    entry_size_usd = round(
        -(
            (
                -possible_loss * entry_price * average_entry
                + entry_price * position_size_usd * average_entry
                - sl_price * entry_price * position_size_usd
                + sl_price * entry_price * position_size_usd * market_fee_pct
                + entry_price * position_size_usd * average_entry * market_fee_pct
            )
            / (average_entry * (entry_price - sl_price + entry_price * market_fee_pct + sl_price * market_fee_pct))
        ),
        3,
    )
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_p() - "
        + "entry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
    )

    entry_size_asset = round_size_by_tick_step(
        user_num=entry_size_usd / entry_price,
        exchange_num=asset_tick_step,
    )
    c_too_b_s(
        logger=logger,
        entry_size_asset=entry_size_asset,
        min_asset_size=min_asset_size,
        max_asset_size=max_asset_size,
        stringer=stringer,
    )

    position_size_asset = round_size_by_tick_step(
        user_num=position_size_asset + entry_size_asset,
        exchange_num=asset_tick_step,
    )
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_p() - "
        + "position_size_asset= "
        + stringer[StringerFuncType.float_to_str](position_size_asset)
    )

    position_size_usd = round(entry_size_usd + position_size_usd, 4)
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_p() - "
        + "position_size_usd= "
        + stringer[StringerFuncType.float_to_str](position_size_usd)
    )

    average_entry = (entry_size_usd + position_size_usd) / (
        (entry_size_usd / entry_price) + (position_size_usd / average_entry)
    )
    average_entry = round_size_by_tick_step(
        user_num=average_entry,
        exchange_num=price_tick_step,
    )
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_p() - "
        + "average_entry= "
        + stringer[StringerFuncType.float_to_str](average_entry)
    )

    sl_pct = round((average_entry - sl_price) / average_entry, 4)
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_p() - "
        + "sl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 4))
    )

    logger[LoggerFuncType.Info](
        "increase_position.py - long_rpa_slbcb_p() - "
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
        + "\npossible_loss= "
        + stringer[StringerFuncType.float_to_str](possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 4))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        possible_loss,
        total_trades,
        sl_pct,
    )


def long_rpa_slbcb_np(
    acc_ex_other: AccExOther,
    order_info: OrderInfo,
    logger,
    stringer,
):
    account_state_equity = acc_ex_other.account_state_equity
    asset_tick_step = acc_ex_other.asset_tick_step
    logger = logger
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    possible_loss = acc_ex_other.possible_loss
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_equity_risk_pct = order_info.max_equity_risk_pct
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    risk_account_pct_size = order_info.risk_account_pct_size
    sl_price = order_info.sl_price

    logger[LoggerFuncType.Debug]("increase_position.py - long_rpa_slbcb_np() - Calculating")
    possible_loss, total_trades = c_pl_ra_ps(
        logger=logger,
        possible_loss=possible_loss,
        account_state_equity=account_state_equity,
        total_trades=total_trades,
        risk_account_pct_size=risk_account_pct_size,
        max_equity_risk_pct=max_equity_risk_pct,
    )

    entry_size_usd = position_size_usd = round(
        -possible_loss / (sl_price / entry_price - 1 - market_fee_pct - sl_price * market_fee_pct / entry_price),
        3,
    )
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_np() - "
        + "entry_size_usd= "
        + stringer[StringerFuncType.float_to_str](entry_size_usd)
    )
    entry_size_asset = position_size_asset = round_size_by_tick_step(
        user_num=entry_size_usd / entry_price,
        exchange_num=asset_tick_step,
    )
    c_too_b_s(
        logger=logger,
        entry_size_asset=entry_size_asset,
        min_asset_size=min_asset_size,
        max_asset_size=max_asset_size,
        stringer=stringer,
    )

    average_entry = entry_price

    sl_pct = round((average_entry - sl_price) / average_entry, 4)
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_rpa_slbcb_np() - "
        + "sl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 4))
    )

    logger[LoggerFuncType.Info](
        "increase_position.py - long_rpa_slbcb_np() - "
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
        + "\npossible_loss= "
        + stringer[StringerFuncType.float_to_str](possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 4))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        possible_loss,
        total_trades,
        sl_pct,
    )


def long_min_amount(
    acc_ex_other: AccExOther,
    order_info: OrderInfo,
    logger,
    stringer,
):
    """
    Setting your position size to the min amount the exchange will allow

    """
    if order_info.in_position:
        logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount() - We are in a position")
        return long_min_amount_p(
            acc_ex_other=acc_ex_other,
            order_info=order_info,
            logger=logger,
            stringer=stringer,
        )
    else:
        logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount() - Not in a position")
        return long_min_amount_np(
            acc_ex_other=acc_ex_other,
            order_info=order_info,
            logger=logger,
            stringer=stringer,
        )


def long_min_amount_p(
    acc_ex_other: AccExOther,
    order_info: OrderInfo,
    logger,
    stringer,
):
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    possible_loss = acc_ex_other.possible_loss
    price_tick_step = acc_ex_other.price_tick_step
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_trades = order_info.max_trades
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    sl_price = order_info.sl_price

    logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount_p() - Calculating")

    position_size_asset += min_asset_size
    entry_size_asset = min_asset_size
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_min_amount_p() - entry_size_asset position_size_asset{entry_size_asset, position_size_asset}"
    )

    entry_size_usd = round(min_asset_size * entry_price, 4)
    logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount_p() - entry_size_usd entry_size_usd}")

    average_entry = (entry_size_usd + position_size_usd) / (
        (entry_size_usd / entry_price) + (position_size_usd / average_entry)
    )
    average_entry = round_size_by_tick_step(
        user_num=average_entry,
        exchange_num=price_tick_step,
    )
    logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount_p() - average_entry average_entry}")

    sl_pct = round((average_entry - sl_price) / average_entry, 4)
    logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount_p() - sl_pct={round(sl_pct*100,2))")

    position_size_usd = round(entry_size_usd + position_size_usd, 4)
    logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount_p() - position_size_usd position_size_usd}")

    possible_loss, total_trades = c_total_trades(
        logger=logger,
        stringer=stringer,
        average_entry=average_entry,
        possible_loss=possible_loss,
        total_trades=total_trades,
        position_size_asset=position_size_asset,
        sl_price=sl_price,
        market_fee_pct=market_fee_pct,
        max_trades=max_trades,
    )
    logger[LoggerFuncType.Debug](
        "increase_position.py - long_min_amount_p() - possible_loss, total_trades {possible_loss, total_trades}"
    )

    c_too_b_s(
        logger=logger,
        entry_size_asset=entry_size_asset,
        min_asset_size=min_asset_size,
        max_asset_size=max_asset_size,
        stringer=stringer,
    )
    logger[LoggerFuncType.Info](
        "increase_position.py - long_rpa_slbcb_np() - "
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
        + "\npossible_loss= "
        + stringer[StringerFuncType.float_to_str](possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 4))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        possible_loss,
        total_trades,
        sl_pct,
    )


def long_min_amount_np(
    acc_ex_other: AccExOther,
    order_info: OrderInfo,
    logger,
    stringer,
):
    market_fee_pct = acc_ex_other.market_fee_pct
    max_asset_size = acc_ex_other.max_asset_size
    min_asset_size = acc_ex_other.min_asset_size
    possible_loss = acc_ex_other.possible_loss
    total_trades = acc_ex_other.total_trades

    average_entry = order_info.average_entry
    entry_price = order_info.entry_price
    max_trades = order_info.max_trades
    position_size_asset = order_info.position_size_asset
    position_size_usd = order_info.position_size_usd
    sl_price = order_info.sl_price

    logger[LoggerFuncType.Debug]("increase_position.py - long_min_amount_np() - Calculating")
    entry_size_asset = position_size_asset = min_asset_size
    logger[LoggerFuncType.Debug]("entry_size_asset position_size_asset{entry_size_asset, position_size_asset}")

    entry_size_usd = position_size_usd = round(entry_size_asset * entry_price, 4)
    logger[LoggerFuncType.Debug]("entry_size_usd position_size_usd {entry_size_usd, position_size_usd}")

    average_entry = entry_price
    logger[LoggerFuncType.Debug]("average_entry average_entry}")
    sl_pct = round((average_entry - sl_price) / average_entry, 4)
    logger[LoggerFuncType.Debug]("sl_pct={round(sl_pct*100,2))")

    possible_loss, total_trades = c_total_trades(
        logger=logger,
        stringer=stringer,
        average_entry=average_entry,
        possible_loss=possible_loss,
        total_trades=total_trades,
        position_size_asset=position_size_asset,
        sl_price=sl_price,
        market_fee_pct=market_fee_pct,
        max_trades=max_trades,
    )
    logger[LoggerFuncType.Debug]("possible_loss, total_trades {possible_loss, total_trades}")

    c_too_b_s(
        logger=logger,
        entry_size_asset=entry_size_asset,
        min_asset_size=min_asset_size,
        max_asset_size=max_asset_size,
        stringer=stringer,
    )
    logger[LoggerFuncType.Info](
        "increase_position.py - long_rpa_slbcb_np() - "
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
        + "\npossible_loss= "
        + stringer[StringerFuncType.float_to_str](possible_loss)
        + "\ntotal_trades= "
        + stringer[StringerFuncType.float_to_str](total_trades)
        + "\nsl_pct= "
        + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 4))
    )
    return (
        average_entry,
        entry_price,
        entry_size_asset,
        entry_size_usd,
        position_size_asset,
        position_size_usd,
        possible_loss,
        total_trades,
        sl_pct,
    )
