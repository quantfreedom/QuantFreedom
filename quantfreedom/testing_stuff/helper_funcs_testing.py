import numpy as np
from numba import njit

from quantfreedom.testing_stuff.base_testing import *
from quantfreedom.testing_stuff.buy_testing import *
from quantfreedom.testing_stuff.enums_testing import *
from quantfreedom.testing_stuff.execute_funcs_testing import *
from quantfreedom.testing_stuff.helper_funcs_testing import *
from quantfreedom.testing_stuff.simulate_testing import *


@njit(cache=True)
def static_var_checker_nb_testing(
    static_variables_tuple: StaticVariables,
) -> StaticVariables:
    if static_variables_tuple.equity < 0 or not np.isfinite(
        static_variables_tuple.equity
    ):
        raise ValueError("YOU HAVE NO MONEY!!!! You Broke!!!!")

    if static_variables_tuple.fee_pct < 0 or not np.isfinite(
        static_variables_tuple.fee_pct
    ):
        raise ValueError("fee_pct must be finite")

    if static_variables_tuple.mmr_pct < 0 or not np.isfinite(
        static_variables_tuple.mmr_pct
    ):
        raise ValueError("mmr_pct must be finite")

    if (
        not np.isfinite(static_variables_tuple.max_lev)
        or 1 > static_variables_tuple.max_lev > 100
    ):
        raise ValueError("max lev has to be between 1 and 100")

    if (
        not np.isfinite(static_variables_tuple.min_order_size_pct)
        or 0.01 > static_variables_tuple.min_order_size_pct > 100
    ):
        raise ValueError("min_order_size_pct  has to be between .01 and 100")

    if (
        not np.isfinite(static_variables_tuple.max_order_size_pct)
        or static_variables_tuple.min_order_size_pct
        > static_variables_tuple.max_order_size_pct
        > 100
    ):
        raise ValueError(
            "max_order_size_pct has to be between min_order_size_pct and 100"
        )

    if (
        not np.isfinite(static_variables_tuple.min_order_size_value)
        or static_variables_tuple.min_order_size_value < 1
    ):
        raise ValueError(
            "min_order_size_value has to be between .01 and 1 min inf")

    if (
        np.isnan(static_variables_tuple.max_order_size_value)
        or static_variables_tuple.max_order_size_value
        < static_variables_tuple.min_order_size_value
    ):
        raise ValueError(
            "max_order_size_value has to be > min_order_size_value")

    if static_variables_tuple.gains_pct_filter == np.inf:
        raise ValueError("gains_pct_filter can't be inf")

    if static_variables_tuple.total_trade_filter < 0 or not np.isfinite(
        static_variables_tuple.total_trade_filter
    ):
        raise ValueError("total_trade_filter needs to be greater than 0")

    # simple check if order size type is valid
    if 0 > static_variables_tuple.order_type > len(OrderType) or not np.isfinite(
        static_variables_tuple.order_type
    ):
        raise ValueError("order_type is invalid")

    if not (-1 <= static_variables_tuple.upside_filter <= 1):
        raise ValueError("upside filter must be between -1 and 1")

    if not (1 <= static_variables_tuple.divide_records_array_size_by <= 1000):
        raise ValueError(
            "divide_records_array_size_by filter must be between 1 and 1000"
        )
    return StaticVariables(
        equity=static_variables_tuple.equity,
        lev_mode=static_variables_tuple.lev_mode,
        order_type=static_variables_tuple.order_type,
        size_type=static_variables_tuple.size_type,
        divide_records_array_size_by=static_variables_tuple.divide_records_array_size_by,
        fee_pct=static_variables_tuple.fee_pct / 100,
        gains_pct_filter=static_variables_tuple.gains_pct_filter,
        max_lev=static_variables_tuple.max_lev,
        max_order_size_pct=static_variables_tuple.max_order_size_pct / 100,
        max_order_size_value=static_variables_tuple.max_order_size_value,
        min_order_size_pct=static_variables_tuple.min_order_size_pct / 100,
        min_order_size_value=static_variables_tuple.min_order_size_value,
        mmr_pct=static_variables_tuple.mmr_pct / 100,
        total_trade_filter=static_variables_tuple.total_trade_filter,
        upside_filter=static_variables_tuple.upside_filter,
    )


@njit(cache=True)
def all_os_as_1d_arrays_nb_testing(
    order_settings_arrays_tuple: OrderSettingsArrays,
) -> OrderSettingsArrays:
    leverage_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.leverage, dtype=np.float_)
    )

    max_equity_risk_pct_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(order_settings_arrays_tuple.max_equity_risk_pct) / 100,
            dtype=np.float_,
        )
    )

    max_equity_risk_value_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.max_equity_risk_value,
                   dtype=np.float_)
    )

    size_pct_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(order_settings_arrays_tuple.size_pct) / 100, dtype=np.float_
        )
    )

    size_value_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.size_value, dtype=np.float_)
    )

    # Stop Loss Arrays
    sl_pct_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(order_settings_arrays_tuple.sl_pct) / 100, dtype=np.float_
        )
    )

    # stop loss based on
    sl_based_on_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.sl_based_on, dtype=np.float_)
    )

    sl_based_on_add_pct_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(order_settings_arrays_tuple.sl_based_on_add_pct) / 100,
            dtype=np.float_,
        )
    )

    sl_based_on_lookback_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.sl_based_on_lookback,
                   dtype=np.float_)
    )

    # stop loss to break even
    sl_to_be_based_on_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.sl_to_be_based_on,
                   dtype=np.float_)
    )

    sl_to_be_when_pct_from_avg_entry_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(
                order_settings_arrays_tuple.sl_to_be_when_pct_from_avg_entry)
            / 100,
            dtype=np.float_,
        )
    )

    sl_to_be_zero_or_entry_array = to_1d_array_nb_testing(
        np.asarray(
            order_settings_arrays_tuple.sl_to_be_zero_or_entry, dtype=np.float_)
    )

    # Trailing Stop Loss Arrays
    trail_sl_based_on_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.trail_sl_based_on,
                   dtype=np.float_)
    )
    trail_sl_by_pct_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(order_settings_arrays_tuple.trail_sl_by_pct) / 100,
            dtype=np.float_,
        )
    )
    trail_sl_when_pct_from_avg_entry_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(
                order_settings_arrays_tuple.trail_sl_when_pct_from_avg_entry)
            / 100,
            dtype=np.float_,
        )
    )

    # Take Profit Arrays
    risk_reward_array = to_1d_array_nb_testing(
        np.asarray(order_settings_arrays_tuple.risk_reward, dtype=np.float_)
    )

    tp_pct_array = to_1d_array_nb_testing(
        np.asarray(
            np.asarray(order_settings_arrays_tuple.tp_pct) / 100,
            dtype=np.float_,
        )
    )

    return OrderSettingsArrays(
        leverage=leverage_array,
        max_equity_risk_pct=max_equity_risk_pct_array,
        max_equity_risk_value=max_equity_risk_value_array,
        risk_reward=risk_reward_array,
        size_pct=size_pct_array,
        size_value=size_value_array,
        sl_based_on=sl_based_on_array,
        sl_based_on_add_pct=sl_based_on_add_pct_array,
        sl_based_on_lookback=sl_based_on_lookback_array,
        sl_pct=sl_pct_array,
        sl_to_be_based_on=sl_to_be_based_on_array,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_array,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_array,
        tp_pct=tp_pct_array,
        trail_sl_based_on=trail_sl_based_on_array,
        trail_sl_by_pct=trail_sl_by_pct_array,
        trail_sl_when_pct_from_avg_entry=trail_sl_when_pct_from_avg_entry_array,
    )


@njit(cache=True)
def check_os_1d_arrays_nb_testing(
    order_settings_arrays_tuple: OrderSettingsArrays,
    static_variables_tuple: StaticVariables,
):
    check_sl_for_nan = (
        np.isnan(order_settings_arrays_tuple.sl_based_on).any()
        and np.isnan(order_settings_arrays_tuple.sl_pct).any()
    )

    # Size Value
    if np.isfinite(order_settings_arrays_tuple.size_value).all():
        if order_settings_arrays_tuple.size_value.any() < 1:
            raise ValueError("size_value must be greater than 1.")
        if (
            order_settings_arrays_tuple.size_value.any()
            > static_variables_tuple.max_order_size_value
        ):
            raise ValueError("size_value is greater than max_order_size_value")

        if (
            order_settings_arrays_tuple.size_value.any()
            < static_variables_tuple.min_order_size_value
        ):
            raise ValueError("size_value is greater than max_order_size_value")

    # Size Pct
    if not np.isfinite(order_settings_arrays_tuple.size_pct).all():
        if order_settings_arrays_tuple.size_pct.any() < 1:
            raise ValueError("size_pct must be greater than 1.")

        if (
            order_settings_arrays_tuple.size_pct.any()
            > static_variables_tuple.max_order_size_pct
        ):
            raise ValueError("size_pct is greater than max_order_size_pct")

        if (
            order_settings_arrays_tuple.size_pct.any()
            < static_variables_tuple.min_order_size_pct
        ):
            raise ValueError("size_pct is greater than max_order_size_pct")

    if (
        not np.isnan(order_settings_arrays_tuple.size_value).any()
        and not np.isnan(order_settings_arrays_tuple.size_pct).any()
    ):
        raise ValueError(
            "You can't have size and size pct set at the same time.")

    # Size Type Checks
    if static_variables_tuple.size_type == SizeType.Amount:
        if (
            np.isnan(order_settings_arrays_tuple.size_value).any()
            or order_settings_arrays_tuple.size_value.any() < 1
        ):
            raise ValueError(
                "With SizeType as amount, size_value must be 1 or greater."
            )

    if static_variables_tuple.size_type == SizeType.PercentOfAccount:
        if np.isnan(order_settings_arrays_tuple.size_pct).any():
            raise ValueError(
                "You need size_pct to be > 0 if using percent of account.")

    if (
        static_variables_tuple.size_type == SizeType.RiskAmount
        or (static_variables_tuple.size_type == SizeType.RiskPercentOfAccount)
        and check_sl_for_nan
    ):
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl pct or tsl pct > 0"
        )

    if static_variables_tuple.size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(order_settings_arrays_tuple.size_pct).any():
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account."
            )

    # Max Equity
    if (
        np.isinf(order_settings_arrays_tuple.max_equity_risk_pct).any()
        or order_settings_arrays_tuple.max_equity_risk_pct.any() < 0
    ):
        raise ValueError(
            "Max equity risk percent has to be greater than 0 or np.nan")

    if (
        np.isinf(order_settings_arrays_tuple.max_equity_risk_value).any()
        or order_settings_arrays_tuple.max_equity_risk_value.any() < 0
    ):
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    if (
        not np.isnan(order_settings_arrays_tuple.max_equity_risk_pct).any()
        and not np.isnan(order_settings_arrays_tuple.max_equity_risk_value).any()
    ):
        raise ValueError(
            "You can't have max risk pct and max risk value both set at the same time."
        )

    # Leverage
    if (0 > static_variables_tuple.lev_mode > len(LeverageMode)) or not np.isfinite(
        static_variables_tuple.lev_mode
    ):
        raise ValueError("leverage mode is out of range or not finite")

    if static_variables_tuple.lev_mode == LeverageMode.Isolated:
        if not np.isfinite(order_settings_arrays_tuple.leverage).any() or (
            order_settings_arrays_tuple.leverage.any() > static_variables_tuple.max_lev
            or order_settings_arrays_tuple.leverage.any() < 0
        ):
            raise ValueError("leverage needs to be between 1 and max lev")

    if static_variables_tuple.lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_for_nan:
            raise ValueError(
                "When using Least Free Cash Used set a proper sl or tsl > 0"
            )
        if np.isfinite(order_settings_arrays_tuple.leverage).any():
            raise ValueError(
                "When using Least Free Cash Used leverage iso must be np.nan"
            )

    # Stop Loss init
    if (
        np.isinf(order_settings_arrays_tuple.sl_pct).any()
        or order_settings_arrays_tuple.sl_pct.any() < 0
    ):
        raise ValueError("sl_pct has to be nan or greater than 0 and not inf")

    # Stop Loss based on
    if (
        np.isinf(order_settings_arrays_tuple.sl_based_on_add_pct).any()
        or order_settings_arrays_tuple.sl_based_on_add_pct.any() < 0
    ):
        raise ValueError(
            "sl_based_on_add_pct has to be nan or greater than 0 and not inf"
        )

    if (
        np.isinf(order_settings_arrays_tuple.sl_based_on_lookback).any()
        or order_settings_arrays_tuple.sl_based_on_lookback.any() < 0
    ):
        raise ValueError(
            "sl_based_on_lookback has to be nan or greater than 0 and not inf"
        )

    if (
        np.isfinite(order_settings_arrays_tuple.sl_based_on_add_pct).any()
        or np.isfinite(order_settings_arrays_tuple.sl_based_on_lookback).any()
    ) and not np.isfinite(order_settings_arrays_tuple.sl_based_on).any():
        raise ValueError(
            "sl_based_on has to be set in order to use sl_based_on_add_pct or sl_based_on_lookback"
        )

    if np.isfinite(order_settings_arrays_tuple.sl_based_on).any() and (
        order_settings_arrays_tuple.sl_based_on.any() < CandleBody.open
        or order_settings_arrays_tuple.sl_based_on.any() > CandleBody.close
    ):
        raise ValueError(
            "You need sl_based_on to be be either open, high , low, or close. look up CandleBody enums"
        )

    if (
        np.isfinite(order_settings_arrays_tuple.sl_based_on).any()
        and np.isfinite(order_settings_arrays_tuple.sl_pct).any()
    ):
        raise ValueError(
            "You can't have sl based on and sl init set at the same time.")

    # Stop loss to break even
    if np.isfinite(order_settings_arrays_tuple.sl_to_be_based_on).any() and (
        order_settings_arrays_tuple.sl_to_be_based_on.any() < CandleBody.open
        or order_settings_arrays_tuple.sl_to_be_based_on.any() > CandleBody.close
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either open, high , low, or close. look up CandleBody enums"
        )

    if (
        order_settings_arrays_tuple.sl_to_be_zero_or_entry.any() < 0
        or order_settings_arrays_tuple.sl_to_be_zero_or_entry.any() > 1
    ):
        raise ValueError(
            "sl_to_be_zero_or_entry needs to be 0 for zero or 1 for entry")

    if (
        np.isinf(order_settings_arrays_tuple.sl_to_be_when_pct_from_avg_entry).any()
        or order_settings_arrays_tuple.sl_to_be_when_pct_from_avg_entry.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_when_pct_from_avg_entry to be > 0 or not inf."
        )
    if (
        np.isfinite(order_settings_arrays_tuple.sl_to_be_zero_or_entry).any()
        or np.isfinite(order_settings_arrays_tuple.sl_to_be_based_on).any()
        or np.isfinite(
            order_settings_arrays_tuple.sl_to_be_when_pct_from_avg_entry
        ).any()
    ) and (
        not np.isfinite(order_settings_arrays_tuple.sl_based_on).any()
        or not np.isfinite(order_settings_arrays_tuple.sl_pct).any()
    ):
        raise ValueError(
            "You need sl_init or sl_based_on to be set to use stop loss to break even"
        )

    # Trailing Stop Loss
    if np.isfinite(order_settings_arrays_tuple.trail_sl_based_on).any() and (
        order_settings_arrays_tuple.trail_sl_based_on.any() < CandleBody.open
        or order_settings_arrays_tuple.trail_sl_based_on.any() > CandleBody.close
    ):
        raise ValueError(
            "You need trail_sl_based_on to be be either open, high , low, or close. look up CandleBody enums"
        )

    if (
        np.isinf(order_settings_arrays_tuple.trail_sl_when_pct_from_avg_entry).any()
        or order_settings_arrays_tuple.trail_sl_when_pct_from_avg_entry.any() < 0
    ):
        raise ValueError(
            "You need trail_sl_when_pct_from_avg_entry to be > 0 or not inf."
        )

    if (
        np.isinf(order_settings_arrays_tuple.trail_sl_by_pct).any()
        or order_settings_arrays_tuple.trail_sl_by_pct.any() < 0
    ):
        raise ValueError("You need trail_sl_by_pct to be > 0 or not inf.")

    if (
        np.isfinite(order_settings_arrays_tuple.trail_sl_by_pct).any()
        or np.isfinite(
            order_settings_arrays_tuple.trail_sl_when_pct_from_avg_entry
        ).any()
        or np.isfinite(order_settings_arrays_tuple.trail_sl_based_on).any()
    ) and (
        not np.isfinite(order_settings_arrays_tuple.sl_based_on).any()
        or not np.isfinite(order_settings_arrays_tuple.sl_pct).any()
    ):
        raise ValueError(
            "You need sl_init or sl_based_on to be set to use a trailing stop loss"
        )

    # Risk To Reward and TP
    if (
        np.isinf(order_settings_arrays_tuple.risk_reward).any()
        or order_settings_arrays_tuple.risk_reward.any() < 0
    ):
        raise ValueError("Risk to Reward has to be greater than 0 or np.nan")

    if (
        not np.isnan(order_settings_arrays_tuple.risk_reward).any()
        and check_sl_for_nan
    ):
        raise ValueError("When risk to reward is set you have to have a sl")

    if (
        order_settings_arrays_tuple.risk_reward.any() > 0
        and np.isfinite(order_settings_arrays_tuple.tp_pct).any()
    ):
        raise ValueError(
            "You can't have take profits set when using Risk to reward")


@njit(cache=True)
def create_os_cart_product_nb_testing(
    order_settings_arrays_tuple: OrderSettingsArrays,
):
    # dtype_names = (
    #     'order_settings_id',
    #     'leverage',
    #     'max_equity_risk_pct',
    #     'max_equity_risk_value',
    #     'risk_reward',
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
    for x in order_settings_arrays_tuple:
        n *= x.size
    out = np.empty((n, len(order_settings_arrays_tuple)))

    for i in range(len(order_settings_arrays_tuple)):
        m = int(n / order_settings_arrays_tuple[i].size)
        out[:n, i] = np.repeat(order_settings_arrays_tuple[i], m)
        n //= order_settings_arrays_tuple[i].size

    n = order_settings_arrays_tuple[-1].size
    for k in range(len(order_settings_arrays_tuple) - 2, -1, -1):
        n *= order_settings_arrays_tuple[k].size
        m = int(n / order_settings_arrays_tuple[k].size)
        for j in range(1, order_settings_arrays_tuple[k].size):
            out[j * m: (j + 1) * m, k + 1:] = out[0:m, k + 1:]

    # # literal unroll
    # counter = 0
    # for dtype_name in literal_unroll(dtype_names):
    #     for col in range(n):
    #         cart_array[dtype_name][col] = out[col][counter]
    #     counter += 1

    # leverage_cart_array = cart_array['leverage']
    # max_equity_risk_pct_cart_array = cart_array['max_equity_risk_pct']
    # max_equity_risk_value_cart_array = cart_array['max_equity_risk_value']
    # risk_reward_cart_array = cart_array['risk_reward']
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

    return OrderSettingsArrays(
        leverage=out.T[0],
        max_equity_risk_pct=out.T[1],
        max_equity_risk_value=out.T[2],
        risk_reward=out.T[3],
        size_pct=out.T[4],
        size_value=out.T[5],
        sl_based_on=out.T[6],
        sl_based_on_add_pct=out.T[7],
        sl_based_on_lookback=out.T[8],
        sl_pct=out.T[9],
        sl_to_be_based_on=out.T[10],
        sl_to_be_when_pct_from_avg_entry=out.T[11],
        sl_to_be_zero_or_entry=out.T[12],
        tp_pct=out.T[13],
        trail_sl_based_on=out.T[14],
        trail_sl_by_pct=out.T[15],
        trail_sl_when_pct_from_avg_entry=out.T[16],
    )


@njit(cache=True)
def boradcast_to_1d_arrays_nb_testing(
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
    max_equity_risk_pct_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[1], biggest)
    max_equity_risk_value_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[2], biggest)
    risk_reward_braodcast_array = np.broadcast_to(arrays_1d_tuple[3], biggest)
    size_pct_braodcast_array = np.broadcast_to(arrays_1d_tuple[4], biggest)
    size_value_braodcast_array = np.broadcast_to(arrays_1d_tuple[5], biggest)
    sl_based_on_add_pct_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[6], biggest)
    sl_based_on_braodcast_array = np.broadcast_to(arrays_1d_tuple[7], biggest)
    sl_pcts_braodcast_array = np.broadcast_to(arrays_1d_tuple[8], biggest)
    sl_to_be_based_on_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[9], biggest)
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
    tsl_based_on_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[14], biggest)
    tsl_pcts_init_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[15], biggest)
    tsl_trail_by_pct_braodcast_array = np.broadcast_to(
        arrays_1d_tuple[16], biggest)
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
        risk_reward=risk_reward_braodcast_array,
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
def get_to_the_upside_nb_testing(
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
def fill_order_records_nb_testing(
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
    order_records["sl_price"] = order_result.sl_price
    order_records["tp_price"] = order_result.tp_price

    order_records_id[0] += 1


@njit(cache=True)
def fill_strat_records_nb_testing(
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
def fill_strategy_result_records_nb_testing(
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
def fill_order_settings_result_records_nb_testing(
    entries_col: int,
    order_settings_tuple: OrderSettings,
    order_settings_result_records: RecordArray,
    symbol_counter: int,
) -> RecordArray:
    order_settings_result_records["symbol"] = symbol_counter
    order_settings_result_records["entries_col"] = entries_col
    order_settings_result_records["leverage"] = order_settings_tuple.leverage
    order_settings_result_records["max_equity_risk_pct"] = (
        order_settings_tuple.max_equity_risk_pct * 100
    )
    order_settings_result_records[
        "max_equity_risk_value"
    ] = order_settings_tuple.max_equity_risk_value
    order_settings_result_records["risk_reward"] = order_settings_tuple.risk_reward
    order_settings_result_records["size_pct"] = order_settings_tuple.size_pct * 100
    order_settings_result_records["size_value"] = order_settings_tuple.size_value
    order_settings_result_records["sl_based_on"] = order_settings_tuple.sl_based_on
    order_settings_result_records["sl_based_on_add_pct"] = order_settings_tuple.sl_based_on_add_pct * 100
    order_settings_result_records["sl_based_on_lookback"] = order_settings_tuple.sl_based_on_lookback
    order_settings_result_records["sl_pct"] = order_settings_tuple.sl_pct * 100
    order_settings_result_records["sl_to_be_based_on"] = order_settings_tuple.sl_to_be_based_on
    order_settings_result_records["sl_to_be_when_pct_from_avg_entry"] = order_settings_tuple.sl_to_be_when_pct_from_avg_entry * 100
    order_settings_result_records["sl_to_be_zero_or_entry"] = order_settings_tuple.sl_to_be_zero_or_entry
    order_settings_result_records["tp_pct"] = order_settings_tuple.tp_pct * 100
    order_settings_result_records["trail_sl_based_on"] = order_settings_tuple.trail_sl_based_on
    order_settings_result_records["trail_sl_by_pct"] = order_settings_tuple.trail_sl_by_pct * 100
    order_settings_result_records["trail_sl_when_pct_from_avg_entry"] = order_settings_tuple.trail_sl_when_pct_from_avg_entry * 100


@njit(cache=True)
def to_1d_array_nb_testing(var: PossibleArray) -> Array1d:
    """Resize array to one dimension."""
    if var.ndim == 0:
        return np.expand_dims(var, axis=0)
    if var.ndim == 1:
        return var
    if var.ndim == 2 and var.shape[1] == 1:
        return var[:, 0]
    raise ValueError("to 1d array problem")


@njit(cache=True)
def to_2d_array_nb_testing(var: PossibleArray, expand_axis: int = 1) -> Array2d:
    if var.ndim == 0:
        return np.expand_dims(np.expand_dims(var, axis=0), axis=0)
    if var.ndim == 1:
        return np.expand_dims(var, axis=expand_axis)
    if var.ndim == 2:
        return var
    raise ValueError("to 2d array problem")
