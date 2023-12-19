from datetime import datetime, timedelta
from logging import getLogger
import pandas as pd
import numpy as np

from quantfreedom.enums import LeverageModeType, LongOrShortType, PositionModeType
from quantfreedom.exchanges.exchange import Exchange

DATETIME_PATTERN = "%m/%d/%Y %H:%M:%S"
SLEEP_RETRY = 0.2
SLEEP_NETWORKING_RETRY = 1
MAX_NETWORKING_RETRY = 20


class LiveExchange(Exchange):
    volume_yes_no = None
    candles_list = None
    last_fetched_ms_time = None
    candles_np = None
    timeframe = None

    def __init__(
        self,
        api_key: str,
        candles_to_dl: int,
        leverage_mode: LeverageModeType,
        position_mode: PositionModeType,
        secret_key: str,
        symbol: str,
        timeframe: str,
        trading_with: str,
        use_test_net: bool,
    ):
        super().__init__(api_key, secret_key, use_test_net)

        self.symbol = symbol
        self.candles_to_dl = candles_to_dl
        self.trading_with = trading_with
        self.timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)

    

    def create_long_hedge_mode_sl_order(self, **kwargs):
        pass

    def create_long_hedge_mode_tp_limit_order(self, **kwargs):
        pass

    def create_long_hedge_mode_entry_market_order(self, **kwargs):
        pass

    def set_init_last_fetched_time(self, **kwargs):
        pass

    def get_long_hedge_mode_position_info(self, **kwargs):
        pass
