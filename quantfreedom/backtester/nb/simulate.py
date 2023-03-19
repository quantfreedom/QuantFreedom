"""
Testing the tester
"""

import numpy as np
from numba import literal_unroll, njit
from quantfreedom._typing import PossibleArray
from quantfreedom.backtester.nb.execute_funcs import (
    process_order_nb,
    check_sl_tp_nb,
    to_1d_array_nb,
)
from quantfreedom.backtester.enums.enums import (
    cart_array_dt,
    df_array_dt,
    or_dt,

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
    entries: PossibleArray,
    open_prices: PossibleArray,
    high_prices: PossibleArray,
    low_prices: PossibleArray,
    close_prices: PossibleArray,

    # required account info
    equity: float,
    fee_pct: float,
    mmr: float,

    # required order
    lev_mode: int,
    order_type: int,
    size_type: int,

    # Order Params
    leverage: PossibleArray = np.nan,
    max_equity_risk_pct: PossibleArray = np.nan,
    max_equity_risk_value: PossibleArray = np.nan,
    max_lev: float = 100.,
    max_order_size_pct: float = 100.,
    min_order_size_pct: float = .01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.,
    size_pct: PossibleArray = np.nan,
    size_value: PossibleArray = np.nan,

    # Stop Losses
    sl_pcts: PossibleArray = np.nan,

    sl_to_be: bool = False,
    sl_to_be_based_on: PossibleArray = np.nan,
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan,
    sl_to_be_zero_or_entry: PossibleArray = np.nan,
    sl_to_be_then_trail: bool = False,
    sl_to_be_trail_by_when_pct_from_avg_entry: PossibleArray = np.nan,

    # Trailing Stop Loss Params
    tsl_pcts_init: PossibleArray = np.nan,

    tsl_true_or_false: bool = False,
    tsl_based_on: PossibleArray = np.nan,
    tsl_trail_by_pct: PossibleArray = np.nan,
    tsl_when_pct_from_avg_entry: PossibleArray = np.nan,

    # Take Profit Params
    risk_rewards: PossibleArray = np.nan,
    tp_pcts: PossibleArray = np.nan,

    # Results Filters
    gains_pct_filter: float = -np.inf,
    total_trade_filter: int = 0,
):

    # Static checks
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

    if gains_pct_filter == np.inf:
        raise ValueError(
            "gains_pct_filter can't be inf")

    if total_trade_filter < 0 or not np.isfinite(total_trade_filter):
        raise ValueError(
            "total_trade_filter needs to be greater than 0")

    if sl_to_be == True and tsl_true_or_false == True:
        raise ValueError(
            "You can't have sl_to_be and tsl_true_or_false both be true")

    if sl_to_be != True and sl_to_be != False:
        raise ValueError(
            "sl_to_be needs to be true or false")

    if sl_to_be_then_trail != True and sl_to_be_then_trail != False:
        raise ValueError(
            "sl_to_be_then_trail needs to be true or false")

    if tsl_true_or_false != True and tsl_true_or_false != False:
        raise ValueError(
            "tsl_true_or_false needs to be true or false")

    # Static variables creation
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
    leverage_array = to_1d_array_nb(
        np.asarray(leverage, dtype=np.float_))

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

    sl_to_be_based_on_array = to_1d_array_nb(
        np.asarray(sl_to_be_based_on, dtype=np.float_))

    sl_to_be_trail_by_when_pct_from_avg_entry_array = to_1d_array_nb(np.asarray(
        np.asarray(sl_to_be_trail_by_when_pct_from_avg_entry)/100, dtype=np.float_))

    sl_to_be_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_to_be_when_pct_from_avg_entry)/100, dtype=np.float_))

    sl_to_be_zero_or_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_zero_or_entry, dtype=np.float_))

    # Trailing Stop Loss Arrays
    tsl_pcts_init_array = to_1d_array_nb(np.asarray(
        np.asarray(tsl_pcts_init)/100, dtype=np.float_))

    tsl_based_on_array = to_1d_array_nb(
        np.asarray(tsl_based_on, dtype=np.float_))

    tsl_trail_by_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_trail_by_pct)/100, dtype=np.float_))

    tsl_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_when_pct_from_avg_entry)/100, dtype=np.float_))

    # Take Profit Arrays
    risk_rewards_array = to_1d_array_nb(
        np.asarray(risk_rewards, dtype=np.float_))

    tp_pcts_array = to_1d_array_nb(np.asarray(
        np.asarray(tp_pcts)/100, dtype=np.float_))

    # Checking all new arrays
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

    if np.isinf(tsl_pcts_init_array).any() or tsl_pcts_init_array.any() < 0:
        raise ValueError(
            "tsl_pcts_init has to be nan or greater than 0 and not inf")

    if np.isinf(tp_pcts_array).any() or tp_pcts_array.any() < 0:
        raise ValueError(
            "tp_pcts has to be nan or greater than 0 and not inf")

    if (0 > lev_mode > len(LeverageMode)) or not np.isfinite(lev_mode):
        raise ValueError(
            "leverage mode is out of range or not finite")

    check_sl_tsl_for_nan = (
        np.isnan(sl_pcts_array).any() and
        np.isnan(tsl_pcts_init_array).any()
    )

    # if leverage is too big or too small
    if lev_mode == LeverageMode.Isolated:
        if not np.isfinite(leverage_array).any() or (
            leverage_array.any() > max_lev or
            leverage_array.any() < 0
        ):
            raise ValueError(
                "leverage needs to be between 1 and max lev")
    if lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise ValueError(
                "When using Least Free Cash Used set a proper sl or tsl > 0")
        if np.isfinite(leverage_array).any():
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

    if risk_rewards_array.any() > 0 and np.isfinite(tp_pcts_array).any():
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
    if not np.isnan(size_value_array).any() and not np.isnan(size_pct_array).any():
        raise ValueError(
            "You can't have size and size pct set at the same time.")

    # simple check if order size type is valid
    if 0 > order_type > len(OrderType) or not np.isfinite(order_type):
        raise ValueError("order_type is invalid")

    # Getting the right size for Size Type Amount
    if size_type == SizeType.Amount:
        if np.isnan(size_value_array).any() or size_value_array.any() < 1:
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
            "When using Risk Amount or Risk Percent of Account set a proper sl pct or tsl pct > 0")

    # setting risk percent size
    if size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account.")

    # stop loss break even checks
    if np.isfinite(sl_to_be_based_on_array).any() and (
        sl_to_be_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price or
        sl_to_be_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums")

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

    if sl_to_be == False:
        if np.isfinite(sl_to_be_based_on_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_based_on.")
        if sl_to_be_then_trail == True:
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_then_trail.")
        if np.isfinite(sl_to_be_trail_by_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_trail_by_when_pct_from_avg_entry.")
        if np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_when_pct_from_avg_entry.")
        if np.isfinite(sl_to_be_zero_or_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_zero_or_entry.")

    if sl_to_be and (
        not np.isfinite(sl_to_be_based_on_array).any() or
        not np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any() or
        not np.isfinite(sl_to_be_zero_or_entry_array).any() or
        not np.isfinite(sl_pcts_array).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts etc")

    if (sl_to_be and sl_to_be_then_trail) and (
        not np.isfinite(sl_to_be_based_on_array).any() or
        not np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any() or
        not np.isfinite(sl_to_be_zero_or_entry_array).any() or
        not np.isfinite(sl_to_be_trail_by_when_pct_from_avg_entry_array).any() or
        not np.isfinite(sl_pcts_array).any()

    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts etc")

    # tsl Checks
    if np.isfinite(tsl_based_on_array).any() and (
        tsl_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price or
        tsl_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need tsl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums")

    if np.isinf(tsl_trail_by_pct_array).any() or \
            tsl_trail_by_pct_array.any() < 0:
        raise ValueError(
            "You need tsl_trail_by_pct to be > 0 or not inf.")

    if np.isinf(tsl_when_pct_from_avg_entry_array).any() or \
            tsl_when_pct_from_avg_entry_array.any() < 0:
        raise ValueError(
            "You need tsl_when_pct_from_avg_entry to be > 0 or not inf.")

    if tsl_true_or_false == False:
        if np.isfinite(tsl_based_on_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_based_on.")
        if np.isfinite(tsl_trail_by_pct_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_trail_by_pct.")
        if np.isfinite(tsl_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_when_pct_from_avg_entry.")

    if tsl_true_or_false and (
        not np.isfinite(tsl_based_on_array).any() or
        not np.isfinite(tsl_trail_by_pct_array).any() or
        not np.isfinite(tsl_when_pct_from_avg_entry_array).any() or
        not np.isfinite(tsl_pcts_init_array).any()
    ):
        raise ValueError(
            "If you have tsl_true_or_false set to true then you must provide the other params like tsl_pcts_init etc")

    # Cart of new arrays
    arrays = (
        # np.array([0.]),
        leverage_array,
        max_equity_risk_pct_array,
        max_equity_risk_value_array,
        risk_rewards_array,
        size_pct_array,
        size_value_array,
        sl_pcts_array,
        sl_to_be_based_on_array,
        sl_to_be_trail_by_when_pct_from_avg_entry_array,
        sl_to_be_when_pct_from_avg_entry_array,
        sl_to_be_zero_or_entry_array,
        tp_pcts_array,
        tsl_based_on_array,
        tsl_pcts_init_array,
        tsl_trail_by_pct_array,
        tsl_when_pct_from_avg_entry_array,
    )
    # arrays = (
    #     np.array([0.]),
    #     np.array([1., 2., 3.]),
    #     np.array([np.nan]),
    #     np.array([4., 5.]),
    #     np.array([np.nan]),
    #     np.array([np.nan]),
    #     np.array([1.,6.,8.]),
    #     np.array([0.]),
    #     np.array([np.nan]),
    #     np.array([3.]),
    #     np.array([np.inf]),
    #     np.array([np.inf]),
    #     np.array([np.nan]),
    #     np.array([np.inf]),
    #     np.array([np.nan]),
    #     np.array([np.inf]),
    #     np.array([np.nan]),
    # )

    dtype_names = (
        # 'order_settings_id',
        'leverage',
        'max_equity_risk_pct',
        'max_equity_risk_value',
        'risk_rewards',
        'size_pct',
        'size_value',
        'sl_pcts',
        'sl_to_be_based_on',
        'sl_to_be_trail_by_when_pct_from_avg_entry',
        'sl_to_be_when_pct_from_avg_entry',
        'sl_to_be_zero_or_entry',
        'tp_pcts',
        'tsl_based_on',
        'tsl_pcts_init',
        'tsl_trail_by_pct',
        'tsl_when_pct_from_avg_entry',
    )

    n = 1
    for x in arrays:
        n *= x.size
    out = np.empty((n, len(arrays)))
    cart_array = np.empty(n, dtype=cart_array_dt)

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
    
    # literal unroll
    counter = 0
    for dtype_name in literal_unroll(dtype_names):
        for col in range(n):
            cart_array[dtype_name][col] = out[col][counter]
        counter += 1

    # Setting variable arrys from cart arrays
    leverage_cart_array = cart_array['leverage']
    max_equity_risk_pct_cart_array = cart_array['max_equity_risk_pct']
    max_equity_risk_value_cart_array = cart_array['max_equity_risk_value']
    risk_rewards_cart_array = cart_array['risk_rewards']
    size_pct_cart_array = cart_array['size_pct']
    size_value_cart_array = cart_array['size_value']
    sl_pcts_cart_array = cart_array['sl_pcts']
    sl_to_be_based_on_cart_array = cart_array['sl_to_be_based_on']
    sl_to_be_trail_by_when_pct_from_avg_entry_cart_array = cart_array[
        'sl_to_be_trail_by_when_pct_from_avg_entry']
    sl_to_be_when_pct_from_avg_entry_cart_array = cart_array[
        'sl_to_be_when_pct_from_avg_entry']
    sl_to_be_zero_or_entry_cart_array = cart_array['sl_to_be_zero_or_entry']
    tp_pcts_cart_array = cart_array['tp_pcts']
    tsl_based_on_cart_array = cart_array['tsl_based_on']
    tsl_pcts_init_cart_array = cart_array['tsl_pcts_init']
    tsl_trail_by_cart_array = cart_array['tsl_trail_by_pct']
    tsl_when_pct_from_avg_entry_cart_array = cart_array['tsl_when_pct_from_avg_entry']

    # Creating Settings Vars
    total_order_settings = sl_pcts_cart_array.shape[0]

    if entries.ndim == 1:
        total_indicator_settings = 1
    else:
        total_indicator_settings = entries.shape[1]

    total_bars = open_prices.shape[0]

    # record_count = 0
    # for i in range(total_order_settings):
    #     for ii in range(total_indicator_settings):
    #         for iii in range(total_bars):
    #             if entries[:, ii][iii]:
    #                 record_count += 1
    # record_count = int(record_count / 2)

    # Creating OR
    df_array = np.empty(100000, dtype=df_array_dt)
    df_cart_array = np.empty(100000, dtype=cart_array_dt)
    df_counter = 0

    order_records = np.empty(100000, dtype=or_dt)
    or_filled_start = 0
    or_filled_temp = np.array([0])
    order_count_id = np.array([0])

    use_stops = not np.isnan(sl_pcts_array[0]) or \
        not np.isnan(tsl_pcts_init_array[0]) or \
        not np.isnan(tp_pcts_array[0])

    # order settings loops
    for order_settings_counter in range(total_order_settings):

        entry_order = EntryOrder(
            leverage=leverage_cart_array[order_settings_counter],
            max_equity_risk_pct=max_equity_risk_pct_cart_array[order_settings_counter],
            max_equity_risk_value=max_equity_risk_value_cart_array[order_settings_counter],
            order_type=order_type,
            risk_rewards=risk_rewards_cart_array[order_settings_counter],
            size_pct=size_pct_cart_array[order_settings_counter],
            size_value=size_value_cart_array[order_settings_counter],
            sl_pcts=sl_pcts_cart_array[order_settings_counter],
            tp_pcts=tp_pcts_cart_array[order_settings_counter],
            tsl_pcts_init=tsl_pcts_init_cart_array[order_settings_counter],
        )
        stops_order = StopsOrder(
            sl_to_be=sl_to_be,
            sl_to_be_based_on=sl_to_be_based_on_cart_array[order_settings_counter],
            sl_to_be_then_trail=sl_to_be_then_trail,
            sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_cart_array[
                order_settings_counter],
            sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_cart_array[
                order_settings_counter],
            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_cart_array[order_settings_counter],
            tsl_based_on=tsl_based_on_cart_array[order_settings_counter],
            tsl_trail_by_pct=tsl_trail_by_cart_array[order_settings_counter],
            tsl_true_or_false=tsl_true_or_false,
            tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_cart_array[
                order_settings_counter],
        )

        # ind set loop
        for indicator_settings_counter in range(total_indicator_settings):

            if entries.ndim != 1:
                current_indicator_entries = entries[
                    :, indicator_settings_counter]
            else:
                current_indicator_entries = entries

            # Account State Reset
            account_state = AccountState(
                available_balance=og_equity,
                cash_borrowed=0.,
                cash_used=0.,
                equity=og_equity,
            )

            # Order Result Reset
            order_result = OrderResult(
                average_entry=0.,
                fees_paid=0.,
                leverage=0.,
                liq_price=np.nan,
                moved_sl_to_be=False,
                order_status=0,
                order_status_info=0,
                order_type=entry_order.order_type,
                pct_chg_trade=0.,
                position=0.,
                price=0.,
                realized_pnl=0.,
                size_value=0.,
                sl_pcts=0.,
                sl_prices=0.,
                tp_pcts=0.,
                tp_prices=0.,
                tsl_pcts_init=0.,
                tsl_prices=0.,
            )
            or_filled_temp[0] = 0

            # entries loop
            for bar in range(total_bars):

                if account_state.available_balance < 5:
                    break

                if current_indicator_entries[bar]:

                    # Process Order nb
                    account_state, order_result = process_order_nb(
                        price=open_prices[bar],
                        order_type=entry_order.order_type,

                        account_state=account_state,
                        entry_order=entry_order,
                        order_result=order_result,
                        static_variables=static_variables,

                        bar=bar,
                        indicator_settings_counter=indicator_settings_counter,
                        order_settings_counter=order_settings_counter,

                        order_records=order_records[order_count_id[0]],
                        order_count_id=order_count_id,
                        or_filled_temp=or_filled_temp,
                    )
                if order_result.position > 0:
                    # Check Stops
                    order_result = check_sl_tp_nb(
                        open_price=open_prices[bar],
                        high_price=high_prices[bar],
                        low_price=low_prices[bar],
                        close_price=close_prices[bar],

                        fee_pct=static_variables.fee_pct,

                        entry_type=entry_order.order_type,
                        order_result=order_result,
                        stops_order=stops_order,

                        account_state=account_state,
                        order_records=order_records[order_count_id[0]],
                        order_count_id=order_count_id,
                        or_filled_temp=or_filled_temp,

                        bar=bar,
                        indicator_settings_counter=indicator_settings_counter,
                        order_settings_counter=order_settings_counter,
                    )
                    # process stops
                    if not np.isnan(order_result.size_value):
                        account_state, order_result = process_order_nb(
                            entry_order=entry_order,
                            order_type=order_result.order_type,

                            price=open_prices[bar],

                            account_state=account_state,
                            order_result=order_result,
                            static_variables=static_variables,

                            bar=bar,
                            indicator_settings_counter=indicator_settings_counter,
                            order_settings_counter=order_settings_counter,

                            order_records=order_records[order_count_id[0]],
                            order_count_id=order_count_id,
                            or_filled_temp=or_filled_temp,
                        )

            # Checking if gains
            gains_pct = ((account_state.equity - og_equity) / og_equity) * 100
            if gains_pct > gains_pct_filter:
                temp_order_records = order_records[or_filled_start:order_count_id[0]]
                w_l = temp_order_records['real_pnl'][~np.isnan(
                    temp_order_records['real_pnl'])]
                # Checking total trade filter
                if w_l.size > total_trade_filter:

                    or_filled_start = order_count_id[0]

                    w_l_no_be = w_l[w_l != 0]  # filter out all BE trades

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

                    # df array
                    df_array['or_set'][df_counter] = temp_order_records['or_set'][0]
                    df_array['ind_set'][df_counter] = temp_order_records['ind_set'][0]
                    df_array['total_trades'][df_counter] = w_l.size
                    df_array['total_BE'][df_counter] = w_l[w_l == 0].size
                    df_array['gains_pct'][df_counter] = gains_pct
                    df_array['win_rate'][df_counter] = win_rate
                    df_array['to_the_upside'][df_counter] = to_the_upside
                    df_array['total_fees'][df_counter] = np.nancumsum(
                        temp_order_records['fees_paid'])[-1]
                    df_array['total_pnl'][df_counter] = total_pnl
                    df_array['ending_eq'][df_counter] = temp_order_records['equity'][-1]

                    # df cart array
                    df_cart_array['order_settings_id'][df_counter] = order_settings_counter * 1.
                    df_cart_array['leverage'][df_counter] = leverage_cart_array[order_settings_counter]
                    df_cart_array['max_equity_risk_pct'][df_counter] = max_equity_risk_pct_cart_array[order_settings_counter] * 100
                    df_cart_array['max_equity_risk_value'][df_counter] = max_equity_risk_value_cart_array[order_settings_counter]
                    df_cart_array['risk_rewards'][df_counter] = risk_rewards_cart_array[order_settings_counter]
                    df_cart_array['size_pct'][df_counter] = size_pct_cart_array[order_settings_counter] * 100
                    df_cart_array['size_value'][df_counter] = size_value_cart_array[order_settings_counter]
                    df_cart_array['sl_pcts'][df_counter] = sl_pcts_cart_array[order_settings_counter] * 100
                    df_cart_array['sl_to_be_based_on'][df_counter] = sl_to_be_based_on_cart_array[order_settings_counter]
                    df_cart_array['sl_to_be_trail_by_when_pct_from_avg_entry'][
                        df_counter] = sl_to_be_trail_by_when_pct_from_avg_entry_cart_array[order_settings_counter] * 100
                    df_cart_array['sl_to_be_when_pct_from_avg_entry'][
                        df_counter] = sl_to_be_when_pct_from_avg_entry_cart_array[order_settings_counter] * 100
                    df_cart_array['sl_to_be_zero_or_entry'][df_counter] = sl_to_be_zero_or_entry_cart_array[order_settings_counter]
                    df_cart_array['tp_pcts'][df_counter] = tp_pcts_cart_array[order_settings_counter] * 100
                    df_cart_array['tsl_based_on'][df_counter] = tsl_based_on_cart_array[order_settings_counter]
                    df_cart_array['tsl_pcts_init'][df_counter] = tsl_pcts_init_cart_array[order_settings_counter] * 100
                    df_cart_array['tsl_trail_by_pct'][df_counter] = tsl_trail_by_cart_array[order_settings_counter] * 100
                    df_cart_array['tsl_when_pct_from_avg_entry'][df_counter] = tsl_when_pct_from_avg_entry_cart_array[order_settings_counter] * 100

                    df_counter += 1
            # Gains False
            else:
                # order_records[or_filled_start:order_count_id[0]] = np.zeros(order_records[0].size, dtype=or_dt)[0]
                order_count_id[0] = order_count_id[0] - or_filled_temp[0]

    return df_array[: df_counter], order_records[: order_count_id[0]], df_cart_array[: df_counter]
