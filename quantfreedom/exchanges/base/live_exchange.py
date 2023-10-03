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
    candles_np = None
    candles_df = None
    
    position_size_asset = None
    in_position = None
    average_entry = None

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        symbol: str,
        timeframe: str,
        trading_in: str,
        long_or_short: LongOrShortType,
        candles_to_dl: int = None,
        keep_volume_in_candles: bool = False,
        use_test_net: bool = False,
        position_mode: PositionModeType = PositionModeType.HedgeMode,
        leverage_mode: LeverageModeType = LeverageModeType.Isolated,
    ):
        super().__init__(api_key, secret_key)

        self.timeframe_in_ms = self.get_timeframe_in_ms(timeframe)
        self.symbol = symbol
        self.candles_to_dl = candles_to_dl
        self.trading_in = trading_in.upper()
        self.position_mode = position_mode
        self.long_or_short = long_or_short

    def last_fetched_time_to_pd_datetime(self):
        return self.get_ms_time_to_pd_datetime(time_in_ms=self.last_fetched_ms_time)

    def create_long_sl_hedge_mode_order(self):
        pass

    def create_long_hedge_mode_tp_limit_order(self):
        pass

    def create_long_hedge_mode_entry_market_order(self):
        pass

    def check_if_order_filled(self):
        pass

    def set_init_last_fetched_time(self):
        pass

    def set_candles_df_and_np(self):
        pass

    def get_long_hedge_mode_position_info(self):
        pass
