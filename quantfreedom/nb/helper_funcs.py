import numpy as np
from numba import njit

from quantfreedom._typing import (
    RecordArray,
    Array1d,
    Array2d,
    PossibleArray,
)

from quantfreedom.enums import (
    AccountState,
    Arrays1dTuple,
    EntryOrder,
    LeverageMode,
    OrderResult,
    OrderType,
    SizeType,
    CandleBody,
    StaticVariables,
    StopsOrder,
)


@njit(cache=True)
def static_var_checker_nb(
    divide_records_array_size_by: float,
    equity: float,
    fee_pct: float,
    gains_pct_filter: float,
    lev_mode: int,
    max_lev: float,
    max_order_size_pct: float,
    max_order_size_value: float,
    min_order_size_pct: float,
    min_order_size_value: float,
    mmr_pct: float,
    order_type: int,
    size_type: int,
    sl_to_be_then_trail: bool,
    sl_to_be: bool,
    total_trade_filter: int,
    tsl_true_or_false: bool,
    upside_filter: float,
) -> StaticVariables:
    if equity < 0 or not np.isfinite(equity):
        raise ValueError("YOU HAVE NO MONEY!!!! You Broke!!!!")

    if fee_pct < 0 or not np.isfinite(fee_pct):
        raise ValueError("fee_pct must be finite")

    if mmr_pct < 0 or not np.isfinite(mmr_pct):
        raise ValueError("mmr_pct must be finite")

    if not np.isfinite(max_lev) or 1 > max_lev > 100:
        raise ValueError("max lev has to be between 1 and 100")

    if not np.isfinite(min_order_size_pct) or 0.01 > min_order_size_pct > 100:
        raise ValueError("min_order_size_pct  has to be between .01 and 100")

    if (
        not np.isfinite(max_order_size_pct)
        or min_order_size_pct > max_order_size_pct > 100
    ):
        raise ValueError(
            "max_order_size_pct has to be between min_order_size_pct and 100"
        )

    if not np.isfinite(min_order_size_value) or min_order_size_value < 1:
        raise ValueError("min_order_size_value has to be between .01 and 1 min inf")

    if np.isnan(max_order_size_value) or max_order_size_value < min_order_size_value:
        raise ValueError("max_order_size_value has to be > min_order_size_value")

    if gains_pct_filter == np.inf:
        raise ValueError("gains_pct_filter can't be inf")

    if total_trade_filter < 0 or not np.isfinite(total_trade_filter):
        raise ValueError("total_trade_filter needs to be greater than 0")

    if sl_to_be == True and tsl_true_or_false == True:
        raise ValueError("You can't have sl_to_be and tsl_true_or_false both be true")

    if sl_to_be != True and sl_to_be != False:
        raise ValueError("sl_to_be needs to be true or false")

    if sl_to_be_then_trail != True and sl_to_be_then_trail != False:
        raise ValueError("sl_to_be_then_trail needs to be true or false")

    if tsl_true_or_false != True and tsl_true_or_false != False:
        raise ValueError("tsl_true_or_false needs to be true or false")

    # simple check if order size type is valid
    if 0 > order_type > len(OrderType) or not np.isfinite(order_type):
        raise ValueError("order_type is invalid")

    if not (-1 <= upside_filter <= 1):
        raise ValueError("upside filter must be between -1 and 1")

    if not (1 <= divide_records_array_size_by <= 1000):
        raise ValueError(
            "divide_records_array_size_by filter must be between 1 and 1000"
        )

    # Static variables creation
    fee_pct /= 100
    mmr_pct /= 100
    max_order_size_pct /= 100
    min_order_size_pct /= 100

    return StaticVariables(
        divide_records_array_size_by=divide_records_array_size_by,
        fee_pct=fee_pct,
        lev_mode=lev_mode,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_pct=min_order_size_pct,
        min_order_size_value=min_order_size_value,
        mmr_pct=mmr_pct,
        order_type=order_type,
        size_type=size_type,
        sl_to_be_then_trail=sl_to_be_then_trail,
        sl_to_be=sl_to_be,
        tsl_true_or_false=tsl_true_or_false,
        upside_filter=upside_filter,
    )


@njit(cache=True)
def create_1d_arrays_nb(
    leverage,
    max_equity_risk_pct,
    max_equity_risk_value,
    risk_rewards,
    size_pct,
    size_value,
    sl_based_on_add_pct,
    sl_based_on,
    sl_pcts,
    sl_to_be_based_on,
    sl_to_be_trail_by_when_pct_from_avg_entry,
    sl_to_be_when_pct_from_avg_entry,
    sl_to_be_zero_or_entry,
    tp_pcts,
    tsl_based_on,
    tsl_pcts_init,
    tsl_trail_by_pct,
    tsl_when_pct_from_avg_entry,
) -> Arrays1dTuple:
    leverage_array = to_1d_array_nb(np.asarray(leverage, dtype=np.float_))

    max_equity_risk_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(max_equity_risk_pct) / 100, dtype=np.float_)
    )

    max_equity_risk_value_array = to_1d_array_nb(
        np.asarray(max_equity_risk_value, dtype=np.float_)
    )

    size_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(size_pct) / 100, dtype=np.float_)
    )

    size_value_array = to_1d_array_nb(np.asarray(size_value, dtype=np.float_))

    # Stop Loss Arrays
    sl_pcts_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_pcts) / 100, dtype=np.float_)
    )

    sl_to_be_based_on_array = to_1d_array_nb(
        np.asarray(sl_to_be_based_on, dtype=np.float_)
    )

    sl_based_on_add_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_based_on_add_pct) / 100, dtype=np.float_)
    )

    sl_based_on_array = to_1d_array_nb(np.asarray(sl_based_on, dtype=np.float_))

    sl_to_be_trail_by_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(
            np.asarray(sl_to_be_trail_by_when_pct_from_avg_entry) / 100, dtype=np.float_
        )
    )

    sl_to_be_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_to_be_when_pct_from_avg_entry) / 100, dtype=np.float_)
    )

    sl_to_be_zero_or_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_zero_or_entry, dtype=np.float_)
    )

    # Trailing Stop Loss Arrays
    tsl_pcts_init_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_pcts_init) / 100, dtype=np.float_)
    )

    tsl_based_on_array = to_1d_array_nb(np.asarray(tsl_based_on, dtype=np.float_))

    tsl_trail_by_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_trail_by_pct) / 100, dtype=np.float_)
    )

    tsl_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_when_pct_from_avg_entry) / 100, dtype=np.float_)
    )

    # Take Profit Arrays
    risk_rewards_array = to_1d_array_nb(np.asarray(risk_rewards, dtype=np.float_))

    tp_pcts_array = to_1d_array_nb(
        np.asarray(np.asarray(tp_pcts) / 100, dtype=np.float_)
    )

    return Arrays1dTuple(
        leverage=leverage_array,
        max_equity_risk_pct=max_equity_risk_pct_array,
        max_equity_risk_value=max_equity_risk_value_array,
        risk_rewards=risk_rewards_array,
        size_pct=size_pct_array,
        size_value=size_value_array,
        sl_based_on_add_pct=sl_based_on_add_pct_array,
        sl_based_on=sl_based_on_array,
        sl_pcts=sl_pcts_array,
        sl_to_be_based_on=sl_to_be_based_on_array,
        sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_array,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_array,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_array,
        tp_pcts=tp_pcts_array,
        tsl_based_on=tsl_based_on_array,
        tsl_pcts_init=tsl_pcts_init_array,
        tsl_trail_by_pct=tsl_trail_by_pct_array,
        tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_array,
    )


@njit(cache=True)
def check_1d_arrays_nb(
    arrays_1d_tuple: Arrays1dTuple,
    static_variables_tuple: StaticVariables,
):
    if np.isfinite(arrays_1d_tuple.size_value).all():
        if arrays_1d_tuple.size_value.any() < 1:
            raise ValueError("size_value must be greater than 1.")
        if (
            arrays_1d_tuple.size_value.any()
            > static_variables_tuple.max_order_size_value
        ):
            raise ValueError("size_value is greater than max_order_size_value")

        if (
            arrays_1d_tuple.size_value.any()
            < static_variables_tuple.min_order_size_value
        ):
            raise ValueError("size_value is greater than max_order_size_value")

    if not np.isfinite(arrays_1d_tuple.size_pct).all():
        if arrays_1d_tuple.size_pct.any() < 1:
            raise ValueError("size_pct must be greater than 1.")

        if arrays_1d_tuple.size_pct.any() > static_variables_tuple.max_order_size_pct:
            raise ValueError("size_pct is greater than max_order_size_pct")

        if arrays_1d_tuple.size_pct.any() < static_variables_tuple.min_order_size_pct:
            raise ValueError("size_pct is greater than max_order_size_pct")

    if np.isinf(arrays_1d_tuple.sl_pcts).any() or arrays_1d_tuple.sl_pcts.any() < 0:
        raise ValueError("sl_pcts has to be nan or greater than 0 and not inf")

    # sl based on checks
    if (
        np.isinf(arrays_1d_tuple.sl_based_on_add_pct).any()
        or arrays_1d_tuple.sl_based_on_add_pct.any() < 0
    ):
        raise ValueError(
            "sl_based_on_add_pct has to be nan or greater than 0 and not inf"
        )

    if (
        not np.isfinite(arrays_1d_tuple.sl_based_on_add_pct).any()
        and np.isfinite(arrays_1d_tuple.sl_based_on).any()
    ):
        raise ValueError(
            "sl_based_on_add_pct has to be set in order to use sl based on ... please set it to be > 0 and not np.inf"
        )

    if (
        np.isinf(arrays_1d_tuple.tsl_pcts_init).any()
        or arrays_1d_tuple.tsl_pcts_init.any() < 0
    ):
        raise ValueError("tsl_pcts_init has to be nan or greater than 0 and not inf")

    if np.isinf(arrays_1d_tuple.tp_pcts).any() or arrays_1d_tuple.tp_pcts.any() < 0:
        raise ValueError("tp_pcts has to be nan or greater than 0 and not inf")

    if (0 > static_variables_tuple.lev_mode > len(LeverageMode)) or not np.isfinite(
        static_variables_tuple.lev_mode
    ):
        raise ValueError("leverage mode is out of range or not finite")

    check_sl_tsl_for_nan = (
        np.isnan(arrays_1d_tuple.sl_pcts).any()
        and np.isnan(arrays_1d_tuple.tsl_pcts_init).any()
        and np.isnan(arrays_1d_tuple.sl_based_on).any()
    )

    # if leverage is too big or too small
    if static_variables_tuple.lev_mode == LeverageMode.Isolated:
        if not np.isfinite(arrays_1d_tuple.leverage).any() or (
            arrays_1d_tuple.leverage.any() > static_variables_tuple.max_lev
            or arrays_1d_tuple.leverage.any() < 0
        ):
            raise ValueError("leverage needs to be between 1 and max lev")
    if static_variables_tuple.lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise ValueError(
                "When using Least Free Cash Used set a proper sl or tsl > 0"
            )
        if np.isfinite(arrays_1d_tuple.leverage).any():
            raise ValueError(
                "When using Least Free Cash Used leverage iso must be np.nan"
            )

    # making sure we have a number greater than 0 for rr
    if (
        np.isinf(arrays_1d_tuple.risk_rewards).any()
        or arrays_1d_tuple.risk_rewards.any() < 0
    ):
        raise ValueError("Risk Rewards has to be greater than 0 or np.nan")

    # check if RR has sl pct / price or tsl pct / price
    if not np.isnan(arrays_1d_tuple.risk_rewards).any() and check_sl_tsl_for_nan:
        raise ValueError("When risk to reward is set you have to have a sl or tsl > 0")

    if (
        arrays_1d_tuple.risk_rewards.any() > 0
        and np.isfinite(arrays_1d_tuple.tp_pcts).any()
    ):
        raise ValueError("You can't have take profits set when using Risk to reward")

    if (
        np.isinf(arrays_1d_tuple.max_equity_risk_pct).any()
        or arrays_1d_tuple.max_equity_risk_pct.any() < 0
    ):
        raise ValueError("Max equity risk percent has to be greater than 0 or np.nan")

    elif (
        np.isinf(arrays_1d_tuple.max_equity_risk_value).any()
        or arrays_1d_tuple.max_equity_risk_value.any() < 0
    ):
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    if (
        not np.isnan(arrays_1d_tuple.max_equity_risk_pct).any()
        and not np.isnan(arrays_1d_tuple.max_equity_risk_value).any()
    ):
        raise ValueError(
            "You can't have max risk pct and max risk value both set at the same time."
        )
    if (
        not np.isnan(arrays_1d_tuple.size_value).any()
        and not np.isnan(arrays_1d_tuple.size_pct).any()
    ):
        raise ValueError("You can't have size and size pct set at the same time.")

    # simple check if order size type is valid
    if 0 > static_variables_tuple.order_type > len(OrderType) or not np.isfinite(
        static_variables_tuple.order_type
    ):
        raise ValueError("order_type is invalid")

    # Getting the right size for Size Type Amount
    if static_variables_tuple.size_type == SizeType.Amount:
        if (
            np.isnan(arrays_1d_tuple.size_value).any()
            or arrays_1d_tuple.size_value.any() < 1
        ):
            raise ValueError(
                "With SizeType as amount, size_value must be 1 or greater."
            )

    if static_variables_tuple.size_type == SizeType.PercentOfAccount:
        if np.isnan(arrays_1d_tuple.size_pct).any():
            raise ValueError("You need size_pct to be > 0 if using percent of account.")

    # checking to see if you set a stop loss for risk based size types
    if (
        static_variables_tuple.size_type == SizeType.RiskAmount
        or (static_variables_tuple.size_type == SizeType.RiskPercentOfAccount)
        and check_sl_tsl_for_nan
    ):
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl pct or tsl pct > 0"
        )

    # setting risk percent size
    if static_variables_tuple.size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(arrays_1d_tuple.size_pct).any():
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account."
            )

    # stop loss break even checks
    if np.isfinite(arrays_1d_tuple.sl_to_be_based_on).any() and (
        arrays_1d_tuple.sl_to_be_based_on.any() < CandleBody.open
        or arrays_1d_tuple.sl_to_be_based_on.any() > CandleBody.close
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either open, high , low, or close. look up CandleBody enums"
        )

    # stop loss based on checks
    if np.isfinite(arrays_1d_tuple.sl_based_on).any() and (
        arrays_1d_tuple.sl_based_on.any() < CandleBody.open
        or arrays_1d_tuple.sl_based_on.any() > CandleBody.close
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either open, high , low, or close. look up CandleBody enums"
        )

    if (
        np.isfinite(arrays_1d_tuple.sl_pcts).any()
        and np.isfinite(arrays_1d_tuple.sl_based_on).any()
    ):
        raise ValueError(
            "You can't have both stop loss pct and stop loss based on set at the same time"
        )

    if (
        np.isinf(arrays_1d_tuple.sl_to_be_trail_by_when_pct_from_avg_entry).any()
        or arrays_1d_tuple.sl_to_be_trail_by_when_pct_from_avg_entry.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_trail_by_when_pct_from_avg_entry to be > 0 or not inf."
        )

    if (
        np.isinf(arrays_1d_tuple.sl_to_be_when_pct_from_avg_entry).any()
        or arrays_1d_tuple.sl_to_be_when_pct_from_avg_entry.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_when_pct_from_avg_entry to be > 0 or not inf."
        )

    if (
        arrays_1d_tuple.sl_to_be_zero_or_entry.any() < 0
        or arrays_1d_tuple.sl_to_be_zero_or_entry.any() > 1
    ):
        raise ValueError("sl_to_be_zero_or_entry needs to be 0 for zero or 1 for entry")

    if static_variables_tuple.sl_to_be == False:
        if np.isfinite(arrays_1d_tuple.sl_to_be_based_on).any():
            raise ValueError("sl_to_be needs to be True to use sl_to_be_based_on.")
        if static_variables_tuple.sl_to_be_then_trail == True:
            raise ValueError("sl_to_be needs to be True to use sl_to_be_then_trail.")
        if np.isfinite(arrays_1d_tuple.sl_to_be_trail_by_when_pct_from_avg_entry).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_trail_by_when_pct_from_avg_entry."
            )
        if np.isfinite(arrays_1d_tuple.sl_to_be_when_pct_from_avg_entry).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_when_pct_from_avg_entry."
            )
        if np.isfinite(arrays_1d_tuple.sl_to_be_zero_or_entry).any():
            raise ValueError("sl_to_be needs to be True to use sl_to_be_zero_or_entry.")

    if static_variables_tuple.sl_to_be and (
        not np.isfinite(arrays_1d_tuple.sl_to_be_based_on).any()
        or not np.isfinite(arrays_1d_tuple.sl_to_be_when_pct_from_avg_entry).any()
        or not np.isfinite(arrays_1d_tuple.sl_to_be_zero_or_entry).any()
        or not np.isfinite(arrays_1d_tuple.sl_based_on).any()
        or not np.isfinite(arrays_1d_tuple.sl_pcts).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts or sl_based_on etc"
        )

    if (
        static_variables_tuple.sl_to_be and static_variables_tuple.sl_to_be_then_trail
    ) and (
        not np.isfinite(arrays_1d_tuple.sl_to_be_based_on).any()
        or not np.isfinite(arrays_1d_tuple.sl_to_be_based_on).any()
        or not np.isfinite(arrays_1d_tuple.sl_to_be_when_pct_from_avg_entry).any()
        or not np.isfinite(arrays_1d_tuple.sl_to_be_zero_or_entry).any()
        or not np.isfinite(
            arrays_1d_tuple.sl_to_be_trail_by_when_pct_from_avg_entry
        ).any()
        or not np.isfinite(arrays_1d_tuple.sl_pcts).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts or sl_based_on etc"
        )

    # tsl Checks
    if np.isfinite(arrays_1d_tuple.tsl_based_on).any() and (
        arrays_1d_tuple.tsl_based_on.any() < CandleBody.open
        or arrays_1d_tuple.tsl_based_on.any() > CandleBody.close
    ):
        raise ValueError(
            "You need tsl_to_be_based_on to be be either 0 1 2 or 3. look up CandleBody enums"
        )

    if (
        np.isinf(arrays_1d_tuple.tsl_trail_by_pct).any()
        or arrays_1d_tuple.tsl_trail_by_pct.any() < 0
    ):
        raise ValueError("You need tsl_trail_by_pct to be > 0 or not inf.")

    if (
        np.isinf(arrays_1d_tuple.tsl_when_pct_from_avg_entry).any()
        or arrays_1d_tuple.tsl_when_pct_from_avg_entry.any() < 0
    ):
        raise ValueError("You need tsl_when_pct_from_avg_entry to be > 0 or not inf.")

    if static_variables_tuple.tsl_true_or_false == False:
        if np.isfinite(arrays_1d_tuple.tsl_based_on).any():
            raise ValueError("tsl_true_or_false needs to be True to use tsl_based_on.")
        if np.isfinite(arrays_1d_tuple.tsl_trail_by_pct).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_trail_by_pct."
            )
        if np.isfinite(arrays_1d_tuple.tsl_when_pct_from_avg_entry).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_when_pct_from_avg_entry."
            )

    if static_variables_tuple.tsl_true_or_false and (
        not np.isfinite(arrays_1d_tuple.tsl_based_on).any()
        or not np.isfinite(arrays_1d_tuple.tsl_trail_by_pct).any()
        or not np.isfinite(arrays_1d_tuple.tsl_when_pct_from_avg_entry).any()
        or not np.isfinite(arrays_1d_tuple.tsl_pcts_init).any()
    ):
        raise ValueError(
            "If you have tsl_true_or_false set to true then you must provide the other params like tsl_pcts_init etc"
        )


@njit(cache=True)
def create_cart_product_nb(
    arrays_1d_tuple: Arrays1dTuple,
):
    # dtype_names = (
    #     'order_settings_id',
    #     'leverage',
    #     'max_equity_risk_pct',
    #     'max_equity_risk_value',
    #     'risk_rewards',
    #     'size_pct',
    #     'size_value',
    #     'sl_pcts',
    #     'sl_to_be_based_on',
    #     'sl_to_be_trail_by_when_pct_from_avg_entry',
    #     'sl_to_be_when_pct_from_avg_entry',
    #     'sl_to_be_zero_or_entry',
    #     'tp_pcts',
    #     'tsl_based_on',
    #     'tsl_pcts_init',
    #     'tsl_trail_by_pct',
    #     'tsl_when_pct_from_avg_entry',
    # )

    # cart array loop
    n = 1
    for x in arrays_1d_tuple:
        n *= x.size
    out = np.empty((n, len(arrays_1d_tuple)))

    for i in range(len(arrays_1d_tuple)):
        m = int(n / arrays_1d_tuple[i].size)
        out[:n, i] = np.repeat(arrays_1d_tuple[i], m)
        n //= arrays_1d_tuple[i].size

    n = arrays_1d_tuple[-1].size
    for k in range(len(arrays_1d_tuple) - 2, -1, -1):
        n *= arrays_1d_tuple[k].size
        m = int(n / arrays_1d_tuple[k].size)
        for j in range(1, arrays_1d_tuple[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    # # literal unroll
    # counter = 0
    # for dtype_name in literal_unroll(dtype_names):
    #     for col in range(n):
    #         cart_array[dtype_name][col] = out[col][counter]
    #     counter += 1

    # Setting variable arrys from cart arrays
    leverage_cart_array = out.T[0]
    max_equity_risk_pct_cart_array = out.T[1]
    max_equity_risk_value_cart_array = out.T[2]
    risk_rewards_cart_array = out.T[3]
    size_pct_cart_array = out.T[4]
    size_value_cart_array = out.T[5]
    sl_based_on_add_pct_cart_array = out.T[6]
    sl_based_on_cart_array = out.T[7]
    sl_pcts_cart_array = out.T[8]
    sl_to_be_based_on_cart_array = out.T[9]
    sl_to_be_trail_by_when_pct_from_avg_entry_cart_array = out.T[10]
    sl_to_be_when_pct_from_avg_entry_cart_array = out.T[11]
    sl_to_be_zero_or_entry_cart_array = out.T[12]
    tp_pcts_cart_array = out.T[13]
    tsl_based_on_cart_array = out.T[14]
    tsl_pcts_init_cart_array = out.T[15]
    tsl_trail_by_pct_cart_array = out.T[16]
    tsl_when_pct_from_avg_entry_cart_array = out.T[17]

    # leverage_cart_array = cart_array['leverage']
    # max_equity_risk_pct_cart_array = cart_array['max_equity_risk_pct']
    # max_equity_risk_value_cart_array = cart_array['max_equity_risk_value']
    # risk_rewards_cart_array = cart_array['risk_rewards']
    # size_pct_cart_array = cart_array['size_pct']
    # size_value_cart_array = cart_array['size_value']
    # sl_pcts_cart_array = cart_array['sl_pcts']
    # sl_to_be_based_on_cart_array = cart_array['sl_to_be_based_on']
    # sl_to_be_trail_by_when_pct_from_avg_entry_cart_array = cart_array[
    #     'sl_to_be_trail_by_when_pct_from_avg_entry']
    # sl_to_be_when_pct_from_avg_entry_cart_array = cart_array[
    #     'sl_to_be_when_pct_from_avg_entry']
    # sl_to_be_zero_or_entry_cart_array = cart_array['sl_to_be_zero_or_entry']
    # tp_pcts_cart_array = cart_array['tp_pcts']
    # tsl_based_on_cart_array = cart_array['tsl_based_on']
    # tsl_pcts_init_cart_array = cart_array['tsl_pcts_init']

    return Arrays1dTuple(
        leverage=leverage_cart_array,
        max_equity_risk_pct=max_equity_risk_pct_cart_array,
        max_equity_risk_value=max_equity_risk_value_cart_array,
        risk_rewards=risk_rewards_cart_array,
        size_pct=size_pct_cart_array,
        size_value=size_value_cart_array,
        sl_based_on_add_pct=sl_based_on_add_pct_cart_array,
        sl_based_on=sl_based_on_cart_array,
        sl_pcts=sl_pcts_cart_array,
        sl_to_be_based_on=sl_to_be_based_on_cart_array,
        sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_cart_array,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_cart_array,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_cart_array,
        tp_pcts=tp_pcts_cart_array,
        tsl_based_on=tsl_based_on_cart_array,
        tsl_pcts_init=tsl_pcts_init_cart_array,
        tsl_trail_by_pct=tsl_trail_by_pct_cart_array,
        tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_cart_array,
    )


@njit(cache=True)
def boradcast_to_1d_arrays(
    arrays_1d_tuple: Arrays1dTuple,
    entries: Array2d,
):
    x = 0
    biggest = 1
    while x < 7:
        if arrays_1d_tuple[x].size > 1:
            biggest = arrays_1d_tuple[x].size
            x += 1
            break
        x += 1

    while x < 7:
        if arrays_1d_tuple[x].size > 1 and arrays_1d_tuple[x].size != biggest:
            raise ValueError("Size mismatch")
        x += 1
    if biggest > 6:
        raise ValueError("Total amount of tests must be <= 6")

    leverage_braodcast_array = np.broadcast_to(arrays_1d_tuple[0], biggest)
    max_equity_risk_pct_braodcast_array = np.broadcast_to(arrays_1d_tuple[1], biggest)
    max_equity_risk_value_braodcast_array = np.broadcast_to(arrays_1d_tuple[2], biggest)
    risk_rewards_braodcast_array = np.broadcast_to(arrays_1d_tuple[3], biggest)
    size_pct_braodcast_array = np.broadcast_to(arrays_1d_tuple[4], biggest)
    size_value_braodcast_array = np.broadcast_to(arrays_1d_tuple[5], biggest)
    sl_based_on_add_pct_braodcast_array = np.broadcast_to(arrays_1d_tuple[6], biggest)
    sl_based_on_braodcast_array = np.broadcast_to(arrays_1d_tuple[7], biggest)
    sl_pcts_braodcast_array = np.broadcast_to(arrays_1d_tuple[8], biggest)
    sl_to_be_based_on_braodcast_array = np.broadcast_to(arrays_1d_tuple[9], biggest)
    sl_to_be_trail_by_when_pct_from_avg_entry_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[10], biggest
    )
    sl_to_be_when_pct_from_avg_entry_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[11], biggest
    )
    sl_to_be_zero_or_entry_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[12], biggest
    )
    tp_pcts_braodcast_array = np.broadcast_to(arrays_1d_tuple[13], biggest)
    tsl_based_on_braodcast_array = np.broadcast_to(arrays_1d_tuple[14], biggest)
    tsl_pcts_init_braodcast_array = np.broadcast_to(arrays_1d_tuple[15], biggest)
    tsl_trail_by_pct_braodcast_array = np.broadcast_to(arrays_1d_tuple[16], biggest)
    tsl_when_pct_from_avg_entry_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[17], biggest
    )

    if entries.shape[1] == 1:
        entries = np.broadcast_to(entries, (entries.shape[0], biggest))
    elif entries.shape[1] != biggest:
        raise ValueError("Something is wrong with entries")

    return entries, Arrays1dTuple(
        leverage=leverage_braodcast_array,
        max_equity_risk_pct=max_equity_risk_pct_braodcast_array,
        max_equity_risk_value=max_equity_risk_value_braodcast_array,
        risk_rewards=risk_rewards_braodcast_array,
        size_pct=size_pct_braodcast_array,
        size_value=size_value_braodcast_array,
        sl_based_on_add_pct=sl_based_on_add_pct_braodcast_array,
        sl_based_on=sl_based_on_braodcast_array,
        sl_pcts=sl_pcts_braodcast_array,
        sl_to_be_based_on=sl_to_be_based_on_braodcast_array,
        sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_braodcast_array,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_braodcast_array,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_braodcast_array,
        tp_pcts=tp_pcts_braodcast_array,
        tsl_based_on=tsl_based_on_braodcast_array,
        tsl_pcts_init=tsl_pcts_init_braodcast_array,
        tsl_trail_by_pct=tsl_trail_by_pct_braodcast_array,
        tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_braodcast_array,
    )


@njit(cache=True)
def fill_order_records_nb(
    bar: int,  # time stamp
    order_records: RecordArray,
    order_settings_counter: int,
    order_records_id: Array1d,
    account_state: AccountState,
    order_result: OrderResult,
) -> RecordArray:
    order_records["avg_entry"] = order_result.average_entry
    order_records["bar"] = bar
    order_records["equity"] = account_state.equity
    order_records["fees_paid"] = order_result.fees_paid
    order_records["order_set_id"] = order_settings_counter
    order_records["order_id"] = order_records_id[0]
    order_records["order_type"] = order_result.order_type
    order_records["price"] = order_result.price
    order_records["real_pnl"] = round(order_result.realized_pnl, 4)
    order_records["size_value"] = order_result.size_value
    order_records["sl_prices"] = order_result.sl_prices
    order_records["tp_prices"] = order_result.tp_prices
    order_records["tsl_prices"] = order_result.tsl_prices

    order_records_id[0] += 1


@njit(cache=True)
def fill_strat_records_nb(
    entries_col: int,
    equity: float,
    order_settings_counter: int,
    pnl: float,
    strat_records_filled: Array1d,
    strat_records: RecordArray,
    symbol_counter: int,
) -> RecordArray:
    strat_records["equity"] = equity
    strat_records["entries_col"] = entries_col
    strat_records["or_set"] = order_settings_counter
    strat_records["symbol"] = symbol_counter
    strat_records["real_pnl"] = round(pnl, 4)

    strat_records_filled[0] += 1


@njit(cache=True)
def get_to_the_upside_nb(
    gains_pct: float,
    wins_and_losses_array_no_be: Array1d,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

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

    if gains_pct <= 0:
        to_the_upside = -to_the_upside
    return to_the_upside


@njit(cache=True)
def fill_strategy_result_records_nb(
    gains_pct: float,
    strategy_result_records: RecordArray,
    temp_strat_records: Array1d,
    to_the_upside: float,
    total_trades: int,
    wins_and_losses_array_no_be: Array1d,
) -> RecordArray:
    # win rate calc
    win_loss = np.where(wins_and_losses_array_no_be < 0, 0, 1)
    win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)

    total_pnl = temp_strat_records["real_pnl"][
        ~np.isnan(temp_strat_records["real_pnl"])
    ].sum()

    # strat array
    strategy_result_records["symbol"] = temp_strat_records["symbol"][0]
    strategy_result_records["entries_col"] = temp_strat_records["entries_col"][0]
    strategy_result_records["or_set"] = temp_strat_records["or_set"][0]
    strategy_result_records["total_trades"] = total_trades
    strategy_result_records["gains_pct"] = gains_pct
    strategy_result_records["win_rate"] = win_rate
    strategy_result_records["to_the_upside"] = to_the_upside
    strategy_result_records["total_pnl"] = total_pnl
    strategy_result_records["ending_eq"] = temp_strat_records["equity"][-1]


@njit(cache=True)
def fill_settings_result_records_nb(
    entries_col: int,
    entry_order: EntryOrder,
    settings_result_records: RecordArray,
    stops_order: StopsOrder,
    symbol_counter: int,
) -> RecordArray:
    settings_result_records["symbol"] = symbol_counter
    settings_result_records["entries_col"] = entries_col
    settings_result_records["leverage"] = entry_order.leverage
    settings_result_records["max_equity_risk_pct"] = (
        entry_order.max_equity_risk_pct * 100
    )
    settings_result_records["max_equity_risk_value"] = entry_order.max_equity_risk_value
    settings_result_records["risk_rewards"] = entry_order.risk_rewards
    settings_result_records["size_pct"] = entry_order.size_pct * 100
    settings_result_records["size_value"] = entry_order.size_value
    settings_result_records["sl_pcts"] = entry_order.sl_pcts * 100
    settings_result_records["sl_to_be_based_on"] = stops_order.sl_to_be_based_on
    settings_result_records["sl_to_be_trail_by_when_pct_from_avg_entry"] = (
        stops_order.sl_to_be_trail_by_when_pct_from_avg_entry * 100
    )
    settings_result_records["sl_to_be_when_pct_from_avg_entry"] = (
        stops_order.sl_to_be_when_pct_from_avg_entry * 100
    )
    settings_result_records[
        "sl_to_be_zero_or_entry"
    ] = stops_order.sl_to_be_zero_or_entry
    settings_result_records["tp_pcts"] = entry_order.tp_pcts * 100
    settings_result_records["tsl_based_on"] = stops_order.tsl_based_on
    settings_result_records["tsl_pcts_init"] = entry_order.tsl_pcts_init * 100
    settings_result_records["tsl_trail_by_pct"] = stops_order.tsl_trail_by_pct * 100
    settings_result_records["tsl_when_pct_from_avg_entry"] = (
        stops_order.tsl_when_pct_from_avg_entry * 100
    )


@njit(cache=True)
def to_1d_array_nb(var: PossibleArray) -> Array1d:
    """Resize array to one dimension."""
    if var.ndim == 0:
        return np.expand_dims(var, axis=0)
    if var.ndim == 1:
        return var
    if var.ndim == 2 and var.shape[1] == 1:
        return var[:, 0]
    raise ValueError("to 1d array problem")


@njit(cache=True)
def to_2d_array_nb(var: PossibleArray, expand_axis: int = 1) -> Array2d:
    if var.ndim == 0:
        return np.expand_dims(np.expand_dims(var, axis=0), axis=0)
    if var.ndim == 1:
        return np.expand_dims(var, axis=expand_axis)
    if var.ndim == 2:
        return var
    raise ValueError("to 2d array problem")
