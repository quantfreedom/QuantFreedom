from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np


UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
TIMEFRAMES_IN_MINUTES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]

DATETIME_PATTERN = "%m/%d/%Y %H:%M:%S"
SLEEP_RETRY = 0.2
SLEEP_NETWORKING_RETRY = 1
MAX_NETWORKING_RETRY = 20


class Exchange:
    last_fetched_time = None
    candles_list = None
    candles_df = None
 
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        api_key: str,
        secret_key: str,
        side: str,
        candles_to_dl: int = None,
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.symbol = symbol
        self.volume_yes_no = -2
        self.timeframe_in_ms = self.__get_timeframe_in_ms(timeframe)
        if candles_to_dl:
            self.candles_to_dl_in_ms = candles_to_dl * self.timeframe_in_ms
        else:
            self.candles_to_dl_in_ms = 0

    def __get_timeframe_in_ms(self, timeframe):
        try:
            timeframe_in_ms = (
                timedelta(minutes=TIMEFRAMES_IN_MINUTES[UNIVERSAL_TIMEFRAMES.index(timeframe)]).seconds * 1000
            )
            return timeframe_in_ms
        except TypeError as e:
            raise TypeError(f"You need to send the following {UNIVERSAL_TIMEFRAMES} -> {e}")

    def __get_current_time_seconds(self):
        return int(datetime.now().timestamp())

    def __get_ms_current_time(self):
        return self.__get_current_time() * 1000

    def __get_current_pd_datetime(self):
        return pd.to_datetime(self.__get_current_time(), unit="s")

    def __last_fetched_time_to_pd_datetime(self):
        return pd.to_datetime(self.last_fetched_time / 1000, unit="s")

    def __convert_to_pd_datetime(self, time_in_ms):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def __candles_list_to_pd(self):
        candles = np.array(self.candles_list, dtype=np.float_)[:, : self.volume_yes_no]
        self.candles_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        self.candles_df = self.candles_df.astype({"timestamp": "int64"})
        self.candles_df.timestamp = self.__convert_to_pd_datetime(self.candles_df.timestamp)

    def __set_init_last_fetched_time(self):
        pass

    def __get_live_trading_candles(self):
        pass

    def set_candles_df(self):
        pass
    
    def get_position_info(self):
        pass