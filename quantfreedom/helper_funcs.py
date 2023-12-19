from time import time
from typing import NamedTuple
import numpy as np
import pandas as pd
from logging import getLogger
from datetime import datetime
from quantfreedom.enums import AccountState, DynamicOrderSettings, DynamicOrderSettingsArrays, OrderResult
from quantfreedom.exchanges.apex_exchange.apex import Apex
from quantfreedom.exchanges.binance_exchange.binance_us import BinanceUS
from quantfreedom.exchanges.binance_exchange.binance_usdm import BinanceUSDM
from quantfreedom.exchanges.bybit_exchange.bybit import Bybit
from quantfreedom.exchanges.mufex_exchange.mufex import Mufex

logger = getLogger("info")


def dl_ex_candles(
    symbol: str,
    exchange: str,
    timeframe: str,
    since_datetime: datetime = None,
    until_datetime: datetime = None,
    candles_to_dl: int = None,
):
    """
    Download candles from the exchange of your choice

    Parameters
    ----------
    exchange: str
        binance us = 'binance_us' | default candles to dl is 1500

        binance futures = 'binance_usdm' | default candles to dl is 1500

        apex = 'apex' | default candles to dl is 200

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
        return BinanceUSDM(use_test_net=False).get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1500 if candles_to_dl is None else candles_to_dl,
        )
    elif exchange.lower() == "binance_us":
        return BinanceUS().get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1500 if candles_to_dl is None else candles_to_dl,
        )
    elif exchange.lower() == "apex":
        return Apex(use_test_net=False).get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=200 if candles_to_dl is None else candles_to_dl,
        )
    elif exchange.lower() == "mufex":
        return Mufex(use_test_net=False).get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1500 if candles_to_dl is None else candles_to_dl,
        )
    elif exchange.lower() == "bybit":
        return Bybit(use_test_net=False).get_candles(
            symbol=symbol,
            timeframe=timeframe,
            since_datetime=since_datetime,
            until_datetime=until_datetime,
            candles_to_dl=1000 if candles_to_dl is None else candles_to_dl,
        )
    else:
        raise Exception("You need to pick an exchange from this list apex, binance_usdm, mufex")


def candles_to_df(
    candles: np.array,
) -> pd.DataFrame:
    """
    Converts your numpy array candles to a pandas dataframe

    Parameters
    ----------
    candles : np.array
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
    wins_and_losses_array_no_be: np.array,
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


def get_dos(
    dos_cart_arrays: DynamicOrderSettingsArrays,
    dos_index: int,
):
    return DynamicOrderSettings(
        max_equity_risk_pct=dos_cart_arrays.max_equity_risk_pct[dos_index],
        max_trades=dos_cart_arrays.max_trades[dos_index],
        risk_account_pct_size=dos_cart_arrays.risk_account_pct_size[dos_index],
        risk_reward=dos_cart_arrays.risk_reward[dos_index],
        sl_based_on_add_pct=dos_cart_arrays.sl_based_on_add_pct[dos_index],
        sl_based_on_lookback=dos_cart_arrays.sl_based_on_lookback[dos_index],
        sl_bcb_type=dos_cart_arrays.sl_bcb_type[dos_index],
        sl_to_be_cb_type=dos_cart_arrays.sl_to_be_cb_type[dos_index],
        sl_to_be_when_pct=dos_cart_arrays.sl_to_be_when_pct[dos_index],
        trail_sl_bcb_type=dos_cart_arrays.trail_sl_bcb_type[dos_index],
        trail_sl_by_pct=dos_cart_arrays.trail_sl_by_pct[dos_index],
        trail_sl_when_pct=dos_cart_arrays.trail_sl_when_pct[dos_index],
    )


def cart_product(
    named_tuple: NamedTuple,
) -> np.array:
    n = 1
    for x in named_tuple:
        n *= x.size
    out = np.empty((n, len(named_tuple)))

    for i in range(len(named_tuple)):
        m = int(n / named_tuple[i].size)
        out[:n, i] = np.repeat(named_tuple[i], m)
        n //= named_tuple[i].size

    n = named_tuple[-1].size
    for k in range(len(named_tuple) - 2, -1, -1):
        n *= named_tuple[k].size
        m = int(n / named_tuple[k].size)
        for j in range(1, named_tuple[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]
    return out.T


def dos_cart_product(
    dos_arrays: DynamicOrderSettingsArrays,
) -> DynamicOrderSettingsArrays:
    cart_arrays = cart_product(named_tuple=dos_arrays)
    return DynamicOrderSettingsArrays(
        max_equity_risk_pct=cart_arrays[0] / 100,
        max_trades=cart_arrays[1].astype(np.int_),
        risk_account_pct_size=cart_arrays[2] / 100,
        risk_reward=cart_arrays[3],
        sl_based_on_add_pct=cart_arrays[4] / 100,
        sl_based_on_lookback=cart_arrays[5].astype(np.int_),
        sl_bcb_type=cart_arrays[6].astype(np.int_),
        sl_to_be_cb_type=cart_arrays[7].astype(np.int_),
        sl_to_be_when_pct=cart_arrays[8] / 100,
        trail_sl_bcb_type=cart_arrays[9].astype(np.int_),
        trail_sl_by_pct=cart_arrays[10] / 100,
        trail_sl_when_pct=cart_arrays[11] / 100,
    )


def round_size_by_tick_step(
    user_num: float,
    exchange_num: float,
) -> float:
    return round(user_num, exchange_num)


def fill_order_records(
    account_state: AccountState,
    or_index: int,
    order_records: np.array,
    order_result: OrderResult,
) -> int:
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
    order_records["sl_pct"] = round(order_result.sl_pct * 100, 3)
    order_records["sl_price"] = order_result.sl_price
    order_records["tp_pct"] = round(order_result.tp_pct * 100, 3)
    order_records["tp_price"] = order_result.tp_price
    return or_index + 1


def log_dynamic_order_settings(
    dos_index: int,
    dynamic_order_settings: DynamicOrderSettingsArrays,
):
    logger.info(
        f"Dynamic Order settings index= {dos_index}\
        \nmax_equity_risk_pct={round(dynamic_order_settings.max_equity_risk_pct * 100, 3)}\
        \nmax_trades={dynamic_order_settings.max_trades}\
        \nrisk_account_pct_size={round(dynamic_order_settings.risk_account_pct_size * 100, 3)}\
        \nrisk_reward={dynamic_order_settings.risk_reward}\
        \nsl_based_on_add_pct={round(dynamic_order_settings.sl_based_on_add_pct * 100, 3)}\
        \nsl_based_on_lookback={dynamic_order_settings.sl_based_on_lookback}\
        \nsl_bcb_type={dynamic_order_settings.sl_bcb_type}\
        \nsl_to_be_cb_type={dynamic_order_settings.sl_to_be_cb_type}\
        \nsl_to_be_when_pct={round(dynamic_order_settings.sl_to_be_when_pct * 100, 3)}\
        \ntrail_sl_bcb_type={dynamic_order_settings.trail_sl_bcb_type}\
        \ntrail_sl_by_pct={round(dynamic_order_settings.trail_sl_by_pct * 100, 3)}\
        \ntrail_sl_when_pct={round(dynamic_order_settings.trail_sl_when_pct * 100, 3)}"
    )
