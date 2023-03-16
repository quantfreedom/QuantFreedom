"""
Testing the tester
"""

import numpy as np
from numba import literal_unroll, njit
from quantfreedom import _typing as tp

from quantfreedom.backtester.nb.helper_funcs import (
    to_1d_array_nb,
)
from quantfreedom.backtester.nb.execute_funcs import (
    process_order_nb,
    process_stops_nb,
    check_sl_tp_nb,
)
from quantfreedom.backtester.enums.enums import (
    cart_array_dt,
    ready_for_df,
    order_records_dt,
    log_records_dt,

    LeverageMode,
    OrderType,
    SizeType,
    SL_BE_or_Trail_BasedOn,

    AccountState,
    EntryOrder,
    OrderResult,
    StopsOrder,
    StaticVariables,
)


@njit(cache=True)
def simulate_from_signals(
    # entry info
    entries: tp.ArrayLike,
    open_price: tp.ArrayLike,

    # required account info
    equity: float,
    fee_pct: float,
    mmr: float,

    # required order
    lev_mode: int,
    order_type: int,
    size_type: int,

    # Price params
    high_price:  tp.Optional[tp.ArrayLike] = None,
    low_price:  tp.Optional[tp.ArrayLike] = None,
    close_price: tp.Optional[tp.ArrayLike] = None,

    # Order Params
    leverage_iso: tp.ArrayLike = np.nan,
    max_equity_risk_pct: tp.ArrayLike = np.nan,
    max_equity_risk_value: tp.ArrayLike = np.nan,
    max_lev: float = 100.,
    max_order_size_pct: float = 100.,
    min_order_size_pct: float = .01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.,
    size_pct: tp.ArrayLike = np.nan,
    size_value: tp.ArrayLike = np.nan,

    # Stop Losses
    sl_pcts: tp.ArrayLike = np.nan,
    sl_prices: tp.ArrayLike = np.nan,

    sl_to_be: tp.ArrayLike = False,
    sl_to_be_based_on: tp.ArrayLike = np.nan,
    sl_to_be_then_trail: tp.ArrayLike = np.nan,
    sl_to_be_trail_by_when_pct_from_avg_entry: tp.ArrayLike = np.nan,
    sl_to_be_when_pct_from_avg_entry: tp.ArrayLike = np.nan,
    sl_to_be_zero_or_entry: tp.ArrayLike = np.nan,

    # Trailing Stop Loss Params
    tsl_pcts: tp.ArrayLike = np.nan,
    tsl_prices: tp.ArrayLike = np.nan,

    tsl_true_or_false: tp.ArrayLike = False,
    tsl_based_on: tp.ArrayLike = np.nan,
    tsl_trail_by: tp.ArrayLike = np.nan,
    tsl_when_pct_from_avg_entry: tp.ArrayLike = np.nan,

    # Take Profit Params
    risk_rewards: tp.ArrayLike = np.nan,
    tp_pcts: tp.ArrayLike = np.nan,
    tp_prices: tp.ArrayLike = np.nan,

    # Record stops logs
    want_to_record_stops_log: bool = False,

    # Results Filters
    gains_pct_filter: float = -np.inf,
    total_trade_filter: int = 0,
):

    # static checks
    if equity < 0 or not np.isfinite(equity):
        raise ValueError("YOU HAVE NO MONEY!!!! You Broke!!!!")

    if fee_pct < 0 or not np.isfinite(fee_pct):
        raise ValueError("fee_pct must be finite")

    if mmr < 0 or not np.isfinite(mmr):
        raise ValueError("mmr must be finite")

    if not np.isfinite(max_lev) or 1 > max_lev > 100:
        raise ValueError(
            "max lev has to be between 1 and 100")

    if not np.isfinite(min_order_size_pct) or .01 > min_order_size_pct > 100:
        raise ValueError(
            "min_order_size_pct  has to be between .01 and 100")

    if not np.isfinite(max_order_size_pct) or min_order_size_pct > max_order_size_pct > 100:
        raise ValueError(
            "max_order_size_pct has to be between min_order_size_pct and 100")

    if not np.isfinite(min_order_size_value) or min_order_size_value < 1:
        raise ValueError(
            "min_order_size_value has to be between .01 and 1 min inf")

    if np.isnan(max_order_size_value) or max_order_size_value < min_order_size_value:
        raise ValueError(
            "max_order_size_value has to be > min_order_size_value")

    og_equity = equity
    fee_pct /= 100
    mmr /= 100
    max_order_size_pct /= 100
    min_order_size_pct /= 100

    static_variables = StaticVariables(
        fee_pct=fee_pct,
        lev_mode=lev_mode,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_pct=min_order_size_pct,
        min_order_size_value=min_order_size_value,
        mmr=mmr,
        size_type=size_type,

    )

    # Order Arrays
    leverage_iso_array = to_1d_array_nb(
        np.asarray(leverage_iso, dtype=np.float_))

    max_equity_risk_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(max_equity_risk_pct)/100, dtype=np.float_))

    max_equity_risk_value_array = to_1d_array_nb(
        np.asarray(max_equity_risk_value, dtype=np.float_))

    size_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(size_pct)/100, dtype=np.float_))

    size_value_array = to_1d_array_nb(
        np.asarray(size_value, dtype=np.float_))

    # Stop Loss Arrays
    sl_pcts_array = to_1d_array_nb(np.asarray(
        np.asarray(sl_pcts)/100, dtype=np.float_))

    sl_prices_array = to_1d_array_nb(np.asarray(sl_prices, dtype=np.float_))

    sl_to_be_array = to_1d_array_nb(np.asarray(sl_to_be, dtype=np.float_))

    sl_to_be_based_on_array = to_1d_array_nb(
        np.asarray(sl_to_be_based_on, dtype=np.float_))

    sl_to_be_then_trail_array = to_1d_array_nb(
        np.asarray(sl_to_be_then_trail, dtype=np.float_))

    sl_to_be_trail_by_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_trail_by_when_pct_from_avg_entry, dtype=np.float_))

    sl_to_be_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_to_be_when_pct_from_avg_entry)/100, dtype=np.float_))

    sl_to_be_zero_or_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_zero_or_entry, dtype=np.float_))

    # Trailing Stop Loss Arrays
    tsl_pcts_array = to_1d_array_nb(np.asarray(
        np.asarray(tsl_pcts)/100, dtype=np.float_))

    tsl_prices_array = to_1d_array_nb(
        np.asarray(tsl_prices, dtype=np.float_))

    tsl_based_on_array = to_1d_array_nb(
        np.asarray(tsl_based_on, dtype=np.float_))

    tsl_trail_by_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_trail_by)/100, dtype=np.float_))

    tsl_true_or_false_array = to_1d_array_nb(
        np.asarray(tsl_true_or_false, dtype=np.float_))

    tsl_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_when_pct_from_avg_entry)/100, dtype=np.float_))

    # Take Profit Arrays
    risk_rewards_array = to_1d_array_nb(
        np.asarray(risk_rewards, dtype=np.float_))

    tp_pcts_array = to_1d_array_nb(np.asarray(
        np.asarray(tp_pcts)/100, dtype=np.float_))

    tp_prices_array = to_1d_array_nb(np.asarray(tp_prices, dtype=np.float_))

    '''
    Check Params
    '''

    if np.isfinite(size_value_array).all():
        if size_value_array.any() < 1:
            raise ValueError("size_value must be greater than 1.")
        if size_value_array.any() > max_order_size_value:
            raise ValueError("size_value is greater than max_order_size_value")

        if size_value_array.any() < min_order_size_value:
            raise ValueError("size_value is greater than max_order_size_value")

    if not np.isfinite(size_pct_array).all():
        if size_pct_array.any() < 1:
            raise ValueError("size_pct must be greater than 1.")

        if size_pct_array.any() > max_order_size_pct:
            raise ValueError("size_pct is greater than max_order_size_pct")

        if size_pct_array.any() < min_order_size_pct:
            raise ValueError("size_pct is greater than max_order_size_pct")

    if np.isinf(sl_pcts_array).any() or sl_pcts_array.any() < 0:
        raise ValueError(
            "sl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(sl_prices_array).any() or sl_prices_array.any() < 0:
        raise ValueError(
            "sl_prices has to be nan or greater than 0 and not inf")

    if np.isinf(tsl_pcts_array).any() or tsl_pcts_array.any() < 0:
        raise ValueError(
            "tsl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(tsl_prices_array).any() or tsl_prices_array.any() < 0:
        raise ValueError(
            "tsl_prices has to be nan or greater than 0 and not inf")

    if np.isinf(tp_pcts_array).any() or tp_pcts_array.any() < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(tp_prices_array).any() or tp_prices_array.any() < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    if (0 > lev_mode > len(LeverageMode)) or not np.isfinite(lev_mode):
        raise ValueError(
            "leverage mode is out of range or not finite")

    check_sl_tsl_for_nan = (
        np.isnan(sl_pcts_array).any() and
        np.isnan(sl_prices_array).any() and (
            np.isnan(tsl_pcts_array).any() and
            np.isnan(tsl_prices_array).any())
    )

    # if leverage_iso is too big or too small
    if lev_mode == LeverageMode.Isolated:
        if not np.isfinite(leverage_iso_array).any() or (
            leverage_iso_array.any() > max_lev or
            leverage_iso_array.any() < 0
        ):
            raise ValueError(
                "leverage_iso needs to be between 1 and max lev")
    if lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise ValueError(
                "When using Least Free Cash Used set a proper sl or tsl > 0")
        if np.isfinite(leverage_iso_array).any():
            raise ValueError(
                "When using Least Free Cash Used leverage iso must be np.nan")

    # making sure we have a number greater than 0 for rr
    if np.isinf(risk_rewards_array).any() or risk_rewards_array.any() < 0:
        raise ValueError(
            "Risk Rewards has to be greater than 0 or np.nan")

    # check if RR has sl pct / price or tsl pct / price
    if not np.isnan(risk_rewards_array).any() and check_sl_tsl_for_nan:
        raise ValueError(
            "When risk to reward is set you have to have a sl or tsl > 0")

    if risk_rewards_array.any() > 0 and (
        np.isfinite(tp_pcts_array).any() or np.isfinite(tp_prices_array).any()
    ):
        raise ValueError(
            "You can't have take profits set when using Risk to reward")

    if np.isinf(max_equity_risk_pct_array).any() or max_equity_risk_pct_array.any() < 0:
        raise ValueError(
            "Max equity risk percent has to be greater than 0 or np.nan")

    elif np.isinf(max_equity_risk_value_array).any() or max_equity_risk_value_array.any() < 0:
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    if not np.isnan(max_equity_risk_pct_array).any() and not np.isnan(max_equity_risk_value_array).any():
        raise ValueError(
            "You can't have max risk pct and max risk value both set at the same time.")
    if not np.isnan(sl_pcts_array).any() and not np.isnan(sl_prices_array).any():
        raise ValueError(
            "You can't have sl pct and sl price both set at the same time.")
    if not np.isnan(tsl_pcts_array).any() and not np.isnan(tsl_prices_array).any():
        raise ValueError(
            "You can't have tsl pct and tsl price both set at the same time.")
    if not np.isnan(tp_pcts_array).any() and not np.isnan(tp_prices_array).any():
        raise ValueError(
            "You can't have tp pct and tp price both set at the same time.")
    if not np.isnan(size_value_array).any() and not np.isnan(size_pct_array).any():
        raise ValueError(
            "You can't have size and size pct set at the same time.")

    # simple check if order size type is valid
    if 0 > order_type > len(OrderType) or not np.isfinite(order_type):
        raise ValueError("order_type is invalid")

    # Getting the right size for Size Type Amount
    if size_type == SizeType.Amount:
        if np.isnan(size_value_array).any():
            raise ValueError(
                "With SizeType as amount, size_value must be 1 or greater.")

    if size_type == SizeType.PercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using percent of account.")

    # checking to see if you set a stop loss for risk based size types
    if size_type == SizeType.RiskAmount or (
            size_type == SizeType.RiskPercentOfAccount) and check_sl_tsl_for_nan:
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl or tsl > 0")

    # setting risk percent size
    if size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account.")

    if not np.isfinite(sl_to_be_array).any() or sl_to_be_array.any() < 0 or sl_to_be_array.any() > 1:
        raise ValueError(
            "sl_to_be needs to be true or false")

    # stop loss break even checks
    if np.isfinite(sl_to_be_based_on_array).any() and (
        sl_to_be_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price or
        sl_to_be_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums")

    if np.isfinite(sl_to_be_then_trail_array).any() and \
            sl_to_be_then_trail_array.any() < 0 or sl_to_be_then_trail_array.any() > 1:
        raise ValueError(
            "sl_to_be_then_trail needs to be true or false")

    if np.isinf(sl_to_be_trail_by_when_pct_from_avg_entry_array).any() or \
            sl_to_be_trail_by_when_pct_from_avg_entry_array.any() < 0:
        raise ValueError(
            "You need sl_to_be_trail_by_when_pct_from_avg_entry to be > 0 or not inf.")

    if np.isinf(sl_to_be_when_pct_from_avg_entry_array).any() or \
            sl_to_be_when_pct_from_avg_entry_array.any() < 0:
        raise ValueError(
            "You need sl_to_be_when_pct_from_avg_entry to be > 0 or not inf.")

    if sl_to_be_zero_or_entry_array.any() < 0 or sl_to_be_zero_or_entry_array.any() > 1:
        raise ValueError(
            "sl_to_be_zero_or_entry needs to be 0 for zero or 1 for entry")

    if sl_to_be_array.any() == False:
        if np.isfinite(sl_to_be_based_on_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_based_on.")
        if np.isfinite(sl_to_be_then_trail_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_then_trail.")
        if np.isfinite(sl_to_be_trail_by_when_pct_from_avg_entry_array).any():
            raise ValueError("sl_to_be needs to be True to use .")
        if np.isfinite(sl_to_be_trail_by_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_trail_by_when_pct_from_avg_entry.")
        if np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_when_pct_from_avg_entry.")
        if np.isfinite(sl_to_be_zero_or_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_zero_or_entry.")

    # trailing stop loss checks

    if not np.isfinite(tsl_true_or_false).any() or \
            tsl_true_or_false.any() < 0 or tsl_true_or_false.any() > 1:
        raise ValueError(
            "tsl_true_or_false needs to be true or false")

    if np.isfinite(tsl_based_on_array).any() and (
        tsl_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price or
        tsl_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need tsl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums")

    if np.isinf(tsl_trail_by_array).any() or \
            tsl_trail_by_array.any() < 0:
        raise ValueError(
            "You need tsl_trail_by to be > 0 or not inf.")

    if np.isinf(tsl_when_pct_from_avg_entry_array).any() or \
            tsl_when_pct_from_avg_entry_array.any() < 0:
        raise ValueError(
            "You need tsl_when_pct_from_avg_entry to be > 0 or not inf.")

    if tsl_true_or_false.any() == False:
        if np.isfinite(tsl_based_on_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_based_on.")
        if np.isfinite(tsl_trail_by_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_trail_by.")
        if np.isfinite(tsl_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_when_pct_from_avg_entry.")

    if want_to_record_stops_log != True and want_to_record_stops_log != False:
        raise ValueError(
            "want_to_record_stops_log needs to be true or false")

    if gains_pct_filter == np.inf:
        raise ValueError(
            "gains_pct_filter can't be inf")

    if total_trade_filter < 0 or not np.isfinite(total_trade_filter):
        raise ValueError(
            "total_trade_filter needs to be greater than 0")

    arrays = (
        leverage_iso_array,
        max_equity_risk_pct_array,
        max_equity_risk_value_array,
        risk_rewards_array,
        size_pct_array,
        size_value_array,
        sl_pcts_array,
        sl_prices_array,
        sl_to_be_array,
        sl_to_be_based_on_array,
        sl_to_be_then_trail_array,
        sl_to_be_trail_by_when_pct_from_avg_entry_array,
        sl_to_be_when_pct_from_avg_entry_array,
        sl_to_be_zero_or_entry_array,
        tp_pcts_array,
        tp_prices_array,
        tsl_based_on_array,
        tsl_pcts_array,
        tsl_prices_array,
        tsl_trail_by_array,
        tsl_true_or_false_array,
        tsl_when_pct_from_avg_entry_array,
    )

    n = 1
    for x in arrays:
        n *= x.size
    out = np.zeros((n, len(arrays)))
    cart_array = np.zeros(n, dtype=cart_array_dt)

    for i in range(len(arrays)):
        m = int(n / arrays[i].size)
        out[:n, i] = np.repeat(arrays[i], m)
        n //= arrays[i].size

    n = arrays[-1].size
    for k in range(len(arrays)-2, -1, -1):
        n *= arrays[k].size
        m = int(n / arrays[k].size)
        for j in range(1, arrays[k].size):
            out[j*m:(j+1)*m, k+1:] = out[0:m, k+1:]

    dtype_names = (
        'leverage_iso_array',
        'max_equity_risk_pct_array',
        'max_equity_risk_value_array',
        'risk_rewards_array',
        'size_pct_array',
        'size_value_array',
        'sl_pcts_array',
        'sl_prices_array',
        'sl_to_be_array',
        'sl_to_be_based_on_array',
        'sl_to_be_then_trail_array',
        'sl_to_be_trail_by_when_pct_from_avg_entry_array',
        'sl_to_be_when_pct_from_avg_entry_array',
        'sl_to_be_zero_or_entry_array',
        'tp_pcts_array',
        'tp_prices_array',
        'tsl_based_on_array',
        'tsl_pcts_array',
        'tsl_prices_array',
        'tsl_trail_by_array',
        'tsl_true_or_false_array',
        'tsl_when_pct_from_avg_entry_array',
    )
    counter = 0
    for dtype_name in literal_unroll(dtype_names):
        for col in range(n):
            cart_array[dtype_name][col] = out[col][counter]
        counter += 1

    # setting arrys as cart arrays
    leverage_iso_cart_array = cart_array['leverage_iso_array']
    max_equity_risk_pct_cart_array = cart_array['max_equity_risk_pct_array']
    max_equity_risk_value_cart_array = cart_array['max_equity_risk_value_array']
    risk_rewards_cart_array = cart_array['risk_rewards_array']
    size_pct_cart_array = cart_array['size_pct_array']
    size_value_cart_array = cart_array['size_value_array']
    sl_pcts_cart_array = cart_array['sl_pcts_array']
    sl_prices_cart_array = cart_array['sl_prices_array']
    sl_to_be_cart_array = np.asarray(
        cart_array['sl_to_be_array'], dtype=np.bool_)
    sl_to_be_based_on_cart_array = cart_array['sl_to_be_based_on_array']
    sl_to_be_then_trail_cart_array = np.asarray(
        cart_array['sl_to_be_then_trail_array'], dtype=np.bool_)
    sl_to_be_trail_by_when_pct_from_avg_entry_cart_array = cart_array[
        'sl_to_be_trail_by_when_pct_from_avg_entry_array']
    sl_to_be_when_pct_from_avg_entry_cart_array = cart_array[
        'sl_to_be_when_pct_from_avg_entry_array']
    sl_to_be_zero_or_entry_cart_array = cart_array['sl_to_be_zero_or_entry_array']
    tp_pcts_cart_array = cart_array['tp_pcts_array']
    tp_prices_cart_array = cart_array['tp_prices_array']
    tsl_based_on_cart_array = cart_array['tsl_based_on_array']
    tsl_pcts_cart_array = cart_array['tsl_pcts_array']
    tsl_prices_cart_array = cart_array['tsl_prices_array']
    tsl_trail_by_cart_array = cart_array['tsl_trail_by_array']
    tsl_true_or_false_cart_array = np.asarray(
        cart_array['tsl_true_or_false_array'], dtype=np.bool_)
    tsl_when_pct_from_avg_entry_cart_array = cart_array['tsl_when_pct_from_avg_entry_array']

    cart_array = counter = out = dtype_names = arrays = n = m = k = j = i = col = 0

    total_order_settings = sl_pcts_cart_array.shape[0]

    if entries.ndim == 1:
        total_indicator_settings = 1
    else:
        total_indicator_settings = entries.shape[1]

    total_bars = open_price.shape[0]

    # record_count = 0
    # for i in range(total_order_settings):
    #     for ii in range(total_indicator_settings):
    #         for iii in range(total_bars):
    #             if entries[:, ii][iii]:
    #                 record_count += 1
    # record_count = int(record_count / 2)

    df_array = np.empty(10000, dtype=ready_for_df)
    df_counter = 0

    order_records = np.empty(10000, dtype=order_records_dt)
    order_count_id = 0
    start_order_count = 0
    end_order_count = 0

    log_records = np.empty(100000, dtype=log_records_dt)
    log_count_id = 0
    start_log_count = 0
    end_log_count = 0

    col = -1  # TODO move this to the end of the for loop

    use_stops = not np.isnan(sl_pcts_array[0]) or \
        not np.isnan(tsl_pcts_array[0]) or \
        not np.isnan(tp_pcts_array[0])

    for order_settings_counter in range(total_order_settings):

        entry_order = EntryOrder(
            lev_mode=lev_mode,
            leverage_iso=leverage_iso_cart_array[order_settings_counter],
            max_equity_risk_pct=max_equity_risk_pct_cart_array[order_settings_counter],
            max_equity_risk_value=max_equity_risk_value_cart_array[order_settings_counter],
            max_lev=max_lev,
            max_order_size_pct=max_order_size_pct,
            max_order_size_value=max_order_size_value,
            min_order_size_pct=min_order_size_pct,
            min_order_size_value=min_order_size_value,
            order_type=order_type,
            risk_rewards=risk_rewards_cart_array[order_settings_counter],
            size_pct=size_pct_cart_array[order_settings_counter],
            size_value=size_value_cart_array[order_settings_counter],
            sl_pcts=sl_pcts_cart_array[order_settings_counter],
            sl_prices=sl_prices_cart_array[order_settings_counter],
            tp_pcts=tp_pcts_cart_array[order_settings_counter],
            tp_prices=tp_prices_cart_array[order_settings_counter],
            tsl_pcts=tsl_pcts_cart_array[order_settings_counter],
            tsl_prices=tsl_prices_cart_array[order_settings_counter],
        )
        stops_order = StopsOrder(
            sl_to_be=sl_to_be_cart_array[order_settings_counter],
            sl_to_be_based_on=sl_to_be_based_on_cart_array[order_settings_counter],
            sl_to_be_then_trail=sl_to_be_then_trail_cart_array[order_settings_counter],
            sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_cart_array[
                order_settings_counter],
            sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_cart_array[
                order_settings_counter],
            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_cart_array[order_settings_counter],

            tsl_based_on=tsl_based_on_cart_array[order_settings_counter],
            tsl_trail_by=tsl_trail_by_cart_array[order_settings_counter],
            tsl_true_or_false=tsl_true_or_false_cart_array[order_settings_counter],
            tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_cart_array[
                order_settings_counter],
        )

        for indicator_settings_counter in range(total_indicator_settings):

            if entries.ndim != 1:
                current_indicator_entries = entries[:,
                                                    indicator_settings_counter]
            else:
                current_indicator_entries = entries

            temp_order_records = np.empty(
                total_bars, dtype=order_records_dt)
            temp_log_records = np.empty(total_bars, dtype=log_records_dt)

            col += 1

            # Account State Reset
            account_state = AccountState(
                available_balance=og_equity,
                equity=og_equity,
                fee_pct=fee_pct,
                log_count_id=log_count_id,
                mmr=mmr,
                order_count_id=order_count_id,
            )

            log_order_records

            # Order Result Reset
            order_result = OrderResult()

            for bar in range(total_bars):

                if available_balance < 5:
                    break

                if current_indicator_entries[bar]:

                    # all returns will be called current so like sl_prices_current
                    available_balance, \
                        average_entry, \
                        cash_borrowed, \
                        cash_used, \
                        leverage_order_result, \
                        liq_price_order_result, \
                        log_count_id, \
                        log_records_filled, \
                        moved_sl_to_be_order_result, \
                        moved_tsl_order_result, \
                        order_count_id, \
                        order_records_filled, \
                        order_status_info_order_result, \
                        order_status_order_result, \
                        position, \
                        sl_pcts_order_result, \
                        sl_prices_order_result, \
                        tp_pcts_order_result, \
                        tp_prices_order_result, \
                        tsl_pcts_order_result, \
                        tsl_prices_order_result,\
                        = process_order_nb(
                            price=open_price[bar],

                            # Account
                            account_state=account_state,

                            # Order
                            entry_order=entry_order,
                            order_result=order_result,
                            static_variables=static_variables,

                            bar=bar,
                            col=col,
                            indicator_settings_counter=indicator_settings_counter,
                            order_settings_counter=order_settings_counter,

                            log_count_id=log_count_id,
                            log_records_filled=log_records_filled,
                            log_records=temp_log_records[log_records_filled],

                            order_count_id=order_count_id,
                            order_records_filled=order_records_filled,
                            order_records=temp_order_records[order_records_filled],
                        )
                if position > 0:
                    log_count_id, \
                        log_records_filled, \
                        moved_sl_to_be_order_result, \
                        moved_tsl_order_result, \
                        order_type_order_result, \
                        price_order_result, \
                        size_value_order_result, \
                        sl_prices_order_result, \
                        tsl_prices_order_result,\
                        = check_sl_tp_nb(
                            average_entry=average_entry,
                            high_price=high_price[bar],
                            low_price=low_price[bar],
                            open_price=open_price[bar],
                            close_price=close_price[bar],
                            fee_pct=fee_pct,
                            order_type=order_type,
                            liq_price=liq_price,

                            sl_prices=sl_prices_order_result,
                            tsl_prices=tsl_prices_order_result,
                            tp_prices=tp_prices_order_result,

                            moved_sl_to_be=moved_sl_to_be_order_result,
                            sl_to_be=sl_to_be_order,
                            sl_to_be_based_on=sl_to_be_based_on_order,
                            sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_order,
                            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_order,
                            want_to_record_stops_log=want_to_record_stops_log,

                            moved_tsl=moved_tsl_order_result,
                            tsl_based_on=tsl_based_on_order,
                            tsl_true_or_false=tsl_true_or_false_order,
                            tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_order,
                            tsl_trail_by=tsl_trail_by_order,

                            # only needed if checking stops movement
                            bar=bar,
                            col=col,
                            log_count_id=log_count_id,
                            log_records=temp_log_records[log_records_filled],
                            log_records_filled=log_records_filled,
                            order_count_id=order_count_id,
                        )
                    if not np.isnan(size_value_order_result):
                        pass
                        # available_balance, \
                        #     cash_borrowed, \
                        #     cash_used, \
                        #     equity, \
                        #     fees_paid, \
                        #     liq_price, \
                        #     log_count_id, \
                        #     log_records_filled, \
                        #     order_count_id, \
                        #     order_records_filled, \
                        #     order_status_info, \
                        #     order_status, \
                        #     position, \
                        #     realized_pnl, \
                        #         = process_stops_nb(

                        #         )
            gains_pct = ((equity - og_equity) / og_equity) * 100
            if gains_pct > gains_pct_filter:
                temp_order_records = temp_order_records[:order_records_filled]
                temp_log_records = temp_log_records[:log_records_filled]
                w_l = temp_order_records['real_pnl'][~np.isnan(
                    temp_order_records['real_pnl'])]
                if w_l.size > total_trade_filter:

                    w_l_no_be = w_l[w_l != 0]  # filter out all BE trades

                    end_order_count += order_records_filled
                    order_records[start_order_count: end_order_count] = temp_order_records
                    start_order_count = end_order_count

                    end_log_count += log_records_filled
                    log_records[start_log_count: end_log_count] = temp_log_records
                    start_log_count = end_log_count

                    # win rate calc
                    win_loss = np.where(w_l_no_be < 0, 0, 1)
                    win_rate = round(np.count_nonzero(
                        win_loss) / win_loss.size * 100, 2)

                    total_pnl = temp_order_records['real_pnl'][~np.isnan(
                        temp_order_records['real_pnl'])].sum()

                    # to_the_upside calculation
                    x = np.arange(1, len(w_l_no_be)+1)
                    y = w_l_no_be.cumsum()

                    xm = x.mean()
                    ym = y.mean()

                    y_ym = y - ym
                    y_ym_s = y_ym**2

                    x_xm = x - xm
                    x_xm_s = x_xm**2

                    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
                    b0 = ym - b1 * xm

                    y_pred = b0 + b1 * x

                    yp_ym = y_pred - ym

                    yp_ym_s = yp_ym**2
                    to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

                    df_array['or_set'][df_counter] = temp_order_records['or_set'][0]
                    df_array['ind_set'][df_counter] = temp_order_records['ind_set'][0]
                    df_array['total_trades'][df_counter] = w_l.size
                    df_array['total_BE'][df_counter] = w_l[w_l == 0].size
                    df_array['gains_pct'][df_counter] = gains_pct
                    df_array['win_rate'][df_counter] = win_rate
                    df_array['to_the_upside'][df_counter] = to_the_upside
                    df_array['total_fees'][df_counter] = temp_order_records['fees'].sum()
                    df_array['total_pnl'][df_counter] = total_pnl
                    df_array['ending_eq'][df_counter] = temp_order_records['equity'][-1]
                    df_array['sl_pct'][df_counter] = temp_order_records['sl_pct'][0] * 100
                    df_array['rr'][df_counter] = temp_order_records['rr'][0]
                    df_array['max_eq_risk_pct'][df_counter] = temp_order_records['max_eq_risk_pct'][0] * 100
                    df_counter += 1

    return df_array[: df_counter], order_records[: end_order_count], log_records[: end_log_count]
