import numpy as np
import pandas as pd

from quantfreedom.enums import AccountState, DynamicOrderSettings, DynamicOrderSettingsArrays, OrderResult

DIGITS_START = 48
DIGITS_END = 58
DASH = 45
DOT = 46
PLUS = 43
E_CHAR = 101


def get_to_the_upside_nb(
    gains_pct: float,
    wins_and_losses_array_no_be: np.array,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

    xm = x.mean()
    ym = y.mean()

    y_ym = y - ym
    if y_ym.all() == 0:
        y_ym = np.array([1.0])
    y_ym_s = np.power(y_ym, 2)

    x_xm = x - xm
    if x_xm.all() == 0:
        x_xm = np.array([1.0])
    x_xm_s = np.power(x_xm, 2)

    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
    b0 = ym - b1 * xm

    y_pred = b0 + b1 * x

    yp_ym = y_pred - ym

    yp_ym_s = np.power(yp_ym, 2)

    to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        to_the_upside = -(to_the_upside)
    return round(to_the_upside, 4)


def get_dos(
    dos_cart_arrays: DynamicOrderSettingsArrays,
    dos_index: int,
):
    return DynamicOrderSettings(
        entry_size_asset=dos_cart_arrays.entry_size_asset[dos_index],
        max_equity_risk_pct=dos_cart_arrays.max_equity_risk_pct[dos_index],
        max_trades=dos_cart_arrays.max_trades[dos_index],
        num_candles=dos_cart_arrays.num_candles[dos_index],
        risk_account_pct_size=dos_cart_arrays.risk_account_pct_size[dos_index],
        risk_reward=dos_cart_arrays.risk_reward[dos_index],
        sl_based_on_add_pct=dos_cart_arrays.sl_based_on_add_pct[dos_index],
        sl_based_on_lookback=dos_cart_arrays.sl_based_on_lookback[dos_index],
        sl_bcb_type=dos_cart_arrays.sl_bcb_type[dos_index],
        sl_to_be_cb_type=dos_cart_arrays.sl_to_be_cb_type[dos_index],
        sl_to_be_when_pct=dos_cart_arrays.sl_to_be_when_pct[dos_index],
        sl_to_be_ze_type=dos_cart_arrays.sl_to_be_ze_type[dos_index],
        static_leverage=dos_cart_arrays.static_leverage[dos_index],
        trail_sl_bcb_type=dos_cart_arrays.trail_sl_bcb_type[dos_index],
        trail_sl_by_pct=dos_cart_arrays.trail_sl_by_pct[dos_index],
        trail_sl_when_pct=dos_cart_arrays.trail_sl_when_pct[dos_index],
    )


def round_size_by_tick_step(
    user_num: float,
    exchange_num: float,
) -> float:
    return round(user_num, exchange_num)


def get_n_digits(x):
    l1, l2 = 0, -1
    _x = x
    while _x > 0:
        _x = _x // 10
        l1 += 1

    _x = x % 10
    while _x > 1e-10:
        _x = (_x * 10) % 10
        l2 += 1
        if l2 >= 16:
            break
    return l1, l2


def float_to_str(x: float):
    return str(x)


def min_price_getter(
    bar_index: int,
    candles: np.array,
    candle_body_type: int,
    lookback: int,
) -> float:
    price = candles[lookback : bar_index + 1 :, candle_body_type].min()
    return price


def max_price_getter(
    bar_index: int,
    candles: np.array,
    candle_body_type: int,
    lookback: int,
) -> float:
    price = candles[lookback : bar_index + 1 :, candle_body_type].max()
    return price


def long_sl_to_zero(
    average_entry,
    market_fee_pct,
    price_tick_step,
):
    sl_price = (market_fee_pct * average_entry + average_entry) / (1 - market_fee_pct)
    sl_price = round_size_by_tick_step(
        user_num=sl_price,
        exchange_num=price_tick_step,
    )
    return sl_price


def sl_to_entry(
    average_entry,
    market_fee_pct,
    price_tick_step,
):
    sl_price = average_entry
    return sl_price


def sl_to_z_e_pass(
    average_entry,
    market_fee_pct,
    price_tick_step,
):
    pass


def fill_order_records(
    account_state: AccountState,
    or_index: int,
    order_records: np.array,
    order_result: OrderResult,
):
    order_records["ind_set_idx"] = account_state.ind_set_index
    order_records["or_set_idx"] = account_state.dos_index
    order_records["bar_idx"] = account_state.bar_index
    order_records["timestamp"] = account_state.timestamp

    order_records["equity"] = account_state.equity
    order_records["available_balance"] = account_state.available_balance
    order_records["cash_borrowed"] = account_state.cash_borrowed
    order_records["cash_used"] = account_state.cash_used

    order_records["average_entry"] = order_result.average_entry
    order_records["fees_paid"] = account_state.fees_paid
    order_records["leverage"] = order_result.leverage
    order_records["liq_price"] = order_result.liq_price
    order_records["order_status"] = order_result.order_status
    order_records["possible_loss"] = account_state.possible_loss
    order_records["total_trades"] = account_state.total_trades
    order_records["entry_size_asset"] = order_result.entry_size_asset
    order_records["entry_size_usd"] = order_result.entry_size_usd
    order_records["entry_price"] = order_result.entry_price
    order_records["exit_price"] = order_result.exit_price
    order_records["position_size_asset"] = order_result.position_size_asset
    order_records["position_size_usd"] = order_result.position_size_usd
    order_records["realized_pnl"] = account_state.realized_pnl
    order_records["sl_pct"] = round(order_result.sl_pct * 100, 4)
    order_records["sl_price"] = order_result.sl_price
    order_records["tp_pct"] = round(order_result.tp_pct * 100, 4)
    order_records["tp_price"] = order_result.tp_price
    return or_index + 1


def dos_cart_product(dos_arrays: DynamicOrderSettingsArrays):
    # cart array loop
    n = 1
    for x in dos_arrays:
        n *= x.size
    out = np.empty((n, len(dos_arrays)))

    for i in range(len(dos_arrays)):
        m = int(n / dos_arrays[i].size)
        out[:n, i] = np.repeat(dos_arrays[i], m)
        n //= dos_arrays[i].size

    n = dos_arrays[-1].size
    for k in range(len(dos_arrays) - 2, -1, -1):
        n *= dos_arrays[k].size
        m = int(n / dos_arrays[k].size)
        for j in range(1, dos_arrays[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    return DynamicOrderSettingsArrays(
        entry_size_asset=out.T[0],
        max_equity_risk_pct=out.T[1] / 100,
        max_trades=out.T[2].astype(np.int_),
        num_candles=out.T[3].astype(np.int_),
        risk_account_pct_size=out.T[4] / 100,
        risk_reward=out.T[5],
        sl_based_on_add_pct=out.T[6] / 100,
        sl_based_on_lookback=out.T[7].astype(np.int_),
        sl_bcb_type=out.T[8].astype(np.int_),
        sl_to_be_cb_type=out.T[9].astype(np.int_),
        sl_to_be_when_pct=out.T[10] / 100,
        sl_to_be_ze_type=out.T[11].astype(np.int_),
        static_leverage=out.T[12],
        trail_sl_bcb_type=out.T[13].astype(np.int_),
        trail_sl_by_pct=out.T[14] / 100,
        trail_sl_when_pct=out.T[15] / 100,
    )


def order_records_to_df(order_records: np.array):
    order_records_df = pd.DataFrame(order_records)
    order_records_df.insert(4, "datetime", pd.to_datetime(order_records_df.timestamp, unit="ms"))
    order_records_df.replace(
        {
            "order_status": {
                0: "HitMaxTrades",
                1: "EntryFilled",
                2: "StopLossFilled",
                3: "TakeProfitFilled",
                4: "LiquidationFilled",
                5: "MovedSLToBE",
                6: "MovedTSL",
                7: "MaxEquityRisk",
                8: "RiskToBig",
                9: "CashUsedExceed",
                10: "EntrySizeTooSmall",
                11: "EntrySizeTooBig",
                12: "PossibleLossTooBig",
                13: "Nothing",
            }
        },
        inplace=True,
    )
    order_records_df[
        [
            "equity",
            "available_balance",
            "cash_borrowed",
            "cash_used",
            "average_entry",
            "fees_paid",
            "leverage",
            "liq_price",
            "possible_loss",
            "entry_size_asset",
            "entry_size_usd",
            "entry_price",
            "exit_price",
            "position_size_asset",
            "position_size_usd",
            "realized_pnl",
            "sl_pct",
            "sl_price",
            "tp_pct",
            "tp_price",
        ]
    ] = order_records_df[
        [
            "equity",
            "available_balance",
            "cash_borrowed",
            "cash_used",
            "average_entry",
            "fees_paid",
            "leverage",
            "liq_price",
            "possible_loss",
            "entry_size_asset",
            "entry_size_usd",
            "entry_price",
            "exit_price",
            "position_size_asset",
            "position_size_usd",
            "realized_pnl",
            "sl_pct",
            "sl_price",
            "tp_pct",
            "tp_price",
        ]
    ].replace(
        {0: np.nan}
    )
    return order_records_df


def get_data_for_plotting(order_records_df: pd.DataFrame, candles: np.array):
    data = {
        "candles": candles.tolist(),
    }
    timestamp_list = candles[:, 0].tolist()

    temp_entries_df = order_records_df[
        ["order_status", "timestamp", "average_entry", "entry_price", "liq_price", "sl_price", "tp_price"]
    ]
    entries_df = temp_entries_df[temp_entries_df["order_status"] == "EntryFilled"]
    entries_list_df = entries_df.values[:, 1:].tolist()

    entries_list = np.vstack(candles[:, 0]).tolist()
    sl_list = np.vstack(candles[:, 0]).tolist()
    tp_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == entries_list_df[0][0]:
            current_entry = entries_list_df[0]
            entries_list[idx] = [current_entry[0], current_entry[2]]
            sl_list[idx] = [current_entry[0], current_entry[4]]
            tp_list[idx] = [current_entry[0], current_entry[5]]
            del entries_list_df[0]
            if len(entries_list_df) == 0:
                break
    data["entries"] = entries_list
    data["sl_prices"] = sl_list
    data["tp_prices"] = tp_list

    temp_sl_filled_df = order_records_df[["order_status", "timestamp", "exit_price"]]
    sl_filled_df = temp_sl_filled_df[temp_sl_filled_df["order_status"] == "StopLossFilled"]
    sl_filled_list_df = sl_filled_df.values[:, 1:].tolist()
    filled_sl_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == sl_filled_list_df[0][0]:
            filled_sl_list[idx] = sl_filled_list_df[0]
            del sl_filled_list_df[0]
            if len(sl_filled_list_df) == 0:
                break
    data["sl_filled"] = filled_sl_list

    temp_tp_filled_df = order_records_df[["order_status", "timestamp", "exit_price"]]
    tp_filled_df = temp_tp_filled_df[temp_tp_filled_df["order_status"] == "TakeProfitFilled"]
    tp_filled_list_df = tp_filled_df.values[:, 1:].tolist()
    filled_tp_list = np.vstack(candles[:, 0]).tolist()

    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == tp_filled_list_df[0][0]:
            filled_tp_list[idx] = tp_filled_list_df[0]
            del tp_filled_list_df[0]
            if len(tp_filled_list_df) == 0:
                break
    data["tp_filled"] = filled_tp_list

    temp_tp_filled_df = order_records_df[["order_status", "timestamp", "sl_price"]]
    moved_sl_df = temp_tp_filled_df[
        (temp_tp_filled_df["order_status"] == "MovedTSL") | (temp_tp_filled_df["order_status"] == "MovedSLToBE")
    ]
    moved_sl_list_df = moved_sl_df.values[:, 1:].tolist()
    moved_sl_list = np.vstack(candles[:, 0]).tolist()
    for idx, timestamp in enumerate(timestamp_list):
        if timestamp == moved_sl_list_df[0][0]:
            moved_sl_list[idx] = moved_sl_list_df[0]
            del moved_sl_list_df[0]
            if len(moved_sl_list_df) == 0:
                break
    data["moved_sl"] = moved_sl_list

    return data
