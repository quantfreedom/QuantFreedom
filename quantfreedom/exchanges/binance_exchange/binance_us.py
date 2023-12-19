from time import sleep
import numpy as np
from requests import get
from quantfreedom.exchanges.binance_exchange.binance_usdm import BINANCE_USDM_TIMEFRAMES
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange
from datetime import datetime


class BinanceUS(Exchange):
    def __init__(self) -> None:
        pass

    def get_exchange_timeframe(
        self,
        timeframe: str,
    ):
        try:
            return BINANCE_USDM_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            raise Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 1500,
    ):
        """
        Summary
        -------
        [Biance US candle docs](https://docs.binance.us/#get-candlestick-data)

        Explainer Video
        ---------------
        Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

        Parameters
        ----------
        symbol : str
            [Use Binance US API for symbol list](https://docs.binance.us/#introduction)
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
        ex_timeframe = self.get_exchange_timeframe(timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        since_timestamp, until_timestamp = self.get_since_until_timestamp(
            candles_to_dl_ms=candles_to_dl_ms,
            since_datetime=since_datetime,
            timeframe_in_ms=timeframe_in_ms,
            until_datetime=until_datetime,
        )

        b_candles = []
        params = {
            "symbol": symbol,
            "interval": ex_timeframe,
            "startTime": since_timestamp,
            "endTime": until_timestamp,
            "limit": 1500,
        }

        while params["startTime"] + timeframe_in_ms < until_timestamp:
            try:
                b_data = get(url="https://api.binance.us/api/v3/klines", params=params).json()
                last_candle_timestamp = b_data[-1][0]
                if last_candle_timestamp == params["startTime"]:
                    sleep(0.3)
                else:
                    b_candles.extend(b_data)
                    params["startTime"] = last_candle_timestamp + 2000
            except Exception as e:
                raise Exception(f"get_candles -> {e}")
        candles_np = np.array(b_candles, dtype=np.float_)[:, :6]
        return candles_np
