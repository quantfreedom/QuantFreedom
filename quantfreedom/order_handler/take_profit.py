import numpy as np
from numba import njit

from quantfreedom.helper_funcs import round_size_by_tick_step
from quantfreedom.enums import CandleBodyType, LoggerFuncType, StringerFuncType


@njit(cache=True)
def long_tp_rr(
    logger,
    stringer,
    average_entry: float,
    market_fee_pct: float,
    position_size_usd: float,
    possible_loss: float,
    price_tick_step: float,
    risk_reward: float,
    tp_fee_pct: float,
):
    profit = possible_loss * risk_reward
    logger[LoggerFuncType.Debug](
        "take_profit.py - calculate_take_profit() - profit= "
        + stringer[StringerFuncType.float_to_str](profit)
    )
    tp_price = (
        (profit * average_entry)
        + (average_entry * position_size_usd)
        + (average_entry * market_fee_pct * position_size_usd)
    ) / (position_size_usd * (1 - tp_fee_pct))

    tp_price = round_size_by_tick_step(
        user_num=tp_price,
        exchange_num=price_tick_step,
    )
    logger[LoggerFuncType.Debug](
        "take_profit.py - calculate_take_profit() - tp_price= "
        + stringer[StringerFuncType.float_to_str](tp_price)
    )
    # https://www.symbolab.com/solver/simplify-calculator/solve%20for%20t%2C%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%20%5Ccdot%5Cleft(t-e%5Cright)%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20e%20%5Ccdot%20m%5Cright)%20-%20%5Cleft(%5Cleft(%5Cfrac%7Bs%7D%7Be%7D%5Cright)%5Ccdot%20t%20%5Ccdot%20%20l%5Cright)%20%3D%20p

    tp_pct = round((tp_price - average_entry) / average_entry, 3)
    logger[LoggerFuncType.Debug](
        "take_profit.py - calculate_take_profit() - tp_pct= "
        + stringer[StringerFuncType.float_to_str](round(tp_pct * 100, 3))
    )
    can_move_sl_to_be = True
    logger[LoggerFuncType.Debug]("take_profit.py - calculate_take_profit() - can_move_sl_to_be= True")
    return (
        can_move_sl_to_be,
        tp_price,
        tp_pct,
    )


@njit(cache=True)
def long_c_tp_hit_regular(
    logger,
    stringer,
    current_candle: np.array,
    tp_price: float,
):
    candle_high = current_candle[CandleBodyType.High]
    logger[LoggerFuncType.Debug](
        "take_profit.py - long_c_tp_hit_regular() - candle_high= "
        + stringer[StringerFuncType.float_to_str](candle_high)
    )
    if tp_price < candle_high:
        logger[LoggerFuncType.Debug]("take_profit.py - long_c_tp_hit_regular() - TP Hit")
        return True
    else:
        logger[LoggerFuncType.Debug]("take_profit.py - long_c_tp_hit_regular() - No Tp Hit")
        return False


@njit(cache=True)
def long_c_tp_hit_provided(
    logger,
    stringer,
    current_candle: np.array,
    tp_price: float,
):
    if not np.isnan(tp_price):
        logger[LoggerFuncType.Debug](
            "take_profit.py - long_c_tp_hit_provided() - Tp Hit Exit Price= "
            + stringer[StringerFuncType.float_to_str](tp_price)
        )
        return True
    else:
        logger[LoggerFuncType.Debug]("take_profit.py - long_c_tp_hit_provided() - No Tp Hit")
        return False
