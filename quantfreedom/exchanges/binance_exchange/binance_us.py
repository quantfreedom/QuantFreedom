from time import sleep
import numpy as np
from requests import get
from quantfreedom.exchanges.exchange import Exchange

BINANCE_USDM_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]


class BinanceUS(Exchange):
    def __init__(self) -> None:
        pass

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = 1500,
    ):
        """
        https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data
        """
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=BINANCE_USDM_TIMEFRAMES, timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        if until_date_ms is None:
            if since_date_ms is None:
                until_date_ms = self.get_current_time_ms() - timeframe_in_ms
                since_date_ms = until_date_ms - candles_to_dl_ms
            else:
                until_date_ms = since_date_ms + candles_to_dl_ms - 5000  # 5000 is to sub 5 seconds
        else:
            if since_date_ms is None:
                since_date_ms = until_date_ms - candles_to_dl_ms
                until_date_ms -= 5000

        b_candles = []
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "startTime": since_date_ms,
            "endTime": until_date_ms,
            "limit": 1500,
        }

        while params["startTime"] + timeframe_in_ms < until_date_ms:
            try:
                b_data = get(url="https://api.binance.us/api/v3/klines", params=params).json()
                last_candle_time_ms = b_data[-1][0]
                if last_candle_time_ms == params["startTime"]:
                    sleep(0.3)
                else:
                    b_candles.extend(b_data)
                    params["startTime"] = last_candle_time_ms + 2000
            except Exception as e:
                raise Exception(f"get_busdm_candles -> {e}")
        candles_np = np.array(b_candles, dtype=np.float_)[:, :5]
        return candles_np
