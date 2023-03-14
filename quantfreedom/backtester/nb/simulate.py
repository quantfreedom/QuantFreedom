"""
Testing the tester
"""

import numpy as np
from numba import literal_unroll, njit

from quantfreedom import _typing as tp
from quantfreedom.backtester.nb.helper_funcs import to_1d_array_nb
from quantfreedom.backtester.nb.execute_funcs import process_order_nb, process_stops_nb, check_sl_tp_nb
from quantfreedom.backtester.enums.enums import (
    cart_array_dt,
    ready_for_df,
    order_records_dt,
    log_records_dt,
    AccountState,
)


@njit(cache=True)
def simulate_from_signals(
    # entry info
    entries: tp.AnyArray,
    open_price: tp.AnyArray,

    # required account info
    equity: float,

    # required order
    lev_mode: int,
    order_type: int,
    size_type: int,

    # Price params
    high_price:  tp.Optional[tp.AnyArray] = None,
    low_price:  tp.Optional[tp.AnyArray] = None,
    close_price: tp.Optional[tp.AnyArray] = None,

    # Account Params
    fee_pct: float = 0.06,
    mmr: float = 0.5,

    # Order Params
    leverage: tp.ArrayLike = 0,
    max_equity_risk_pct: tp.ArrayLike = np.nan,
    max_equity_risk_value: tp.ArrayLike = np.nan,
    max_lev: float = 100.,
    max_order_size_pct: float = 100.,
    max_order_size_value: float = np.inf,
    min_order_size_pct: float = .01,
    min_order_size_value: float = 1.,
    size_pct: tp.ArrayLike = np.nan,
    size_value: tp.ArrayLike = np.nan,
    slippage_pct: float = np.nan,

    # Stop Losses
    sl_pcts: tp.ArrayLike = np.nan,
    sl_prices: tp.ArrayLike = np.nan,

    sl_to_be: tp.ArrayLike = False,
    sl_to_be_based_on: tp.ArrayLike = np.nan,
    sl_to_be_then_trail: tp.ArrayLike = False,
    sl_to_be_trail_when_pct_from_avg_entry: tp.ArrayLike = np.nan,
    sl_to_be_when_pct_from_avg_entry: tp.ArrayLike = np.nan,
    sl_to_be_zero_or_entry: tp.ArrayLike = np.nan,

    # Trailing Stop Loss Params
    tsl_pcts: tp.ArrayLike = np.nan,
    tsl_prices: tp.ArrayLike = np.nan,

    tsl_based_on: tp.ArrayLike = np.nan,
    tsl_true_or_false: tp.ArrayLike = False,
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

    og_equity = equity
    fee_pct /= 100
    mmr /= 100

    # Order Arrays
    leverage_array = to_1d_array_nb(np.asarray(leverage, dtype=np.float_))

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
        np.asarray(sl_to_be_then_trail, dtype=np.float_))

    sl_to_be_then_trail_array = to_1d_array_nb(
        np.asarray(sl_to_be_then_trail, dtype=np.float_))

    sl_to_be_trail_when_pct_from_avg_entry_array = to_1d_array_nb(
        np.asarray(sl_to_be_trail_when_pct_from_avg_entry, dtype=np.float_))

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

    arrays = (
        leverage_array,
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
        sl_to_be_trail_when_pct_from_avg_entry_array,
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
        'leverage_array',
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
        'sl_to_be_trail_when_pct_from_avg_entry_array',
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
    leverage_cart_array = cart_array['leverage_array']
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
    sl_to_be_trail_when_pct_from_avg_entry_cart_array = cart_array[
        'sl_to_be_trail_when_pct_from_avg_entry_array']
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

    cart_array = counter = out = dtype_names = arrays = \
        n = m = k = j = i = col = 0

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

        # set order settings
        leverage_order = leverage_cart_array[order_settings_counter]
        max_equity_risk_pct_order = max_equity_risk_pct_cart_array[order_settings_counter]
        max_equity_risk_value_order = max_equity_risk_value_cart_array[order_settings_counter]
        risk_rewards_order = risk_rewards_cart_array[order_settings_counter]
        size_pct_order = size_pct_cart_array[order_settings_counter]
        size_value_order = size_value_cart_array[order_settings_counter]

        sl_pcts_order = sl_pcts_cart_array[order_settings_counter]
        sl_prices_order = sl_prices_cart_array[order_settings_counter]

        sl_to_be_order = sl_to_be_cart_array[order_settings_counter]
        sl_to_be_based_on_order = sl_to_be_based_on_cart_array[order_settings_counter]
        sl_to_be_then_trail_order = sl_to_be_then_trail_cart_array[order_settings_counter]
        sl_to_be_trail_when_pct_from_avg_entry_order = sl_to_be_trail_when_pct_from_avg_entry_cart_array[
            order_settings_counter]
        sl_to_be_when_pct_from_avg_entry_order = sl_to_be_when_pct_from_avg_entry_cart_array[
            order_settings_counter]
        sl_to_be_zero_or_entry_order = sl_to_be_zero_or_entry_cart_array[order_settings_counter]

        tp_pcts_order = tp_pcts_cart_array[order_settings_counter]
        tp_prices_order = tp_prices_cart_array[order_settings_counter]

        tsl_pcts_order = tsl_pcts_cart_array[order_settings_counter]
        tsl_prices_order = tsl_prices_cart_array[order_settings_counter]

        tsl_based_on_order = tsl_based_on_cart_array[order_settings_counter]
        tsl_trail_by_order = tsl_trail_by_cart_array[order_settings_counter]
        tsl_true_or_false_order = tsl_true_or_false_cart_array[order_settings_counter]
        tsl_when_pct_from_avg_entry_order = tsl_when_pct_from_avg_entry_cart_array[
            order_settings_counter]

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
                cash_borrowed=0.,
                cash_used=0.,
                equity=og_equity,
                fee_pct=fee_pct,
                log_count_id=log_count_id,
                log_records_filled=0,
                mmr=mmr,
                order_count_id=order_count_id,
                order_records_filled=0,
            )
            # log_and_order_records =
            available_balance = equity
            cash_borrowed = 0.
            cash_used = 0.
            equity = og_equity
            log_records_filled = 0
            order_count_id = 0
            order_records_filled = 0

            # Order Result Reset
            average_entry = 0.
            position = 0.
            liq_price = np.nan
            moved_sl_to_be_order_result = False
            moved_tsl_order_result = False
            sl_pcts_order_result = 0.
            sl_prices_order_result = 0.
            tp_pcts_order_result = 0.
            tp_prices_order_result = 0.
            tsl_pcts_order_result = 0.
            tsl_prices_order_result = 0.

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
                        tsl_prices_order_result, \
                        = process_order_nb(
                            price=open_price[bar],

                            # Account
                            available_balance=available_balance,
                            cash_borrowed=cash_borrowed,
                            cash_used=cash_used,
                            equity=equity,
                            fee_pct=fee_pct,
                            mmr=mmr,

                            # Order
                            lev_mode=lev_mode,
                            max_equity_risk_pct=max_equity_risk_pct_order,
                            max_equity_risk_value=max_equity_risk_value_order,
                            max_lev=max_lev,
                            max_order_size_pct=max_order_size_pct,
                            max_order_size_value=max_order_size_value,
                            min_order_size_pct=min_order_size_pct,
                            min_order_size_value=min_order_size_value,
                            risk_rewards=risk_rewards_order,
                            size_pct=size_pct_order,
                            size_type=size_type,
                            slippage_pct=slippage_pct,
                            sl_pcts=sl_pcts_order,
                            sl_prices=sl_prices_order,
                            tp_pcts=tp_pcts_order,
                            tp_prices=tp_prices_order,
                            tsl_pcts=tsl_pcts_order,
                            tsl_prices=tsl_prices_order,
                            sl_be_then_trail=sl_to_be_then_trail_order,
                            sl_to_be=sl_to_be_order,
                            sl_to_be_zero_or_entry=sl_to_be_zero_or_entry_order,
                            tsl_based_on=tsl_based_on_order,

                            # Order Result
                            average_entry=average_entry,
                            leverage=leverage_order,
                            liq_price=liq_price,
                            moved_sl_to_be=moved_sl_to_be_order_result,
                            moved_tsl=moved_tsl_order_result,
                            order_type=order_type,
                            position=position,
                            size_value=size_value_order,
                            sl_pcts_order_result=sl_pcts_order_result,
                            sl_prices_order_result=sl_prices_order_result,
                            tp_pcts_order_result=tp_pcts_order_result,
                            tp_prices_order_result=tp_prices_order_result,
                            tsl_pcts_order_result=tsl_pcts_order_result,
                            tsl_prices_order_result=tsl_prices_order_result,

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
                        tsl_prices_order_result, \
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
