import numpy as np
from numba import njit
from nb_quantfreedom.nb_enums import AccountState, CandleBodyType, LoggerFuncType, OrderResult, StringerFuncType
from nb_quantfreedom.nb_helper_funcs import price_getter, round_size_by_tick_step


@njit(cache=True)
def long_c_sl_hit(
    logger,
    current_candle: np.array,
    sl_price: float,
):
    logger[LoggerFuncType.Debug]("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - Starting")
    candle_low = price_getter(
        logger=logger,
        candle_body_type=CandleBodyType.Low,
        current_candle=current_candle,
    )
    if sl_price > candle_low:
        logger[LoggerFuncType.Debug]("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - Stop loss hit")
        return True
    else:
        logger[LoggerFuncType.Debug]("nb_stop_loss.py - nb_Long_StopLoss - check_stop_loss_hit() - No hit on stop loss")
        return False


@njit(cache=True)
def long_cm_sl_to_be_pass(
    logger,
    average_entry: float,
    can_move_sl_to_be: bool,
    candle_body_type: int,
    current_candle: np.array,
    zero_or_be_calc,
    sl_price: float,
    sl_to_be_move_when_pct: float,
    price_tick_step: float,
    market_fee_pct: float,
):
    """
    Long stop loss to break even pass
    """
    pass


@njit(cache=True)
def long_cm_sl_to_be(
    logger,
    stringer,
    average_entry: float,
    can_move_sl_to_be: bool,
    candle_body_type: int,
    current_candle: np.array,
    zero_or_entry_calc,
    sl_price: float,
    sl_to_be_move_when_pct: float,
    price_tick_step: float,
    market_fee_pct: float,
):
    if can_move_sl_to_be:
        logger[LoggerFuncType.Debug](
            "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - Might move sl to break even"
        )
        # Stop Loss to break even
        candle_body = price_getter(
            logger=logger,
            candle_body_type=candle_body_type,
            current_candle=current_candle,
        )
        pct_from_ae = (candle_body - average_entry) / average_entry
        logger[LoggerFuncType.Debug](
            "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - pct_from_ae= "
            + stringer[StringerFuncType.float_to_str](round(pct_from_ae * 100, 3))
        )
        move_sl = pct_from_ae > sl_to_be_move_when_pct
        if move_sl:
            old_sl = sl_price
            sl_price = zero_or_entry_calc(
                average_entry=average_entry,
                market_fee_pct=market_fee_pct,
                price_tick_step=price_tick_step,
            )
            logger[LoggerFuncType.Debug](
                "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - moving sl old_sl= "
                + stringer[StringerFuncType.float_to_str](old_sl)
                + " new sl= "
                + stringer[StringerFuncType.float_to_str](sl_price)
            )
            return sl_price
        else:
            logger[LoggerFuncType.Debug](
                "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - not moving sl to be"
            )
            pass
    else:
        logger[LoggerFuncType.Debug](
            "nb_stop_loss.py - nb_Long_StopLoss - check_move_stop_loss_to_be() - can't move sl to be"
        )
        pass


@njit(cache=True)
def long_cm_tsl_pass(
    logger,
    average_entry: float,
    candle_body_type: CandleBodyType,
    current_candle: np.array,
    sl_price: float,
    trail_sl_by_pct: float,
    trail_sl_when_pct: float,
    price_tick_step: float,
):
    pass


@njit(cache=True)
def long_cm_tsl(
    logger,
    stringer,
    average_entry: float,
    candle_body_type: CandleBodyType,
    current_candle: np.array,
    sl_price: float,
    trail_sl_by_pct: float,
    trail_sl_when_pct: float,
    price_tick_step: float,
):
    candle_body = price_getter(
        logger=logger,
        candle_body_type=candle_body_type,
        current_candle=current_candle,
    )
    pct_from_ae = (candle_body - average_entry) / average_entry
    logger[LoggerFuncType.Debug](
        "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - pct_from_ae= "
        + stringer[StringerFuncType.float_to_str](round(pct_from_ae * 100, 3))
    )
    possible_move_tsl = pct_from_ae > trail_sl_when_pct
    if possible_move_tsl:
        logger[LoggerFuncType.Debug](
            "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Maybe move tsl"
        )
        temp_sl_price = candle_body - candle_body * trail_sl_by_pct
        temp_sl_price = round_size_by_tick_step(
            user_num=temp_sl_price,
            exchange_num=price_tick_step,
        )
        logger[LoggerFuncType.Debug](
            "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - temp sl= "
            + stringer[StringerFuncType.float_to_str](temp_sl_price)
        )
        if temp_sl_price > sl_price:
            logger[LoggerFuncType.Debug](
                "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Moving tsl new sl= "
                + stringer[StringerFuncType.float_to_str](temp_sl_price)
                + " > old sl= "
                + stringer[StringerFuncType.float_to_str](sl_price)
            )
            return temp_sl_price
        else:
            logger[LoggerFuncType.Debug](
                "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Wont move tsl"
            )
            pass
    else:
        logger[LoggerFuncType.Debug](
            "nb_stop_loss.py - nb_Long_StopLoss - check_move_trailing_stop_loss() - Not moving tsl"
        )
        pass


@njit(cache=True)
def long_sl_bcb(
    bar_index: int,
    candles: np.array,
    logger,
    stringer,
    price_tick_step: float,
    sl_based_on_add_pct: float,
    sl_based_on_lookback: int,
    sl_bcb_price_getter,
    sl_bcb_type: int,
) -> float:
    """
    Long Stop Loss Based on Candle Body Calculator
    """
    # lb will be bar index if sl isn't based on lookback because look back will be 0
    lookback = max(bar_index - sl_based_on_lookback, 0)
    logger[LoggerFuncType.Debug](
        "nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - lookback= "
        + stringer[StringerFuncType.float_to_str](lookback)
    )
    candle_body = sl_bcb_price_getter(
        bar_index=bar_index,
        candles=candles,
        candle_body_type=sl_bcb_type,
        lookback=lookback,
    )
    logger[LoggerFuncType.Debug](
        "nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - candle_body= "
        + stringer[StringerFuncType.float_to_str](candle_body)
    )
    sl_price = candle_body - (candle_body * sl_based_on_add_pct)
    sl_price = round_size_by_tick_step(
        user_num=sl_price,
        exchange_num=price_tick_step,
    )
    logger[LoggerFuncType.Debug](
        "nb_stop_loss.py - nb_Long_SLBCB - calculate_stop_loss() - sl_price= "
        + stringer[StringerFuncType.float_to_str](sl_price)
    )
    return sl_price


@njit(cache=True)
def move_stop_loss(
    account_state: AccountState,
    bar_index: int,
    can_move_sl_to_be: bool,
    dos_index: int,
    ind_set_index: int,
    logger,
    stringer,
    order_result: OrderResult,
    order_status: int,
    sl_price: float,
    timestamp: int,
) -> OrderResult:
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
        possible_loss=account_state.possible_loss,
        realized_pnl=account_state.realized_pnl,
        total_trades=account_state.total_trades,
    )
    logger[LoggerFuncType.Debug]("nb_stop_loss.py - nb_MoveSL - move_stop_loss() - created account state")
    sl_pct = abs(round((order_result.average_entry - sl_price) / order_result.average_entry, 3))
    logger[LoggerFuncType.Debug](
        "nb_stop_loss.py - nb_MoveSL - move_stop_loss() - sl percent= "
        + stringer[StringerFuncType.float_to_str](sl_pct)
    )
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
    logger[LoggerFuncType.Debug]("nb_stop_loss.py - nb_MoveSL - move_stop_loss() - created order result")

    return account_state, order_result


@njit(cache=True)
def move_stop_loss_pass(
    account_state: AccountState,
    bar_index: int,
    can_move_sl_to_be: bool,
    dos_index: int,
    ind_set_index: int,
    logger,
    order_result: OrderResult,
    order_status: int,
    sl_price: float,
    timestamp: int,
) -> OrderResult:
    return None, None
