import numpy as np
import pandas as pd
from logging import getLogger
from datetime import datetime
from quantfreedom.core.enums import AccountState, FootprintCandlesTuple, OrderResult
from quantfreedom.exchanges.binance_usdm import BinanceUSDM
from quantfreedom.exchanges.bybit import Bybit
from quantfreedom.exchanges.mufex import Mufex

logger = getLogger()


def dl_ex_candles(
    exchange: str,
    symbol: str,
    timeframe: str,
    candles_to_dl: int = None,
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
    order_records["total_possible_loss"] = account_state.total_possible_loss
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
