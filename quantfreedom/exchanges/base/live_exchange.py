from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np

from quantfreedom.enums import LeverageModeType, LongOrShortType, PositionModeType
from quantfreedom.exchanges.base.exchange import Exchange

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



