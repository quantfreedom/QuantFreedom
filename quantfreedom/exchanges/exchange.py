from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np

from quantfreedom.enums import LeverageModeType, LongOrShortType, PositionModeType


UNIVERSAL_SIDES = ["buy", "sell"]
UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
TIMEFRAMES_IN_MINUTES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]

DATETIME_PATTERN = "%m/%d/%Y %H:%M:%S"
SLEEP_RETRY = 0.2
SLEEP_NETWORKING_RETRY = 1
MAX_NETWORKING_RETRY = 20


class Exchange:
    last_fetched_ms_time = None
    candles_list = None
    candles_df = None
    symbol = None
    timeframe = None
    api_key = None
    secret_key = None
    long_or_short = None
    candles_to_dl = None
    keep_volume_in_candles = None
    use_test_net = None
    position_mode = None
    leverage_mode = None

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        api_key: str,
        secret_key: str,
        long_or_short: LongOrShortType,
        candles_to_dl: int = None,
        keep_volume_in_candles: bool = False,
        use_test_net: bool = False,
        position_mode: PositionModeType = PositionModeType.HedgeMode,
        leverage_mode: LeverageModeType = LeverageModeType.Isolated,
    ):
        self.timeframe_in_ms = self.__get_timeframe_in_ms(timeframe)
        self.api_key = api_key
        self.secret_key = secret_key
        self.symbol = symbol
        self.long_or_short = long_or_short
        self.keep_volume_in_candles = keep_volume_in_candles
        self.use_test_net = use_test_net
        self.position_mode = position_mode
        self.leverage_mode = leverage_mode

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
        return self.__get_current_time_seconds() * 1000

    def __get_current_pd_datetime(self):
        return pd.to_datetime(self.__get_current_time_seconds(), unit="s")

    def __last_fetched_time_to_pd_datetime(self):
        return pd.to_datetime(self.last_fetched_ms_time / 1000, unit="s")

    def __convert_to_pd_datetime(self, time_in_ms):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def __candles_list_to_pd(self):
        candles = np.array(self.candles_list, dtype=np.float_)[:, : self.volume_yes_no]
        self.candles_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        self.candles_df = self.candles_df.astype({"timestamp": "int64"})
        self.candles_df["timestamp"] = self.__convert_to_pd_datetime(self.candles_df["timestamp"])

    def get_and_set_candles_df(self, **vargs):
        pass

    def get_position_info(self, **vargs):
        pass

    def create_long_entry_market_order(self, **vargs):
        pass

    def create_long_entry_limit_order(self, **vargs):
        pass

    def create_long_tp_limit_order(self, **vargs):
        pass

    def create_long_tp_market_order(self, **vargs):
        pass

    def create_long_sl_order(self, **vargs):
        pass
