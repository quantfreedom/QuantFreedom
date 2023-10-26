import numpy as np
from numba import njit

from quantfreedom.enums import CandleBodyType, LoggerFuncType, StringerFuncType
from quantfreedom.helper_funcs import round_size_by_tick_step


@njit(cache=True)
def long_calc_liq_price(
    logger,
    stringer,
    average_entry: float,
    entry_size_usd: float,
    leverage: float,
    mmr_pct: float,
    og_available_balance: float,
    og_cash_borrowed: float,
    og_cash_used: float,
    price_tick_step: float,
):
    # Getting Order Cost
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
    initial_margin = entry_size_usd / leverage
    fee_to_open = entry_size_usd * 0.0009  # math checked
    possible_bankruptcy_fee = entry_size_usd * (leverage - 1) / leverage * mmr_pct
    cash_used = initial_margin + fee_to_open + possible_bankruptcy_fee  # math checked
    logger[LoggerFuncType.Debug](
        "leverage.py - calc_liq_price() -"
        + "\ninitial_margin= "
        + stringer[StringerFuncType.float_to_str](round(initial_margin, 3))
        + "\nfee_to_open= "
        + stringer[StringerFuncType.float_to_str](round(fee_to_open, 3))
        + "\npossible_bankruptcy_fee= "
        + stringer[StringerFuncType.float_to_str](round(possible_bankruptcy_fee, 3))
        + "\ncash_used= "
        + stringer[StringerFuncType.float_to_str](round(cash_used, 3))
    )

    if cash_used > og_available_balance:
        logger[LoggerFuncType.Warning](
            "leverage.py - calc_liq_price() - Cash used bigger than available balance"
        )
        raise Exception
    else:
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        available_balance = round(og_available_balance - cash_used, 3)
        cash_used = round(og_cash_used + cash_used, 3)
        cash_borrowed = round(og_cash_borrowed + entry_size_usd - cash_used, 3)

        liq_price = average_entry * (1 - (1 / leverage) + mmr_pct)  # math checked
        liq_price = round_size_by_tick_step(
            user_num=liq_price,
            exchange_num=price_tick_step,
        )
        logger[LoggerFuncType.Debug](
            "leverage.py - calc_liq_price() -"
            + "\navailable_balance= "
            + stringer[StringerFuncType.float_to_str](available_balance)
            + "\nnew cash_used= "
            + stringer[StringerFuncType.float_to_str](cash_used)
            + "\ncash_borrowed= "
            + stringer[StringerFuncType.float_to_str](cash_borrowed)
            + "\nliq_price= "
            + stringer[StringerFuncType.float_to_str](liq_price)
        )

    return (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    )


@njit(cache=True)
def long_static_lev(
    logger,
    stringer,
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    entry_size_usd: float,
    leverage_tick_step: float,
    max_leverage: float,
    mmr_pct: float,
    sl_price: float,
    static_leverage: float,
    price_tick_step: float,
):
    (
        available_balance,
        can_move_sl_to_be,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = long_calc_liq_price(
        logger=logger,
        stringer=stringer,
        leverage=static_leverage,
        entry_size_usd=entry_size_usd,
        average_entry=average_entry,
        og_cash_used=cash_used,
        og_available_balance=available_balance,
        og_cash_borrowed=cash_borrowed,
        mmr_pct=mmr_pct,
        price_tick_step=price_tick_step,
    )
    leverage = static_leverage
    logger[LoggerFuncType.Debug](
        "leverage.py - calculate_leverage() - Lev set to static lev= "
        + stringer[StringerFuncType.float_to_str](leverage)
    )
    return (
        available_balance,
        can_move_sl_to_be,
        cash_borrowed,
        cash_used,
        leverage,
        liq_price,
    )


@njit(cache=True)
def long_dynamic_lev(
    logger,
    stringer,
    available_balance: float,
    average_entry: float,
    cash_borrowed: float,
    cash_used: float,
    entry_size_usd: float,
    leverage_tick_step: float,
    max_leverage: float,
    min_leverage: float,
    mmr_pct: float,
    sl_price: float,
    static_leverage: float,
    price_tick_step: float,
):
    leverage = -average_entry / ((sl_price - sl_price * 0.001) - average_entry - mmr_pct * average_entry)
    leverage = round_size_by_tick_step(
        user_num=leverage,
        exchange_num=leverage_tick_step,
    )
    if leverage > max_leverage:
        logger[LoggerFuncType.Debug](
            "leverage.py - calculate_leverage() - Lev too high"
            + " Old Lev= "
            + stringer[StringerFuncType.float_to_str](leverage)
            + " Max Lev= "
            + stringer[StringerFuncType.float_to_str](max_leverage)
        )
        leverage = max_leverage
    elif leverage < min_leverage:
        logger[LoggerFuncType.Debug](
            "leverage.py - calculate_leverage() - Lev too low"
            + " Old Lev= "
            + stringer[StringerFuncType.float_to_str](leverage)
            + " Min Lev= "
            + stringer[StringerFuncType.float_to_str](min_leverage)
        )
        leverage = 1
    else:
        logger[LoggerFuncType.Debug](
            "leverage.py - calculate_leverage() -"
            + " Leverage= "
            + stringer[StringerFuncType.float_to_str](leverage)
        )

    (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = long_calc_liq_price(
        logger=logger,
        stringer=stringer,
        leverage=leverage,
        entry_size_usd=entry_size_usd,
        average_entry=average_entry,
        mmr_pct=mmr_pct,
        og_cash_used=cash_used,
        og_available_balance=available_balance,
        og_cash_borrowed=cash_borrowed,
        price_tick_step=price_tick_step,
    )
    return (
        available_balance,
        cash_borrowed,
        cash_used,
        leverage,
        liq_price,
    )


@njit(cache=True)
def long_check_liq_hit(
    logger,
    current_candle: np.array,
    liq_price: float,
    stringer,
):
    candle_low = current_candle[CandleBodyType.Low]
    logger[LoggerFuncType.Debug](
        "leverage.py - long_check_liq_hit() - candle_low= " + stringer[StringerFuncType.float_to_str](candle_low)
    )
    if liq_price > candle_low:
        logger[LoggerFuncType.Debug]("leverage.py - check_liq_hit() - Liq Hit")
        return True
    else:
        logger[LoggerFuncType.Debug]("leverage.py - check_liq_hit() - No hit on liq price")
        return False
