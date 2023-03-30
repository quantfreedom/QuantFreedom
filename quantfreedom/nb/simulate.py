"""
Testing the tester
"""

import numpy as np
from numba import njit
from quantfreedom._typing import PossibleArray, Array1d
from quantfreedom.nb.helper_funcs import static_var_checker, to_1d_array_nb
from quantfreedom.nb.execute_funcs import process_order_nb, check_sl_tp_nb
from quantfreedom.enums.enums import (
    final_array_dt,
    or_dt,
    strat_df_array_dt,
    strat_records_dt,
    LeverageMode,
    OrderType,
    SizeType,
    SL_BE_or_Trail_BasedOn,
    AccountState,
    EntryOrder,
    OrderResult,
    StopsOrder,
    settings_array_dt,
)


@njit(cache=True)
def backtest_df_array_only(
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
    max_lev: float = 100.0,
    max_order_size_pct: float = 100.0,
    min_order_size_pct: float = 0.01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.0,
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
) -> tuple[Array1d, Array1d, Array1d]:

    # Static checks
    static_variables = static_var_checker(
        equity=equity,
        fee_pct=fee_pct,
        mmr=mmr,
        lev_mode=lev_mode,
        order_type=order_type,
        size_type=size_type,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        min_order_size_pct=min_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_value=min_order_size_value,
        sl_to_be=sl_to_be,
        sl_to_be_then_trail=sl_to_be_then_trail,
        tsl_true_or_false=tsl_true_or_false,
        gains_pct_filter=gains_pct_filter,
        total_trade_filter=total_trade_filter,
    )

    og_equity = equity

    # Order Arrays
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

    sl_to_be_trail_by_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(
            np.asarray(sl_to_be_trail_by_when_pct_from_avg_entry) / 100, dtype=np.float_
        )
    )

    sl_to_be_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_to_be_when_pct_from_avg_entry) /
                   100, dtype=np.float_)
    )

    sl_to_be_zero_or_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_zero_or_entry, dtype=np.float_)
    )

    # Trailing Stop Loss Arrays
    tsl_pcts_init_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_pcts_init) / 100, dtype=np.float_)
    )

    tsl_based_on_array = to_1d_array_nb(
        np.asarray(tsl_based_on, dtype=np.float_))

    tsl_trail_by_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_trail_by_pct) / 100, dtype=np.float_)
    )

    tsl_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_when_pct_from_avg_entry) /
                   100, dtype=np.float_)
    )

    # Take Profit Arrays
    risk_rewards_array = to_1d_array_nb(
        np.asarray(risk_rewards, dtype=np.float_))

    tp_pcts_array = to_1d_array_nb(
        np.asarray(np.asarray(tp_pcts) / 100, dtype=np.float_)
    )

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
        raise ValueError("sl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(tsl_pcts_init_array).any() or tsl_pcts_init_array.any() < 0:
        raise ValueError(
            "tsl_pcts_init has to be nan or greater than 0 and not inf")

    if np.isinf(tp_pcts_array).any() or tp_pcts_array.any() < 0:
        raise ValueError("tp_pcts has to be nan or greater than 0 and not inf")

    if (0 > lev_mode > len(LeverageMode)) or not np.isfinite(lev_mode):
        raise ValueError("leverage mode is out of range or not finite")

    check_sl_tsl_for_nan = (
        np.isnan(sl_pcts_array).any() and np.isnan(tsl_pcts_init_array).any()
    )

    # if leverage is too big or too small
    if lev_mode == LeverageMode.Isolated:
        if not np.isfinite(leverage_array).any() or (
            leverage_array.any() > max_lev or leverage_array.any() < 0
        ):
            raise ValueError("leverage needs to be between 1 and max lev")
    if lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise ValueError(
                "When using Least Free Cash Used set a proper sl or tsl > 0"
            )
        if np.isfinite(leverage_array).any():
            raise ValueError(
                "When using Least Free Cash Used leverage iso must be np.nan"
            )

    # making sure we have a number greater than 0 for rr
    if np.isinf(risk_rewards_array).any() or risk_rewards_array.any() < 0:
        raise ValueError("Risk Rewards has to be greater than 0 or np.nan")

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

    elif (
        np.isinf(max_equity_risk_value_array).any()
        or max_equity_risk_value_array.any() < 0
    ):
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    if (
        not np.isnan(max_equity_risk_pct_array).any()
        and not np.isnan(max_equity_risk_value_array).any()
    ):
        raise ValueError(
            "You can't have max risk pct and max risk value both set at the same time."
        )
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
                "With SizeType as amount, size_value must be 1 or greater."
            )

    if size_type == SizeType.PercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using percent of account.")

    # checking to see if you set a stop loss for risk based size types
    if (
        size_type == SizeType.RiskAmount
        or (size_type == SizeType.RiskPercentOfAccount)
        and check_sl_tsl_for_nan
    ):
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl pct or tsl pct > 0"
        )

    # setting risk percent size
    if size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account."
            )

    # stop loss break even checks
    if np.isfinite(sl_to_be_based_on_array).any() and (
        sl_to_be_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price
        or sl_to_be_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums"
        )

    if (
        np.isinf(sl_to_be_trail_by_when_pct_from_avg_entry_array).any()
        or sl_to_be_trail_by_when_pct_from_avg_entry_array.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_trail_by_when_pct_from_avg_entry to be > 0 or not inf."
        )

    if (
        np.isinf(sl_to_be_when_pct_from_avg_entry_array).any()
        or sl_to_be_when_pct_from_avg_entry_array.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_when_pct_from_avg_entry to be > 0 or not inf."
        )

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
                "sl_to_be needs to be True to use sl_to_be_trail_by_when_pct_from_avg_entry."
            )
        if np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_when_pct_from_avg_entry."
            )
        if np.isfinite(sl_to_be_zero_or_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_zero_or_entry.")

    if sl_to_be and (
        not np.isfinite(sl_to_be_based_on_array).any()
        or not np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any()
        or not np.isfinite(sl_to_be_zero_or_entry_array).any()
        or not np.isfinite(sl_pcts_array).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts etc"
        )

    if (sl_to_be and sl_to_be_then_trail) and (
        not np.isfinite(sl_to_be_based_on_array).any()
        or not np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any()
        or not np.isfinite(sl_to_be_zero_or_entry_array).any()
        or not np.isfinite(sl_to_be_trail_by_when_pct_from_avg_entry_array).any()
        or not np.isfinite(sl_pcts_array).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts etc"
        )

    # tsl Checks
    if np.isfinite(tsl_based_on_array).any() and (
        tsl_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price
        or tsl_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need tsl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums"
        )

    if np.isinf(tsl_trail_by_pct_array).any() or tsl_trail_by_pct_array.any() < 0:
        raise ValueError("You need tsl_trail_by_pct to be > 0 or not inf.")

    if (
        np.isinf(tsl_when_pct_from_avg_entry_array).any()
        or tsl_when_pct_from_avg_entry_array.any() < 0
    ):
        raise ValueError(
            "You need tsl_when_pct_from_avg_entry to be > 0 or not inf.")

    if tsl_true_or_false == False:
        if np.isfinite(tsl_based_on_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_based_on.")
        if np.isfinite(tsl_trail_by_pct_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_trail_by_pct."
            )
        if np.isfinite(tsl_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_when_pct_from_avg_entry."
            )

    if tsl_true_or_false and (
        not np.isfinite(tsl_based_on_array).any()
        or not np.isfinite(tsl_trail_by_pct_array).any()
        or not np.isfinite(tsl_when_pct_from_avg_entry_array).any()
        or not np.isfinite(tsl_pcts_init_array).any()
    ):
        raise ValueError(
            "If you have tsl_true_or_false set to true then you must provide the other params like tsl_pcts_init etc"
        )

    # Cart of new arrays
    arrays = (
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
    for x in arrays:
        n *= x.size
    out = np.empty((n, len(arrays)))

    for i in range(len(arrays)):
        m = int(n / arrays[i].size)
        out[:n, i] = np.repeat(arrays[i], m)
        n //= arrays[i].size

    n = arrays[-1].size
    for k in range(len(arrays) - 2, -1, -1):
        n *= arrays[k].size
        m = int(n / arrays[k].size)
        for j in range(1, arrays[k].size):
            out[j * m: (j + 1) * m, k + 1:] = out[0:m, k + 1:]

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
    sl_pcts_cart_array = out.T[6]
    sl_to_be_based_on_cart_array = out.T[7]
    sl_to_be_trail_by_when_pct_from_avg_entry_cart_array = out.T[8]
    sl_to_be_when_pct_from_avg_entry_cart_array = out.T[9]
    sl_to_be_zero_or_entry_cart_array = out.T[10]
    tp_pcts_cart_array = out.T[11]
    tsl_based_on_cart_array = out.T[12]
    tsl_pcts_init_cart_array = out.T[13]
    tsl_trail_by_cart_array = out.T[14]
    tsl_when_pct_from_avg_entry_cart_array = out.T[15]

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
    # tsl_trail_by_cart_array = cart_array['tsl_trail_by_pct']
    # tsl_when_pct_from_avg_entry_cart_array = cart_array['tsl_when_pct_from_avg_entry']

    out = 0
    arrays = 0

    # Creating Settings Vars
    total_order_settings = sl_pcts_cart_array.shape[0]

    total_indicator_settings = entries.shape[1]

    total_bars = open_prices.shape[0]

    # Creating strat records
    strat_df_array = np.empty(
        total_indicator_settings * total_order_settings, dtype=strat_df_array_dt
    )
    settings_df_array = np.empty(
        total_indicator_settings * total_order_settings, dtype=settings_array_dt
    )
    strat_arrays_filled = 0

    strat_records = np.empty(int(total_bars / 1.5), dtype=strat_records_dt)
    strat_records_filled = np.array([0])

    # order settings loops
    for order_settings_counter in range(total_order_settings):

        entry_order = EntryOrder(
            leverage=leverage_cart_array[order_settings_counter],
            max_equity_risk_pct=max_equity_risk_pct_cart_array[order_settings_counter],
            max_equity_risk_value=max_equity_risk_value_cart_array[
                order_settings_counter
            ],
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
                order_settings_counter
            ],
            sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_cart_array[
                order_settings_counter
            ],
            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_cart_array[
                order_settings_counter
            ],
            tsl_based_on=tsl_based_on_cart_array[order_settings_counter],
            tsl_trail_by_pct=tsl_trail_by_cart_array[order_settings_counter],
            tsl_true_or_false=tsl_true_or_false,
            tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_cart_array[
                order_settings_counter
            ],
        )

        # ind set loop
        for indicator_settings_counter in range(total_indicator_settings):

            current_indicator_entries = entries[:, indicator_settings_counter]

            # Account State Reset
            account_state = AccountState(
                available_balance=og_equity,
                cash_borrowed=0.0,
                cash_used=0.0,
                equity=og_equity,
            )

            # Order Result Reset
            order_result = OrderResult(
                average_entry=0.0,
                fees_paid=0.0,
                leverage=0.0,
                liq_price=np.nan,
                moved_sl_to_be=False,
                order_status=0,
                order_status_info=0,
                order_type=entry_order.order_type,
                pct_chg_trade=0.0,
                position=0.0,
                price=0.0,
                realized_pnl=0.0,
                size_value=0.0,
                sl_pcts=0.0,
                sl_prices=0.0,
                tp_pcts=0.0,
                tp_prices=0.0,
                tsl_pcts_init=0.0,
                tsl_prices=0.0,
            )
            strat_records_filled[0] = 0

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
                        strat_records=strat_records[strat_records_filled[0]],
                        strat_records_filled=strat_records_filled,
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
                        bar=bar,
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
                            strat_records=strat_records[strat_records_filled[0]],
                            strat_records_filled=strat_records_filled,
                        )

            # Checking if gains
            gains_pct = ((account_state.equity - og_equity) / og_equity) * 100
            if gains_pct > gains_pct_filter:
                temp_order_records = strat_records[0: strat_records_filled[0]]
                w_l = temp_order_records["real_pnl"][
                    ~np.isnan(temp_order_records["real_pnl"])
                ]
                # Checking total trade filter
                if w_l.size > total_trade_filter:

                    w_l_no_be = w_l[w_l != 0]  # filter out all BE trades

                    # win rate calc
                    win_loss = np.where(w_l_no_be < 0, 0, 1)
                    win_rate = round(
                        np.count_nonzero(win_loss) / win_loss.size * 100, 2
                    )

                    total_pnl = temp_order_records["real_pnl"][
                        ~np.isnan(temp_order_records["real_pnl"])
                    ].sum()

                    # to_the_upside calculation
                    x = np.arange(1, len(w_l_no_be) + 1)
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

                    # strat array
                    strat_df_array["or_set"][strat_arrays_filled] = temp_order_records[
                        "or_set"
                    ][0]
                    strat_df_array["ind_set"][strat_arrays_filled] = temp_order_records[
                        "ind_set"
                    ][0]
                    strat_df_array["total_trades"][strat_arrays_filled] = w_l.size
                    strat_df_array["gains_pct"][strat_arrays_filled] = gains_pct
                    strat_df_array["win_rate"][strat_arrays_filled] = win_rate
                    strat_df_array["to_the_upside"][strat_arrays_filled] = to_the_upside
                    strat_df_array["total_pnl"][strat_arrays_filled] = total_pnl
                    strat_df_array["ending_eq"][
                        strat_arrays_filled
                    ] = temp_order_records["equity"][-1]

                    settings_df_array["order_set_id"][strat_arrays_filled] = order_settings_counter
                    settings_df_array["ind_set_id"][strat_arrays_filled] = indicator_settings_counter
                    settings_df_array["leverage"][strat_arrays_filled] = entry_order.leverage
                    settings_df_array["max_equity_risk_pct"][strat_arrays_filled] = entry_order.max_equity_risk_pct * 100
                    settings_df_array["max_equity_risk_value"][strat_arrays_filled] = entry_order.max_equity_risk_value
                    settings_df_array["risk_rewards"][strat_arrays_filled] = entry_order.risk_rewards
                    settings_df_array["size_pct"][strat_arrays_filled] = entry_order.size_pct * 100
                    settings_df_array["size_value"][strat_arrays_filled] = entry_order.size_value
                    settings_df_array["sl_pcts"][strat_arrays_filled] = entry_order.sl_pcts * 100
                    settings_df_array["sl_to_be_based_on"][strat_arrays_filled] = stops_order.sl_to_be_based_on
                    settings_df_array["sl_to_be_trail_by_when_pct_from_avg_entry"][
                        strat_arrays_filled] = stops_order.sl_to_be_trail_by_when_pct_from_avg_entry * 100
                    settings_df_array["sl_to_be_when_pct_from_avg_entry"][
                        strat_arrays_filled] = stops_order.sl_to_be_when_pct_from_avg_entry * 100
                    settings_df_array["sl_to_be_zero_or_entry"][strat_arrays_filled] = stops_order.sl_to_be_zero_or_entry
                    settings_df_array["tp_pcts"][strat_arrays_filled] = entry_order.tp_pcts * 100
                    settings_df_array["tsl_based_on"][strat_arrays_filled] = stops_order.tsl_based_on
                    settings_df_array["tsl_pcts_init"][strat_arrays_filled] = entry_order.tsl_pcts_init * 100
                    settings_df_array["tsl_trail_by_pct"][strat_arrays_filled] = stops_order.tsl_trail_by_pct * 100
                    settings_df_array["tsl_when_pct_from_avg_entry"][strat_arrays_filled] = stops_order.tsl_when_pct_from_avg_entry * 100

                    strat_arrays_filled += 1

    return strat_df_array[:strat_arrays_filled], settings_df_array[:strat_arrays_filled]


@njit(cache=True)
def simulate_up_to_6(
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
    max_lev: float = 100.0,
    max_order_size_pct: float = 100.0,
    min_order_size_pct: float = 0.01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.0,
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
) -> tuple[Array1d, Array1d, Array1d]:

    # Static checks & create
    static_variables = static_var_checker(
        equity=equity,
        fee_pct=fee_pct,
        mmr=mmr,
        lev_mode=lev_mode,
        order_type=order_type,
        size_type=size_type,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        min_order_size_pct=min_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_value=min_order_size_value,
        sl_to_be=sl_to_be,
        sl_to_be_then_trail=sl_to_be_then_trail,
        tsl_true_or_false=tsl_true_or_false,
        gains_pct_filter=0.0,
        total_trade_filter=0,
    )
    og_equity = equity

    # Order Arrays
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

    sl_to_be_trail_by_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(
            np.asarray(sl_to_be_trail_by_when_pct_from_avg_entry) / 100, dtype=np.float_
        )
    )

    sl_to_be_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(sl_to_be_when_pct_from_avg_entry) /
                   100, dtype=np.float_)
    )

    sl_to_be_zero_or_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_zero_or_entry, dtype=np.float_)
    )

    # Trailing Stop Loss Arrays
    tsl_pcts_init_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_pcts_init) / 100, dtype=np.float_)
    )

    tsl_based_on_array = to_1d_array_nb(
        np.asarray(tsl_based_on, dtype=np.float_))

    tsl_trail_by_pct_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_trail_by_pct) / 100, dtype=np.float_)
    )

    tsl_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(np.asarray(tsl_when_pct_from_avg_entry) /
                   100, dtype=np.float_)
    )

    # Take Profit Arrays
    risk_rewards_array = to_1d_array_nb(
        np.asarray(risk_rewards, dtype=np.float_))

    tp_pcts_array = to_1d_array_nb(
        np.asarray(np.asarray(tp_pcts) / 100, dtype=np.float_)
    )

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
        raise ValueError("sl_pcts has to be nan or greater than 0 and not inf")

    if np.isinf(tsl_pcts_init_array).any() or tsl_pcts_init_array.any() < 0:
        raise ValueError(
            "tsl_pcts_init has to be nan or greater than 0 and not inf")

    if np.isinf(tp_pcts_array).any() or tp_pcts_array.any() < 0:
        raise ValueError("tp_pcts has to be nan or greater than 0 and not inf")

    if (0 > lev_mode > len(LeverageMode)) or not np.isfinite(lev_mode):
        raise ValueError("leverage mode is out of range or not finite")

    check_sl_tsl_for_nan = (
        np.isnan(sl_pcts_array).any() and np.isnan(tsl_pcts_init_array).any()
    )

    # if leverage is too big or too small
    if lev_mode == LeverageMode.Isolated:
        if not np.isfinite(leverage_array).any() or (
            leverage_array.any() > max_lev or leverage_array.any() < 0
        ):
            raise ValueError("leverage needs to be between 1 and max lev")
    if lev_mode == LeverageMode.LeastFreeCashUsed:
        if check_sl_tsl_for_nan:
            raise ValueError(
                "When using Least Free Cash Used set a proper sl or tsl > 0"
            )
        if np.isfinite(leverage_array).any():
            raise ValueError(
                "When using Least Free Cash Used leverage iso must be np.nan"
            )

    # making sure we have a number greater than 0 for rr
    if np.isinf(risk_rewards_array).any() or risk_rewards_array.any() < 0:
        raise ValueError("Risk Rewards has to be greater than 0 or np.nan")

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

    elif (
        np.isinf(max_equity_risk_value_array).any()
        or max_equity_risk_value_array.any() < 0
    ):
        raise ValueError("Max equity risk has to be greater than 0 or np.nan")

    if (
        not np.isnan(max_equity_risk_pct_array).any()
        and not np.isnan(max_equity_risk_value_array).any()
    ):
        raise ValueError(
            "You can't have max risk pct and max risk value both set at the same time."
        )
    if not np.isnan(size_value_array).any() and not np.isnan(size_pct_array).any():
        raise ValueError(
            "You can't have size and size pct set at the same time.")

    # Getting the right size for Size Type Amount
    if size_type == SizeType.Amount:
        if np.isnan(size_value_array).any() or size_value_array.any() < 1:
            raise ValueError(
                "With SizeType as amount, size_value must be 1 or greater."
            )

    if size_type == SizeType.PercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using percent of account.")

    # checking to see if you set a stop loss for risk based size types
    if (
        size_type == SizeType.RiskAmount
        or (size_type == SizeType.RiskPercentOfAccount)
        and check_sl_tsl_for_nan
    ):
        raise ValueError(
            "When using Risk Amount or Risk Percent of Account set a proper sl pct or tsl pct > 0"
        )

    # setting risk percent size
    if size_type == SizeType.RiskPercentOfAccount:
        if np.isnan(size_pct_array).any():
            raise ValueError(
                "You need size_pct to be > 0 if using risk percent of account."
            )

    # stop loss break even checks
    if np.isfinite(sl_to_be_based_on_array).any() and (
        sl_to_be_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price
        or sl_to_be_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need sl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums"
        )

    if (
        np.isinf(sl_to_be_trail_by_when_pct_from_avg_entry_array).any()
        or sl_to_be_trail_by_when_pct_from_avg_entry_array.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_trail_by_when_pct_from_avg_entry to be > 0 or not inf."
        )

    if (
        np.isinf(sl_to_be_when_pct_from_avg_entry_array).any()
        or sl_to_be_when_pct_from_avg_entry_array.any() < 0
    ):
        raise ValueError(
            "You need sl_to_be_when_pct_from_avg_entry to be > 0 or not inf."
        )

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
                "sl_to_be needs to be True to use sl_to_be_trail_by_when_pct_from_avg_entry."
            )
        if np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_when_pct_from_avg_entry."
            )
        if np.isfinite(sl_to_be_zero_or_entry_array).any():
            raise ValueError(
                "sl_to_be needs to be True to use sl_to_be_zero_or_entry.")

    if sl_to_be and (
        not np.isfinite(sl_to_be_based_on_array).any()
        or not np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any()
        or not np.isfinite(sl_to_be_zero_or_entry_array).any()
        or not np.isfinite(sl_pcts_array).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts etc"
        )

    if (sl_to_be and sl_to_be_then_trail) and (
        not np.isfinite(sl_to_be_based_on_array).any()
        or not np.isfinite(sl_to_be_when_pct_from_avg_entry_array).any()
        or not np.isfinite(sl_to_be_zero_or_entry_array).any()
        or not np.isfinite(sl_to_be_trail_by_when_pct_from_avg_entry_array).any()
        or not np.isfinite(sl_pcts_array).any()
    ):
        raise ValueError(
            "If you have sl_to_be set to true then you must provide the other params like sl_pcts etc"
        )

    # tsl Checks
    if np.isfinite(tsl_based_on_array).any() and (
        tsl_based_on_array.any() < SL_BE_or_Trail_BasedOn.open_price
        or tsl_based_on_array.any() > SL_BE_or_Trail_BasedOn.close_price
    ):
        raise ValueError(
            "You need tsl_to_be_based_on to be be either 0 1 2 or 3. look up SL_BE_or_Trail_BasedOn enums"
        )

    if np.isinf(tsl_trail_by_pct_array).any() or tsl_trail_by_pct_array.any() < 0:
        raise ValueError("You need tsl_trail_by_pct to be > 0 or not inf.")

    if (
        np.isinf(tsl_when_pct_from_avg_entry_array).any()
        or tsl_when_pct_from_avg_entry_array.any() < 0
    ):
        raise ValueError(
            "You need tsl_when_pct_from_avg_entry to be > 0 or not inf.")

    if tsl_true_or_false == False:
        if np.isfinite(tsl_based_on_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_based_on.")
        if np.isfinite(tsl_trail_by_pct_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_trail_by_pct."
            )
        if np.isfinite(tsl_when_pct_from_avg_entry_array).any():
            raise ValueError(
                "tsl_true_or_false needs to be True to use tsl_when_pct_from_avg_entry."
            )

    if tsl_true_or_false and (
        not np.isfinite(tsl_based_on_array).any()
        or not np.isfinite(tsl_trail_by_pct_array).any()
        or not np.isfinite(tsl_when_pct_from_avg_entry_array).any()
        or not np.isfinite(tsl_pcts_init_array).any()
    ):
        raise ValueError(
            "If you have tsl_true_or_false set to true then you must provide the other params like tsl_pcts_init etc"
        )

    # Cart of new arrays
    broad_array = (
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

    x = 0
    biggest = 1
    while x < 7:
        if broad_array[x].size > 1:
            biggest = broad_array[x].size
            break
        x += 1

    while x < 7:
        if broad_array[x].size > 1 and broad_array[x].size != biggest:
            raise ValueError("Size mismatch")
        x += 1
    if biggest >= 6:
        raise ValueError("Total amount of tests must be <= 6")

    # Setting variable arrys from cart arrays
    leverage_cart_array = np.broadcast_to(broad_array[0], biggest)
    max_equity_risk_pct_cart_array = np.broadcast_to(broad_array[1], biggest)
    max_equity_risk_value_cart_array = np.broadcast_to(broad_array[2], biggest)
    risk_rewards_cart_array = np.broadcast_to(broad_array[3], biggest)
    size_pct_cart_array = np.broadcast_to(broad_array[4], biggest)
    size_value_cart_array = np.broadcast_to(broad_array[5], biggest)
    sl_pcts_cart_array = np.broadcast_to(broad_array[6], biggest)
    sl_to_be_based_on_cart_array = np.broadcast_to(broad_array[7], biggest)
    sl_to_be_trail_by_when_pct_from_avg_entry_cart_array = np.broadcast_to(
        broad_array[8], biggest
    )
    sl_to_be_when_pct_from_avg_entry_cart_array = np.broadcast_to(
        broad_array[9], biggest
    )
    sl_to_be_zero_or_entry_cart_array = np.broadcast_to(
        broad_array[10], biggest)
    tp_pcts_cart_array = np.broadcast_to(broad_array[11], biggest)
    tsl_based_on_cart_array = np.broadcast_to(broad_array[12], biggest)
    tsl_pcts_init_cart_array = np.broadcast_to(broad_array[13], biggest)
    tsl_trail_by_cart_array = np.broadcast_to(broad_array[14], biggest)
    tsl_when_pct_from_avg_entry_cart_array = np.broadcast_to(
        broad_array[15], biggest)

    if entries.shape[1] == 1:
        entries = np.broadcast_to(entries, (entries.shape[0], biggest))
    elif entries.shape[1] != biggest:
        raise ValueError("Something is wrong with entries")

    total_bars = open_prices.shape[0]

    broad_array = 0

    # Record Arrays
    final_array = np.empty(biggest, dtype=final_array_dt)
    final_array_counter = 0

    order_records = np.empty(total_bars * 2, dtype=or_dt)
    order_records_id = np.array([0])
    or_filled_start = 0

    # order settings loops
    for settings_counter in range(biggest):
        entry_order = EntryOrder(
            leverage=leverage_cart_array[settings_counter],
            max_equity_risk_pct=max_equity_risk_pct_cart_array[settings_counter],
            max_equity_risk_value=max_equity_risk_value_cart_array[settings_counter],
            order_type=order_type,
            risk_rewards=risk_rewards_cart_array[settings_counter],
            size_pct=size_pct_cart_array[settings_counter],
            size_value=size_value_cart_array[settings_counter],
            sl_pcts=sl_pcts_cart_array[settings_counter],
            tp_pcts=tp_pcts_cart_array[settings_counter],
            tsl_pcts_init=tsl_pcts_init_cart_array[settings_counter],
        )
        stops_order = StopsOrder(
            sl_to_be=sl_to_be,
            sl_to_be_based_on=sl_to_be_based_on_cart_array[settings_counter],
            sl_to_be_then_trail=sl_to_be_then_trail,
            sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry_cart_array[
                settings_counter
            ],
            sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry_cart_array[
                settings_counter
            ],
            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_cart_array[settings_counter],
            tsl_based_on=tsl_based_on_cart_array[settings_counter],
            tsl_trail_by_pct=tsl_trail_by_cart_array[settings_counter],
            tsl_true_or_false=tsl_true_or_false,
            tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry_cart_array[
                settings_counter
            ],
        )

        # Account State Reset
        account_state = AccountState(
            available_balance=og_equity,
            cash_borrowed=0.0,
            cash_used=0.0,
            equity=og_equity,
        )

        # Order Result Reset
        order_result = OrderResult(
            average_entry=0.0,
            fees_paid=0.0,
            leverage=0.0,
            liq_price=np.nan,
            moved_sl_to_be=False,
            order_status=0,
            order_status_info=0,
            order_type=entry_order.order_type,
            pct_chg_trade=0.0,
            position=0.0,
            price=0.0,
            realized_pnl=0.0,
            size_value=0.0,
            sl_pcts=0.0,
            sl_prices=0.0,
            tp_pcts=0.0,
            tp_prices=0.0,
            tsl_pcts_init=0.0,
            tsl_prices=0.0,
        )

        current_indicator_entries = entries[:, settings_counter]

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
                    indicator_settings_counter=settings_counter,
                    order_settings_counter=settings_counter,
                    order_records=order_records[order_records_id[0]],
                    order_records_id=order_records_id,
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
                    order_records=order_records[order_records_id[0]],
                    order_records_id=order_records_id,
                    bar=bar,
                    order_settings_counter=settings_counter,
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
                        indicator_settings_counter=settings_counter,
                        order_settings_counter=settings_counter,
                        order_records=order_records[order_records_id[0]],
                        order_records_id=order_records_id,
                    )

        # Checking if gains
        temp_order_records = order_records[or_filled_start: order_records_id[0]]
        or_filled_start = order_records_id[0]
        gains_pct = ((account_state.equity - og_equity) / og_equity) * 100

        w_l = temp_order_records["real_pnl"][~np.isnan(
            temp_order_records["real_pnl"])]

        w_l_no_be = w_l[w_l != 0]  # filter out all BE trades

        # win rate calc
        win_loss = np.where(w_l_no_be < 0, 0, 1)
        win_rate = round(np.count_nonzero(win_loss) / win_loss.size * 100, 2)

        total_pnl = temp_order_records["real_pnl"][
            ~np.isnan(temp_order_records["real_pnl"])
        ].sum()

        # to_the_upside calculation
        x = np.arange(1, len(w_l_no_be) + 1)
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
        final_array["total_trades"][final_array_counter] = w_l.size
        final_array["gains_pct"][final_array_counter] = gains_pct
        final_array["win_rate"][final_array_counter] = win_rate
        final_array["to_the_upside"][final_array_counter] = to_the_upside
        final_array["total_pnl"][final_array_counter] = total_pnl
        final_array["ending_eq"][final_array_counter] = temp_order_records["equity"][-1]
        final_array["settings_id"][final_array_counter] = final_array_counter
        final_array["leverage"][final_array_counter] = leverage_cart_array[
            final_array_counter
        ]
        final_array["max_equity_risk_pct"][final_array_counter] = (
            max_equity_risk_pct_cart_array[final_array_counter] * 100
        )
        final_array["max_equity_risk_value"][
            final_array_counter
        ] = max_equity_risk_value_cart_array[final_array_counter]
        final_array["risk_rewards"][final_array_counter] = risk_rewards_cart_array[
            final_array_counter
        ]
        final_array["size_pct"][final_array_counter] = (
            size_pct_cart_array[final_array_counter] * 100
        )
        final_array["size_value"][final_array_counter] = size_value_cart_array[
            final_array_counter
        ]
        final_array["sl_pcts"][final_array_counter] = (
            sl_pcts_cart_array[final_array_counter] * 100
        )
        final_array["sl_to_be_based_on"][
            final_array_counter
        ] = sl_to_be_based_on_cart_array[final_array_counter]
        final_array["sl_to_be_trail_by_when_pct_from_avg_entry"][
            final_array_counter
        ] = (
            sl_to_be_trail_by_when_pct_from_avg_entry_cart_array[final_array_counter]
            * 100
        )
        final_array["sl_to_be_when_pct_from_avg_entry"][final_array_counter] = (
            sl_to_be_when_pct_from_avg_entry_cart_array[final_array_counter] * 100
        )
        final_array["sl_to_be_zero_or_entry"][
            final_array_counter
        ] = sl_to_be_zero_or_entry_cart_array[final_array_counter]
        final_array["tp_pcts"][final_array_counter] = (
            tp_pcts_cart_array[final_array_counter] * 100
        )
        final_array["tsl_based_on"][final_array_counter] = tsl_based_on_cart_array[
            final_array_counter
        ]
        final_array["tsl_pcts_init"][final_array_counter] = (
            tsl_pcts_init_cart_array[final_array_counter] * 100
        )
        final_array["tsl_trail_by_pct"][final_array_counter] = (
            tsl_trail_by_cart_array[final_array_counter] * 100
        )
        final_array["tsl_when_pct_from_avg_entry"][final_array_counter] = (
            tsl_when_pct_from_avg_entry_cart_array[final_array_counter] * 100
        )

        final_array_counter += 1

    return final_array, order_records[: order_records_id[-1]]
