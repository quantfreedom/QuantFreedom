from typing import Callable, NamedTuple
import numpy as np
from numba import njit

from quantfreedom.enums import CandleBodyType, LoggerFuncType, StringerFuncType
from quantfreedom.nb_funcs.nb_helper_funcs import nb_round_size_by_tick_step


class LevAccExOther(NamedTuple):
    available_balance: float
    cash_borrowed: float
    cash_used: float
    leverage_tick_step: float
    market_fee_pct: float
    max_leverage: float
    min_leverage: float
    mmr_pct: float
    price_tick_step: float


class LevOrderInfo(NamedTuple):
    average_entry: float
    position_size_asset: float
    position_size_usd: float
    sl_price: float
    static_leverage: float


@njit(cache=True)
def nb_long_get_bankruptcy_price(
    average_entry: float,
    leverage: float,
):
    # https://www.bybithelp.com/en-US/s/article/Order-Cost-USDT-Contract
    return average_entry * (leverage - 1) / leverage


@njit(cache=True)
def nb_long_get_liq_price(
    average_entry: float,
    leverage: float,
    mmr_pct: float,
):
    # liq formula
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
    return average_entry * (1 - (1 / leverage) + mmr_pct)


@njit(cache=True)
def nb_long_liq_hit_bool(
    current_candle: np.array,
    liq_price: float,
    logger,
    stringer,
):
    candle_low = current_candle[CandleBodyType.Low]
    logger("nb_leverage.py - nb_check_liq_hit() - candle_low= " + stringer[StringerFuncType.float_to_str](candle_low))
    return liq_price > candle_low


@njit(cache=True)
def nb_long_calc_dynamic_lev(
    average_entry: float,
    mmr_pct: float,
    sl_price: float,
):
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
    # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20l%2C%20e%5Ccdot%5Cleft(1-%5Cfrac%7B1%7D%7Bl%7D%2Bm%5Cright)%3Ds-s%5Ccdot%20p?or=input
    # the .001 is to add .001 buffer
    return average_entry / (-sl_price + sl_price * 0.001 + average_entry + average_entry * mmr_pct)


@njit(cache=True)
def nb_short_calc_dynamic_lev(
    average_entry: float,
    mmr_pct: float,
    sl_price: float,
):
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
    # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20l%2C%20e%5Ccdot%5Cleft(1%2B%5Cfrac%7B1%7D%7Bl%7D-m%5Cright)%3Ds%2Bs%5Ccdot%20p?or=input
    # the .001 is to add .001 buffer
    return average_entry / (sl_price + sl_price * 0.001 - average_entry + average_entry * mmr_pct)


@njit(cache=True)
def nb_short_get_bankruptcy_price(
    average_entry: float,
    leverage: float,
):
    # https://www.bybithelp.com/en-US/s/article/Order-Cost-USDT-Contract
    return average_entry * (leverage + 1) / leverage


@njit(cache=True)
def nb_short_get_liq_price(
    average_entry: float,
    leverage: float,
    mmr_pct: float,
):
    # liq formula
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
    return average_entry * (1 + (1 / leverage) - mmr_pct)


@njit(cache=True)
def nb_short_liq_hit_bool(
    current_candle: np.array,
    liq_price: float,
    logger,
    stringer,
):
    candle_high = current_candle[CandleBodyType.High]
    logger("nb_leverage.py - nb_short_liq_hit_bool() - candle_high= " + stringer[StringerFuncType.float_to_str](candle_high))
    return liq_price < candle_high


@njit(cache=True)
def nb_calc_liq_price(
    average_entry: float,
    leverage: float,
    logger,
    market_fee_pct: float,
    mmr_pct: float,
    nb_get_bankruptcy_price,
    nb_get_liq_price,
    og_available_balance: float,
    og_cash_borrowed: float,
    og_cash_used: float,
    position_size_asset: float,
    position_size_usd: float,
    price_tick_step: float,
    stringer,
):
    # Getting Order Cost
    # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001064&language=en_US
    initial_margin = (position_size_asset * average_entry) / leverage
    fee_to_open = position_size_asset * average_entry * market_fee_pct  # math checked
    bankruptcy_price = nb_get_bankruptcy_price(
        average_entry=average_entry,
        leverage=leverage,
    )
    fee_to_close = position_size_asset * bankruptcy_price * market_fee_pct

    cash_used = initial_margin + fee_to_open + fee_to_close  # math checked
    logger(
        "nb_leverage.py - nb_calc_liq_price() -"
        + "\ninitial_margin= "
        + stringer[StringerFuncType.float_to_str](round(initial_margin, 3))
        + "\nfee_to_open= "
        + stringer[StringerFuncType.float_to_str](round(fee_to_open, 3))
        + "\nbankruptcy_price= "
        + stringer[StringerFuncType.float_to_str](round(bankruptcy_price, 3))
        + "\ncash_used= "
        + stringer[StringerFuncType.float_to_str](round(cash_used, 3))
    )

    if cash_used > og_available_balance:
        logger("nb_leverage.py - nb_calc_liq_price() - Cash used bigger than available balance")
        raise Exception
    else:
        # liq formula
        # https://www.bybithelp.com/HelpCenterKnowledge/bybitHC_Article?id=000001067&language=en_US
        available_balance = round(og_available_balance - cash_used, 3)
        cash_used = round(og_cash_used + cash_used, 3)
        cash_borrowed = round(og_cash_borrowed + position_size_usd - cash_used, 3)

        liq_price = nb_get_liq_price(
            average_entry=average_entry,
            leverage=leverage,
            mmr_pct=mmr_pct,
        )  # math checked
        liq_price = nb_round_size_by_tick_step(
            exchange_num=price_tick_step,
            user_num=liq_price,
        )
        logger(
            "nb_leverage.py - nb_calc_liq_price() -"
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
def nb_static_lev(
    lev_acc_ex_other: LevAccExOther,
    lev_order_info: LevOrderInfo,
    logger,
    nb_calc_dynamic_lev,
    nb_get_bankruptcy_price,
    nb_get_liq_price,
    stringer,
):
    (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = nb_calc_liq_price(
        average_entry=lev_order_info.average_entry,
        leverage=lev_order_info.static_leverage,
        logger=logger,
        market_fee_pct=lev_acc_ex_other.market_fee_pct,
        mmr_pct=lev_acc_ex_other.mmr_pct,
        nb_get_bankruptcy_price=nb_get_bankruptcy_price,
        nb_get_liq_price=nb_get_liq_price,
        og_available_balance=lev_acc_ex_other.available_balance,
        og_cash_borrowed=lev_acc_ex_other.cash_borrowed,
        og_cash_used=lev_acc_ex_other.cash_used,
        position_size_asset=lev_order_info.position_size_asset,
        position_size_usd=lev_order_info.position_size_usd,
        price_tick_step=lev_acc_ex_other.price_tick_step,
        stringer=stringer,
    )
    leverage = lev_order_info.static_leverage
    logger(
        "nb_leverage.py - nb_calculate_leverage() - Lev set to static lev= "
        + stringer[StringerFuncType.float_to_str](leverage)
    )
    return (
        available_balance,
        cash_borrowed,
        cash_used,
        leverage,
        liq_price,
    )


@njit(cache=True)
def nb_dynamic_lev(
    lev_acc_ex_other: LevAccExOther,
    lev_order_info: LevOrderInfo,
    logger,
    nb_calc_dynamic_lev,
    nb_get_bankruptcy_price,
    nb_get_liq_price,
    stringer,
):
    leverage = nb_calc_dynamic_lev(
        average_entry=lev_order_info.average_entry,
        mmr_pct=lev_acc_ex_other.mmr_pct,
        sl_price=lev_order_info.sl_price,
    )
    leverage = nb_round_size_by_tick_step(
        exchange_num=lev_acc_ex_other.leverage_tick_step,
        user_num=leverage,
    )
    if leverage > lev_acc_ex_other.max_leverage:
        logger(
            "nb_leverage.py - nb_calculate_leverage() - Lev too high"
            + " Old Lev= "
            + stringer[StringerFuncType.float_to_str](leverage)
            + " Max Lev= "
            + stringer[StringerFuncType.float_to_str](lev_acc_ex_other.max_leverage)
        )
        leverage = lev_acc_ex_other.max_leverage
    elif leverage < lev_acc_ex_other.min_leverage:
        logger(
            "nb_leverage.py - nb_calculate_leverage() - Lev too low"
            + " Old Lev= "
            + stringer[StringerFuncType.float_to_str](leverage)
            + " Min Lev= "
            + stringer[StringerFuncType.float_to_str](lev_acc_ex_other.min_leverage)
        )
        leverage = 1.0
    else:
        logger(
            "nb_leverage.py - nb_calculate_leverage() -"
            + " Leverage= "
            + stringer[StringerFuncType.float_to_str](leverage)
        )

    (
        available_balance,
        cash_borrowed,
        cash_used,
        liq_price,
    ) = nb_calc_liq_price(
        average_entry=lev_order_info.average_entry,
        leverage=leverage,
        logger=logger,
        market_fee_pct=lev_acc_ex_other.market_fee_pct,
        mmr_pct=lev_acc_ex_other.mmr_pct,
        nb_get_bankruptcy_price=nb_get_bankruptcy_price,
        nb_get_liq_price=nb_get_liq_price,
        og_available_balance=lev_acc_ex_other.available_balance,
        og_cash_borrowed=lev_acc_ex_other.cash_borrowed,
        og_cash_used=lev_acc_ex_other.cash_used,
        position_size_asset=lev_order_info.position_size_asset,
        position_size_usd=lev_order_info.position_size_usd,
        price_tick_step=lev_acc_ex_other.price_tick_step,
        stringer=stringer,
    )
    return (
        available_balance,
        cash_borrowed,
        cash_used,
        leverage,
        liq_price,
    )


@njit(cache=True)
def nb_check_liq_hit(
    current_candle: np.array,
    liq_price: float,
    logger,
    nb_liq_hit_bool,
    stringer,
):
    candle_low = current_candle[CandleBodyType.Low]
    if nb_liq_hit_bool(
        current_candle=current_candle,
        logger=logger,
        liq_price=liq_price,
        stringer=stringer,
    ):
        logger("nb_leverage.py - nb_check_liq_hit() - Liq Hit")
        return True
    else:
        logger("nb_leverage.py - nb_check_liq_hit() - No hit on liq price")
        return False
