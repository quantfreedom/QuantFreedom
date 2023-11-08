import pandas as pd
import numpy as np

from datetime import timedelta
from time import time

from requests import get

from quantfreedom.enums import ExchangeSettings

UNIVERSAL_SIDES = ["buy", "sell"]
UNIVERSAL_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"]
TIMEFRAMES_IN_MINUTES = [1, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080]


class Exchange:
    candles_list = None
    volume_yes_no_start = None
    volume_yes_no_end = None
    exchange_settings: ExchangeSettings = None

    def __init__(
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
    ):
        self.api_key = api_key
        self.secret_key = secret_key

    def create_order(self, **kwargs):
        pass

    def get_candles(self, **kwargs):
        pass

    def cancel_open_order(self, **kwargs):
        pass

    def get_filled_orders_by_order_id(self, **kwargs):
        pass

    def move_open_order(self, **kwargs):
        pass

    def get_open_order_by_order_id(self, **kwargs):
        pass

    def cancel_all_open_order_per_symbol(self, **kwargs):
        pass

    def get_wallet_info_of_asset(self, **kwargs):
        pass

    def check_if_order_filled(self, **kwargs):
        pass

    def set_leverage_value(self, **kwargs):
        pass

    def check_if_order_canceled(self, **kwargs):
        pass

    def check_if_order_open(self, **kwargs):
        pass

    def get_equity_of_asset(self, **kwargs):
        pass

    def move_stop_order(self, **kwargs):
        pass

    def get_latest_pnl_result(self, **kwargs):
        pass

    def get_closed_pnl(self, **kwargs):
        pass

    def get_current_time_sec(self):
        return int(time())

    def get_current_time_ms(self):
        return self.get_current_time_sec() * 1000

    def get_current_pd_datetime(self):
        return pd.to_datetime(self.get_current_time_sec(), unit="s")

    def get_ms_time_to_pd_datetime(self, time_in_ms):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def get_timeframe_in_ms(self, timeframe: str):
        return self.get_timeframe_in_s(timeframe=timeframe) * 1000

    def get_timeframe_in_s(self, timeframe: str):
        return int(timedelta(minutes=TIMEFRAMES_IN_MINUTES[UNIVERSAL_TIMEFRAMES.index(timeframe)]).seconds)

    def get_exchange_timeframe(self, timeframe: str, ex_timeframes: list):
        try:
            return ex_timeframes[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            raise Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")
