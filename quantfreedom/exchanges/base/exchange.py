import pandas as pd
import numpy as np

from datetime import datetime, timedelta

UNIVERSAL_SIDES = ["buy", "sell"]
UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
TIMEFRAMES_IN_MINUTES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]


class Exchange:
    candles_list = None
    volume_yes_no_start = None
    volume_yes_no_end = None

    def __init__(self, api_key: str, secret_key: str, use_test_net: bool = False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.use_test_net = use_test_net

    def __get_current_time_seconds(self):
        return int(datetime.now().timestamp())

    def get_ms_current_time(self):
        return self.__get_current_time_seconds() * 1000

    def __get_current_pd_datetime(self):
        return pd.to_datetime(self.__get_current_time_seconds(), unit="s")

    def __get_ms_time_to_pd_datetime(self, time_in_ms):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def __get_candles_list_to_pd(self, candles_list, col_end: int):
        candles = np.array(candles_list, dtype=np.float_)[:, :col_end]
        candles_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        candles_df = candles_df.astype({"timestamp": "int64"})
        candles_df["timestamp"] = self.__get_ms_time_to_pd_datetime(candles_df["timestamp"])
        return candles_df

    def __get_candles_to_dl_in_ms(candles_to_dl: int, timeframe_in_ms):
        if candles_to_dl is not None:
            return candles_to_dl * timeframe_in_ms
        else:
            return 0

    def __get_timeframe_in_ms(self, timeframe):
        try:
            timeframe_in_ms = int(
                timedelta(minutes=TIMEFRAMES_IN_MINUTES[UNIVERSAL_TIMEFRAMES.index(timeframe)]).seconds * 1000
            )
            return timeframe_in_ms
        except TypeError as e:
            raise TypeError(f"You need to send the following {UNIVERSAL_TIMEFRAMES} -> {e}")
