from time import sleep
import numpy as np
from requests import get
from quantfreedom.exchanges.exchange import Exchange
from datetime import datetime


BINANCE_USDM_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]


class BinanceUS(Exchange):
    def __init__(self) -> None:
        pass

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 1500,
    ):
        """
        https://docs.binance.us/#get-candlestick-data
        """
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=BINANCE_USDM_TIMEFRAMES, timeframe=timeframe)
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
