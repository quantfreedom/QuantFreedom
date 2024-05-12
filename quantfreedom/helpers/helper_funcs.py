import numpy as np
import pandas as pd
from logging import getLogger
from datetime import datetime
from quantfreedom.core.enums import AccountState, FootprintCandlesTuple, OrderResult
from quantfreedom.core.strategy import Strategy
from quantfreedom.exchanges.binance_usdm import BinanceUSDM
from quantfreedom.exchanges.bybit import Bybit
from quantfreedom.exchanges.mufex import Mufex
from typing import Optional

logger = getLogger()


def all_backtest_stats(
    step_by: int,
    strategy: Strategy,
    threads: int,
    total_bars: int,
    num_chunk_bts: Optional[int] = None,
):

    # logger.infoing out total numbers of things
    print("Starting the backtest now ... and also here are some stats for your backtest." + "\n")
    print(f"Total threads to use: {threads:,}")
    print(f"Total indicator settings to test: {strategy.total_indicator_settings:,}")
    print(f"Total order settings to test: {strategy.total_order_settings:,}")
    print(f"Total settings combinations to test: {strategy.total_order_settings * strategy.total_indicator_settings:,}")
    print(f"Total settings combination to test after filtering: {strategy.total_filtered_settings:,}")
    print(
        f"Total settings combination chunks to process at the same time: {strategy.total_filtered_settings // threads:,}"
        + "\n"
    )

    print(f"Total candles: {total_bars:,}")
    total_candles = strategy.total_filtered_settings * total_bars
    print(f"Total candles to test: {total_candles:,}")
    chunks = total_candles // threads
    print(f"Total candle chunks to be processed at the same time: {chunks:,}")
    print(f"Total candle chunks with step by: {chunks // step_by:,}")

    if num_chunk_bts:
        total_settings = (num_chunk_bts * threads * step_by // total_bars) + 1
        print("\n" + f"New Total Settings: {total_settings:,}")
        new_total_candles = total_settings * total_bars
        new_chunks = new_total_candles // threads
        print(f"New total chunks with step by: {new_chunks // step_by:,}")


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
