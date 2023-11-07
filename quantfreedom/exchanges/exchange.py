import pandas as pd
import numpy as np

from datetime import datetime, timedelta

from requests import get

from quantfreedom.enums import ExchangeSettings

UNIVERSAL_SIDES = ["buy", "sell"]

class Exchange:
    candles_list = None
    volume_yes_no_start = None
    volume_yes_no_end = None
    exchange_settings: ExchangeSettings = None

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        use_test_net: bool,
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

    def get_current_time_seconds(self):
        return int(datetime.now().timestamp())

    def get_current_time_ms(self):
        return self.get_current_time_seconds() * 1000

    def get_current_pd_datetime(self):
        return pd.to_datetime(self.get_current_time_seconds(), unit="s")

    def get_ms_time_to_pd_datetime(self, time_in_ms):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def turn_candles_list_to_pd(self, candles_np):
        candles_df = pd.DataFrame(candles_np)
        candles_df["datetime"] = self.get_ms_time_to_pd_datetime(candles_df["timestamp"])
        candles_df.set_index("datetime", inplace=True)
        return candles_df

    def get_candles_to_dl_in_ms(self, candles_to_dl: int, timeframe_in_ms, limit: int):
        if candles_to_dl is not None:
            return candles_to_dl * timeframe_in_ms
        else:
            return timeframe_in_ms * limit
