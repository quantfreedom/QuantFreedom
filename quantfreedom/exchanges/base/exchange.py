import pandas as pd
import numpy as np

from datetime import datetime


class Exchange:
    candles_list = None
    volume_yes_no_start = None
    volume_yes_no_end = None

    def __init__(
        self,
        api_key: str,
        secret_key: str,
    ):
        self.api_key = api_key
        self.secret_key = secret_key

    def __get_current_time_seconds(self):
        return int(datetime.now().timestamp())

    def get_ms_current_time(self):
        return self.__get_current_time_seconds() * 1000

    def __get_current_pd_datetime(self):
        return pd.to_datetime(self.__get_current_time_seconds(), unit="s")

    def __convert_to_pd_datetime(self, time_in_ms):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def __candles_list_to_pd(self):
        candles = np.array(self.candles_list, dtype=np.float_)[:, self.volume_yes_no_start : self.volume_yes_no_end]
        self.candles_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        self.candles_df = self.candles_df.astype({"timestamp": "int64"})
        self.candles_df["timestamp"] = self.__convert_to_pd_datetime(self.candles_df["timestamp"])
