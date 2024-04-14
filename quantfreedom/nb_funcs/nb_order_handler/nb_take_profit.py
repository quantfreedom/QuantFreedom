from typing import Callable
import numpy as np
from numba import njit

from quantfreedom.nb_funcs.nb_helper_funcs import nb_round_size_by_tick_step
from quantfreedom.core.enums import CandleBodyType, LoggerFuncType, StringerFuncType


@njit(cache=True)
def nb_short_tp_price(
    average_entry: float,
    market_fee_pct: float,
    position_size_usd: float,
    profit: float,
    tp_fee_pct: float,
):
    # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(e-t%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p?or=input

    tp_price = -(
        (profit * average_entry)
        - (average_entry * position_size_usd)
        + (average_entry * market_fee_pct * position_size_usd)
    ) / (position_size_usd * (1 + tp_fee_pct))
    return tp_price


@njit(cache=True)
def nb_short_tp_hit_bool(
    current_candle: np.array,
    logger,
    stringer,
    tp_price: float,
):
    candle_low = current_candle[CandleBodyType.Low]
    logger(
        "nb_take_profit.py - nb_short_c_tp_candle() - candle_low= "
        + stringer[StringerFuncType.float_to_str](candle_low)
    )
    return tp_price > candle_low


@njit(cache=True)
def nb_long_tp_price(
    average_entry: float,
    market_fee_pct: float,
    position_size_usd: float,
    profit: float,
    tp_fee_pct: float,
):
    # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(t-e%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p

    tp_price = (
        (profit * average_entry)
        + (average_entry * position_size_usd)
        + (average_entry * market_fee_pct * position_size_usd)
    ) / (position_size_usd * (1 - tp_fee_pct))
    return tp_price


@njit(cache=True)
def nb_long_tp_hit_bool(
    current_candle: np.array,
    logger,
    stringer,
    tp_price: float,
):
    candle_high = current_candle[CandleBodyType.High]
    logger(
        "nb_take_profit.py - nb_long_c_tp_candle() - candle_high= "
        + stringer[StringerFuncType.float_to_str](candle_high)
    )
    return tp_price < candle_high


@njit(cache=True)
def nb_tp_rr(
    average_entry: float,
    logger,
    market_fee_pct: float,
    nb_get_tp_price,
    position_size_usd: float,
    total_possible_loss: float,
    price_tick_step: float,
    risk_reward: float,
    stringer,
    tp_fee_pct: float,
):
    profit = -total_possible_loss * risk_reward
    logger("nb_take_profit.py - nb_tp_rr() - profit= " + stringer[StringerFuncType.float_to_str](profit))
    tp_price = nb_get_tp_price(
        average_entry=average_entry,
        market_fee_pct=market_fee_pct,
        position_size_usd=position_size_usd,
        profit=profit,
        tp_fee_pct=tp_fee_pct,
    )

    tp_price = nb_round_size_by_tick_step(
        exchange_num=price_tick_step,
        user_num=tp_price,
    )
    logger("nb_take_profit.py - nb_tp_rr() - tp_price= " + stringer[StringerFuncType.float_to_str](tp_price))

    tp_pct = round(abs(tp_price - average_entry) / average_entry, 3)
    logger(
        "nb_take_profit.py - nb_tp_rr() - tp_pct= " + stringer[StringerFuncType.float_to_str](round(tp_pct * 100, 3))
    )
    can_move_sl_to_be = True
    logger("nb_take_profit.py - nb_tp_rr() - can_move_sl_to_be= True")
    return (
        can_move_sl_to_be,
        tp_price,
        tp_pct,
    )


@njit(cache=True)
def nb_c_tp_hit_regular(
    current_candle: np.array,
    logger,
    nb_tp_hit_bool,
    stringer,
    tp_price: float,
):
    if nb_tp_hit_bool(
        current_candle=current_candle,
        logger=logger,
        stringer=stringer,
        tp_price=tp_price,
    ):
        logger("nb_take_profit.py - nb_c_tp_hit_regular() - TP Hit")
        return True
    else:
        logger("nb_take_profit.py - nb_c_tp_hit_regular() - No Tp Hit")
        return False


@njit(cache=True)
def nb_c_tp_hit_provided(
    current_candle: np.array,
    logger,
    nb_tp_hit_bool,
    stringer,
    tp_price: float,
):
    if not np.isnan(tp_price):
        logger(
            "nb_take_profit.py - nb_c_tp_hit_provided() - Tp Hit Exit Price= "
            + stringer[StringerFuncType.float_to_str](tp_price)
        )
        return True
    else:
        logger("nb_take_profit.py - nb_c_tp_hit_provided() - No Tp Hit")
        return False
