from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np

from quantfreedom.enums import LeverageModeType, LongOrShortType, PositionModeType
from quantfreedom.exchanges.base.exchange import Exchange


UNIVERSAL_SIDES = ["buy", "sell"]
UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
TIMEFRAMES_IN_MINUTES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]

DATETIME_PATTERN = "%m/%d/%Y %H:%M:%S"
SLEEP_RETRY = 0.2
SLEEP_NETWORKING_RETRY = 1
MAX_NETWORKING_RETRY = 20


class LiveExchange(Exchange):
    volume_yes_no = None
    candles_list = None
    last_fetched_ms_time = None

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        symbol: str,
        timeframe: str,
        long_or_short: LongOrShortType,
        candles_to_dl: int = None,
        keep_volume_in_candles: bool = False,
        use_test_net: bool = False,
        position_mode: PositionModeType = PositionModeType.HedgeMode,
        leverage_mode: LeverageModeType = LeverageModeType.Isolated,
    ):
        super().__init__(api_key, secret_key)

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

    def last_fetched_time_to_pd_datetime(self):
        return pd.to_datetime(self.last_fetched_ms_time / 1000, unit="s")

