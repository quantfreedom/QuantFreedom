import numpy as np
import pandas as pd
from logging import getLogger
from datetime import datetime
from quantfreedom.core.enums import CandleBodyType, FootprintCandlesTuple
from quantfreedom.core.strategy import Strategy
from quantfreedom.exchanges.binance_usdm import BinanceUSDM
from quantfreedom.exchanges.bybit import Bybit
from quantfreedom.exchanges.mufex import Mufex
from typing import List, Optional, Union

logger = getLogger()


def all_backtest_stats(
    candles: FootprintCandlesTuple,
    strategy: Strategy,
    threads: int,
    num_chunk_bts: Optional[int] = None,
    step_by: int = 1,
):
    # Creating Settings Vars
    total_bars = candles.candle_open_timestamps.size
    step_by_settings = strategy.total_filtered_settings // step_by
    chunk_process = step_by_settings // threads

    print("Starting the backtest now ... and also here are some stats for your backtest.")

    print("\n" + f"Total threads to use: {threads:,}")
    print(f"Total indicator settings to test: {strategy.total_indicator_settings:,}")
    print(f"Total order settings to test: {strategy.total_order_settings:,}")
    print(f"Total settings combinations to test: {strategy.total_order_settings * strategy.total_indicator_settings:,}")
    print(f"Total settings combination to test after filtering: {strategy.total_filtered_settings:,}")
    print(f"Total settings combination with step by: {step_by_settings:,}")
    print(f"Total settings combination to process per chunk: {chunk_process:,}")

    total_candles = strategy.total_filtered_settings * total_bars
    chunks = total_candles // threads
    candle_chunks = chunks // step_by
    print("\n" + f"Total candles: {total_bars:,}")
    print(f"Total candles to test: {total_candles:,}")
    print(f"Total candle chunks to be processed at the same time: {chunks:,}")
    print(f"Total candle chunks with step by: {candle_chunks:,}")

    if num_chunk_bts:
        new_step_by = step_by = total_candles // num_chunk_bts // threads
        if new_step_by < 1:
            print("\n" + f"Step by set to 1. Num_chunk_bts > candle chunks you would get with step by set to 1")
            step_by = 1
        else:
            new_candle_chunks = chunks // new_step_by
            new_step_by_settings = strategy.total_filtered_settings // new_step_by
            print("\n" + f"New step by: {new_step_by:,}")
            print(f"Total settings combination with new step by: {new_step_by_settings:,}")
            print(f"Total candle chunks with new step by: {new_candle_chunks:,}")
            step_by = new_step_by


def dl_ex_candles(
    exchange: str,
    symbol: str,
    timeframe: str,
    candles_to_dl: Optional[int] = None,
    since_datetime: datetime = None,
    until_datetime: datetime = None,
) -> FootprintCandlesTuple:
    """
    Download candles from the exchange of your choice

    Parameters
    ----------
    exchange: str
        binance futures = 'binance_usdm' | default candles to dl is 1500

        mufex = 'mufex' | default candles to dl is 1500

        bybit = 'bybit' | default candles to dl is 1000
    symbol : str
        Check the api of the exchange or get all the symbols of the exchange to see which ones you need to put here
    timeframe : str
            "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"
    since_datetime : datetime
        The start date, in datetime format, of candles you want to download. EX: datetime(year, month, day, hour, minute)
    until_datetime : datetime
        The until date, in datetime format, of candles you want to download minus one candle so if you are on the 5 min if you say your until date is 1200 your last candle will be 1155. EX: datetime(year, month, day, hour, minute)
    candles_to_dl : int
        The amount of candles you want to download

    Returns
    -------
    np.array
        a 2 dim array with the following columns "timestamp", "open", "high", "low", "close", "volume"
    """
    if exchange.lower() == "binance_usdm":
        return BinanceUSDM().get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1500 if candles_to_dl is None else candles_to_dl,
        )
    elif exchange.lower() == "mufex":
        return Mufex(use_testnet=False).get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1500 if candles_to_dl is None else candles_to_dl,
        )
    elif exchange.lower() == "bybit":
        return Bybit(use_testnet=False).get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1000 if candles_to_dl is None else candles_to_dl,
        )
    else:
        raise Exception("You need to pick an exchange from this list binance_usdm, mufex, bybit")


def candles_to_df(
    candles: FootprintCandlesTuple,
) -> pd.DataFrame:
    """
    Converts your numpy array candles to a pandas dataframe

    Parameters
    ----------
    candles : np.ndarray
        a 2 dim array with the following columns "timestamp", "open", "high", "low", "close", "volume"

    Returns
    -------
    pd.DataFrame
        columns "timestamp", "open", "high", "low", "close", "volume" with an index of pandas datetimes
    """
    candles_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    candles_df["timestamp"] = candles_df["timestamp"].astype(dtype=np.int64)
    candles_df.set_index(pd.to_datetime(candles_df["timestamp"], unit="ms"), inplace=True)
    candles_df.index.rename("datetime", inplace=True)
    return candles_df


def get_qf_score(
    gains_pct: float,
    wins_and_losses_array_no_be: np.ndarray,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

    xm = x.mean()
    ym = y.mean()

    y_ym = y - ym
    if (y_ym == 0).all():
        y_ym = np.array([1.0])
    y_ym_s = np.power(y_ym, 2)

    x_xm = x - xm
    if (x_xm == 0).all():
        x_xm = np.array([1.0])
    x_xm_s = np.power(x_xm, 2)

    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
    b0 = ym - b1 * xm

    y_pred = b0 + b1 * x

    yp_ym = y_pred - ym

    yp_ym_s = np.power(yp_ym, 2)

    qf_score = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        qf_score = -(qf_score)
    return round(qf_score, 3)


def round_size_by_tick_step(
    user_num: float,
    exchange_num: float,
) -> float:
    return round(user_num, exchange_num)


def order_records_to_df(
    order_records: np.ndarray,
):
    order_records_df = pd.DataFrame(order_records)
    order_records_df.insert(4, "datetime", pd.to_datetime(order_records_df["timestamp"], unit="ms"))
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
            "total_possible_loss",
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
            "total_possible_loss",
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


def make_bt_df(
    strategy: Strategy,
    strategy_result_records: np.ndarray,
):
    def cbt_to_field(x):
        field_name = CandleBodyType._fields[int(x)]
        return field_name

    def rounder(x):
        rounded = round(x * 100, 2)
        return rounded

    column_names = (
        [
            "total_trades",
            "wins",
            "losses",
            "gains_pct",
            "win_rate",
            "qf_score",
            "fees_paid",
            "total_pnl",
            "ending_eq",
        ]
        + list(strategy.og_dos_tuple._fields)
        + list(strategy.og_ind_set_tuple._fields)
    )
    backtest_df = pd.DataFrame(data=strategy_result_records, columns=column_names).dropna()
    backtest_df.set_index(backtest_df["settings_index"].values.astype(np.int_), inplace=True)

    backtest_df["sl_bcb_type"] = backtest_df["sl_bcb_type"].apply(cbt_to_field)
    backtest_df["trail_sl_bcb_type"] = backtest_df["trail_sl_bcb_type"].apply(cbt_to_field)
    backtest_df["sl_to_be_cb_type"] = backtest_df["sl_to_be_cb_type"].apply(cbt_to_field)

    backtest_df["account_pct_risk_per_trade"] = backtest_df["account_pct_risk_per_trade"].apply(rounder)
    backtest_df["sl_based_on_add_pct"] = backtest_df["sl_based_on_add_pct"].apply(rounder)
    backtest_df["sl_to_be_when_pct"] = backtest_df["sl_to_be_when_pct"].apply(rounder)
    backtest_df["trail_sl_by_pct"] = backtest_df["trail_sl_by_pct"].apply(rounder)
    backtest_df["trail_sl_when_pct"] = backtest_df["trail_sl_when_pct"].apply(rounder)

    backtest_df.sort_values("gains_pct", ascending=False, inplace=True)

    return backtest_df


def symbol_bt_df(
    backtest_df: pd.DataFrame,
):

    def dollar_sign(x):
        result = "${:,.2f}".format(x)
        return result

    def pct_sign(x):
        result = "{:,.2f}%".format(x)
        return result

    backtest_df["fees_paid"] = backtest_df["fees_paid"].apply(dollar_sign)
    backtest_df["total_pnl"] = backtest_df["total_pnl"].apply(dollar_sign)
    backtest_df["ending_eq"] = backtest_df["ending_eq"].apply(dollar_sign)

    backtest_df["gains_pct"] = backtest_df["gains_pct"].apply(pct_sign)
    backtest_df["win_rate"] = backtest_df["win_rate"].apply(pct_sign)

    return backtest_df


def np_shift_fwd(
    arr: np.ndarray,
    fill_value: Union[float, int, bool, str],
    shift: int = 1,
) -> np.ndarray:

    result = np.empty_like(arr)

    result[:shift] = fill_value
    result[shift:] = arr[:-shift]

    return result


def np_shift_bwd(
    arr: np.ndarray,
    fill_value: Union[float, int, bool, str],
    shift: int = -1,
) -> np.ndarray:

    result = np.empty_like(arr)

    result[shift:] = fill_value
    result[:shift] = arr[-shift:]

    return result


def np_lookback_one(
    arr: np.ndarray,
    lookback: int,
    include_current: bool,
    fill_value: Union[float, int, bool, str],
    fwd_bwd: str,
) -> tuple[np.ndarray, np.ndarray]:
    """
    _summary_

    [Video]()

    Parameters
    ----------
    arr : np.ndarray
        _description_
    lookback : int
        _description_
    include_current : bool
        _description_
    fill_value : float, int, bool, str]
        _description_
    fwd_bwd : str
        fwd for forward and bwd for backward

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        _description_
    """

    def np_shift(
        arr: np.ndarray,
        fill_value: Union[float, int, bool, str],
        shift: int = 1,
    ) -> np.ndarray:
        pass

    if fwd_bwd.lower() == "fwd":
        np_shift = np_shift_fwd
    elif fwd_bwd.lower() == "bwd":
        np_shift = np_shift_bwd
    else:
        raise Exception("fwd_bwd must be either 'fwd' or 'bwd'")

    prev_arr = np.empty((arr.size, lookback), dtype=arr.dtype)

    if include_current:
        lookback += 1
        prev_arr = np.empty((arr.size, lookback), dtype=arr.dtype)
        prev_arr[:, 0] = arr

    else:

        prev_arr = np.empty((arr.size, lookback), dtype=arr.dtype)
        prev_arr[:, 0] = np_shift(arr, fill_value=fill_value)

    for idx in range(1, lookback):
        prev_arr[:, idx] = np_shift(prev_arr[:, idx - 1], fill_value=fill_value)

    return prev_arr


def np_lookback_two(
    arr_1: np.ndarray,
    arr_2: np.ndarray,
    lookback: int,
    include_current: bool,
    fill_value: Union[float, int, bool, str],
    fwd_bwd: str = "fwd",
) -> tuple[np.ndarray, np.ndarray]:
    """
    _summary_

    [Video]()

    Parameters
    ----------
    arr_1 : np.ndarray
        _description_
    arr_2 : np.ndarray
        _description_
    lookback : int
        _description_
    include_current : bool
        _description_
    fill_value : float, int, bool, str]
        _description_
    fwd_bwd : str
        fwd for forward and bwd for backward

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        _description_
    """

    def np_shift(
        arr: np.ndarray,
        fill_value: Union[float, int, bool, str],
        shift: int = 1,
    ) -> np.ndarray:
        pass

    if fwd_bwd.lower() == "fwd":
        np_shift = np_shift_fwd
    elif fwd_bwd.lower() == "bwd":
        np_shift = np_shift_bwd
    else:
        raise Exception("fwd_bwd must be either 'fwd' or 'bwd'")

    if include_current:
        lookback += 1

        prev_arr_1 = np.empty((arr_1.size, lookback), dtype=arr_1.dtype)
        prev_arr_2 = np.empty((arr_2.size, lookback), dtype=arr_2.dtype)

        prev_arr_1[:, 0] = arr_1
        prev_arr_2[:, 0] = arr_2
    else:

        prev_arr_1 = np.empty((arr_1.size, lookback), dtype=arr_1.dtype)
        prev_arr_2 = np.empty((arr_2.size, lookback), dtype=arr_2.dtype)

        prev_arr_1[:, 0] = np_shift(arr_1, fill_value=fill_value)
        prev_arr_2[:, 0] = np_shift(arr_2, fill_value=fill_value)

    for idx in range(1, lookback):
        prev_arr_1[:, idx] = np_shift(prev_arr_1[:, idx - 1], fill_value=fill_value)
        prev_arr_2[:, idx] = np_shift(prev_arr_2[:, idx - 1], fill_value=fill_value)

    return prev_arr_1, prev_arr_2
