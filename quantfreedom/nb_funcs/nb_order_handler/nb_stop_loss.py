from typing import Callable
import numpy as np
from numba import njit

from quantfreedom.nb_funcs.nb_helper_funcs import nb_round_size_by_tick_step
from quantfreedom.core.enums import AccountState, CandleBodyType, LoggerFuncType, OrderResult, StringerFuncType


##############################################
##############################################
##############################################
##############################################
##############################################
# functions
##############################################
##############################################
##############################################
##############################################
##############################################
@njit(cache=True)
def nb_sl_to_entry(
    average_entry: float,
    market_fee_pct: float,
    price_tick_step: float,
):
    sl_price = average_entry
    return sl_price


@njit(cache=True)
def nb_sl_based_on_candle_body(
    bar_index: int,
    candles: FootprintCandlesTuple,
    logger,
    nb_sl_bcb_price_getter,
    nb_sl_price_calc,
    price_tick_step: float,
    sl_based_on_add_pct: float,
    sl_based_on_lookback: int,
    sl_bcb_type: CandleBodyType,
    stringer,
):
    """
    Long Stop Loss Based on Candle Body Calculator
    """
    # lb will be bar index if sl isn't based on lookback because look back will be 0
    lookback = max(bar_index - sl_based_on_lookback, 0)
    logger("nb_stop_loss.py - sl_bcb() - lookback to index= " + stringer[StringerFuncType.float_to_str](lookback))
    candle_body = nb_sl_bcb_price_getter(
        bar_index=bar_index,
        candles=candles,
        candle_body_type=sl_bcb_type,
        lookback=lookback,
    )
    logger("nb_stop_loss.py - sl_bcb() - candle_body= " + stringer[StringerFuncType.float_to_str](candle_body))
    sl_price = nb_sl_price_calc(
        add_pct=sl_based_on_add_pct,
        candle_body=candle_body,
    )
    sl_price = nb_round_size_by_tick_step(
        exchange_num=price_tick_step,
        user_num=sl_price,
    )
    logger("nb_stop_loss.py - sl_bcb() - sl_price= " + stringer[StringerFuncType.float_to_str](sl_price))
    return sl_price


@njit(cache=True)
def nb_check_sl_hit(
    current_candle: CurrentFootprintCandleTuple,
    logger,
    nb_sl_hit_bool,
    sl_price: float,
    stringer,
):
    logger("nb_stop_loss.py - c_sl_hit() - Starting")
    if nb_sl_hit_bool(
        current_candle=current_candle,
        logger=logger,
        sl_price=sl_price,
        stringer=stringer,
    ):
        logger("nb_stop_loss.py - c_sl_hit() - Stop loss hit")
        return True
    else:
        logger("nb_stop_loss.py - c_sl_hit() - No hit on stop loss")
        return False


@njit(cache=True)
def nb_check_move_sl_to_be(
    average_entry: float,
    can_move_sl_to_be: bool,
    current_candle: CurrentFootprintCandleTuple,
    logger,
    market_fee_pct: float,
    nb_move_sl_bool,
    nb_zero_or_entry_calc,
    price_tick_step: float,
    sl_price: float,
    sl_to_be_cb_type: CandleBodyType,
    sl_to_be_when_pct: float,
    stringer,
):
    """
    Checking to see if we move the stop loss to break even
    """
    if can_move_sl_to_be:
        logger("nb_stop_loss.py - cm_sl_to_be() - Might move sl to break even")
        # Stop Loss to break even
        candle_body = current_candle[sl_to_be_cb_type]
        pct_from_ae = abs(candle_body - average_entry) / average_entry
        logger(
            "nb_stop_loss.py - cm_sl_to_be() - pct_from_ae= "
            + stringer[StringerFuncType.float_to_str](round(pct_from_ae * 100, 3))
        )
        move_sl = nb_move_sl_bool(
            num_1=pct_from_ae,
            num_2=sl_to_be_when_pct,
        )
        if move_sl:
            old_sl = sl_price
            sl_price = nb_zero_or_entry_calc(
                average_entry=average_entry,
                market_fee_pct=market_fee_pct,
                price_tick_step=price_tick_step,
            )
            sl_pct = round(abs(average_entry - sl_price) / average_entry, 3)
            logger(
                "nb_stop_loss.py - cm_sl_to_be() - moving sl old_sl= "
                + stringer[StringerFuncType.float_to_str](old_sl)
                + " new sl= "
                + stringer[StringerFuncType.float_to_str](sl_price)
                + " new sl pct= "
                + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
            )
            return sl_price, sl_pct
        else:
            logger("nb_stop_loss.py - cm_sl_to_be() - not moving sl to be")
            0.0, 0.0
    else:
        logger("nb_stop_loss.py - cm_sl_to_be() - can't move sl to be")
        0.0, 0.0


@njit(cache=True)
def nb_move_stop_loss(
    account_state: AccountState,
    bar_index: int,
    can_move_sl_to_be: bool,
    dos_index: int,
    ind_set_index: int,
    logger,
    order_result: OrderResult,
    order_status: int,
    sl_pct: float,
    sl_price: float,
    timestamp: int,
):
    account_state = AccountState(
        # where we are at
        ind_set_index=ind_set_index,
        dos_index=dos_index,
        bar_index=bar_index,
        timestamp=timestamp,
        # account info
        available_balance=account_state.available_balance,
        cash_borrowed=account_state.cash_borrowed,
        cash_used=account_state.cash_used,
        equity=account_state.equity,
        fees_paid=account_state.fees_paid,
        total_possible_loss=account_state.total_possible_loss,
        realized_pnl=account_state.realized_pnl,
        total_trades=account_state.total_trades,
    )
    logger("nb_stop_loss.py - nb_move_stop_loss() - created account state")
    order_result = OrderResult(
        average_entry=order_result.average_entry,
        can_move_sl_to_be=can_move_sl_to_be,
        entry_price=order_result.entry_price,
        entry_size_asset=order_result.entry_size_asset,
        entry_size_usd=order_result.entry_size_usd,
        exit_price=order_result.exit_price,
        leverage=order_result.leverage,
        liq_price=order_result.liq_price,
        order_status=order_status,
        position_size_asset=order_result.position_size_asset,
        position_size_usd=order_result.position_size_usd,
        sl_pct=sl_pct,
        sl_price=sl_price,
        tp_pct=order_result.tp_pct,
        tp_price=order_result.tp_price,
    )
    logger("nb_stop_loss.py - nb_move_stop_loss() - created order result")

    return account_state, order_result


@njit(cache=True)
def nb_check_move_tsl(
    average_entry: float,
    current_candle: CurrentFootprintCandleTuple,
    logger,
    nb_move_sl_bool,
    nb_sl_price_calc,
    price_tick_step: float,
    sl_price: float,
    stringer,
    trail_sl_bcb_type: CandleBodyType,
    trail_sl_by_pct: float,
    trail_sl_when_pct: float,
):
    """
    Checking to see if we move the trailing stop loss
    """
    candle_body = current_candle[trail_sl_bcb_type]
    pct_from_ae = abs(candle_body - average_entry) / average_entry
    logger(
        "nb_stop_loss.py - cm_tsl() - pct_from_ae= "
        + stringer[StringerFuncType.float_to_str](round(pct_from_ae * 100, 3))
    )
    possible_move_tsl = nb_move_sl_bool(
        num_1=pct_from_ae,
        num_2=trail_sl_when_pct,
    )
    if possible_move_tsl:
        logger("nb_stop_loss.py - cm_tsl() - Maybe move tsl")
        temp_sl_price = nb_sl_price_calc(
            add_pct=trail_sl_by_pct,
            candle_body=candle_body,
        )
        temp_sl_price = nb_round_size_by_tick_step(
            exchange_num=price_tick_step,
            user_num=temp_sl_price,
        )
        logger(
            "nb_stop_loss.py - cm_tsl() - "
            + "temp sl= "
            + stringer[StringerFuncType.float_to_str](temp_sl_price)
            + " sl= "
            + stringer[StringerFuncType.float_to_str](sl_price)
        )
        if nb_move_sl_bool(
            num_1=temp_sl_price,
            num_2=sl_price,
        ):
            sl_pct = round(abs(average_entry - temp_sl_price) / average_entry, 3)
            logger(
                "nb_stop_loss.py - cm_tsl() - Moving tsl new sl= "
                + stringer[StringerFuncType.float_to_str](temp_sl_price)
                + " > old sl= "
                + stringer[StringerFuncType.float_to_str](sl_price)
                + " new sl pct= "
                + stringer[StringerFuncType.float_to_str](round(sl_pct * 100, 3))
            )
            return temp_sl_price, sl_pct
        else:
            logger("nb_stop_loss.py - cm_tsl() - Wont move tsl")
            return 0.0, 0.0
    else:
        logger("nb_stop_loss.py - cm_tsl() - Not moving tsl")
        return 0.0, 0.0


##############################################
##############################################
##############################################
##############################################
##############################################
# Long Functions
##############################################
##############################################
##############################################
##############################################
##############################################
@njit(cache=True)
def nb_long_sl_price_calc(
    add_pct: float,
    candle_body: float,
):
    sl_price = candle_body - (candle_body * add_pct)
    return sl_price


@njit(cache=True)
def nb_long_sl_to_zero(
    average_entry: float,
    market_fee_pct: float,
    price_tick_step: float,
):
    sl_price = (average_entry + market_fee_pct * average_entry) / (1 - market_fee_pct)
    sl_price = nb_round_size_by_tick_step(
        exchange_num=price_tick_step,
        user_num=sl_price,
    )
    return sl_price


@njit(cache=True)
def nb_num_greater_than_num(
    num_1: float,
    num_2: float,
):
    return num_1 > num_2


@njit(cache=True)
def nb_long_sl_hit_bool(
    current_candle: CurrentFootprintCandleTuple,
    logger,
    sl_price: float,
    stringer,
):
    candle_low = current_candle[CandleBodyType.Low]
    logger(
        "nb_stop_loss.py - nb_long_sl_hit_bool() - candle_low= " + stringer[StringerFuncType.float_to_str](candle_low)
    )
    return sl_price > candle_low


##############################################
##############################################
##############################################
##############################################
##############################################
# Short Functions
##############################################
##############################################
##############################################
##############################################
##############################################
@njit(cache=True)
def nb_short_sl_price_calc(
    add_pct: float,
    candle_body: float,
):
    sl_price = candle_body + (candle_body * add_pct)
    return sl_price


@njit(cache=True)
def nb_short_sl_to_zero(
    average_entry: float,
    market_fee_pct: float,
    price_tick_step: float,
):
    sl_price = (average_entry - market_fee_pct * average_entry) / (1 + market_fee_pct)
    sl_price = nb_round_size_by_tick_step(
        exchange_num=price_tick_step,
        user_num=sl_price,
    )
    return sl_price


@njit(cache=True)
def nb_short_sl_hit_bool(
    current_candle: CurrentFootprintCandleTuple,
    logger,
    sl_price: float,
    stringer,
):
    candle_high = current_candle[CandleBodyType.High]
    logger(
        "nb_stop_loss.py - nb_short_sl_hit_bool() - candle_high= "
        + stringer[StringerFuncType.float_to_str](candle_high)
    )
    return sl_price < candle_high


@njit(cache=True)
def nb_num_less_than_num(
    num_1: float,
    num_2: float,
):
    return num_1 < num_2


##############################################
##############################################
##############################################
##############################################
##############################################
# price getter
##############################################
##############################################
##############################################
##############################################
##############################################
@njit(cache=True)
def nb_min_price_getter(
    bar_index: int,
    candles: FootprintCandlesTuple,
    candle_body_type: CandleBodyType,
    lookback: int,
):
    price = candles[lookback : bar_index + 1 :, candle_body_type].min()
    return price


@njit(cache=True)
def nb_max_price_getter(
    bar_index: int,
    candles: FootprintCandlesTuple,
    candle_body_type: CandleBodyType,
    lookback: int,
):
    price = candles[lookback : bar_index + 1 :, candle_body_type].max()
    return price


##############################################
##############################################
##############################################
##############################################
##############################################
# PASSING
##############################################
##############################################
##############################################
##############################################
##############################################


@njit(cache=True)
def nb_sl_to_z_e_pass(
    average_entry: float,
    market_fee_pct: float,
    price_tick_step: float,
):
    pass


@njit(cache=True)
def nb_cm_sl_to_be_pass(
    average_entry: float,
    can_move_sl_to_be: bool,
    current_candle: CurrentFootprintCandleTuple,
    logger,
    market_fee_pct: float,
    nb_move_sl_bool,
    nb_zero_or_entry_calc,
    price_tick_step: float,
    sl_price: float,
    sl_to_be_cb_type: CandleBodyType,
    sl_to_be_when_pct: float,
    stringer,
):
    """
    Long stop loss to break even pass
    """
    return 0.0, 0.0


@njit(cache=True)
def nb_cm_tsl_pass(
    average_entry: float,
    current_candle: CurrentFootprintCandleTuple,
    logger,
    nb_move_sl_bool,
    nb_sl_price_calc,
    price_tick_step: float,
    sl_price: float,
    stringer,
    trail_sl_bcb_type: CandleBodyType,
    trail_sl_by_pct: float,
    trail_sl_when_pct: float,
):
    return 0.0, 0.0


@njit(cache=True)
def nb_move_stop_loss_pass(
    account_state: AccountState,
    bar_index: int,
    can_move_sl_to_be: bool,
    dos_index: int,
    ind_set_index: int,
    logger,
    order_result: OrderResult,
    order_status: int,
    sl_pct: float,
    sl_price: float,
    timestamp: int,
):
    return account_state, order_result


@njit(cache=True)
def nb_sl_calculator_pass(
    bar_index: int,
    candles: FootprintCandlesTuple,
    logger,
    nb_sl_bcb_price_getter,
    nb_sl_price_calc,
    price_tick_step: float,
    sl_based_on_add_pct: float,
    sl_based_on_lookback: int,
    sl_bcb_type: CandleBodyType,
    stringer,
):
    pass


@njit(cache=True)
def nb_check_sl_hit_pass(
    current_candle: CurrentFootprintCandleTuple,
    logger,
    nb_sl_hit_bool,
    sl_price: float,
    stringer,
):
    pass


@njit(cache=True)
def nb_price_getter_pass(
    bar_index: int,
    candles: FootprintCandlesTuple,
    candle_body_type: CandleBodyType,
    lookback: int,
):
    pass
