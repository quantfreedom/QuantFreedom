import json
import pandas as pd

from datetime import timedelta
from time import time
from datetime import datetime, timezone

from quantfreedom.enums import ExchangeSettings

UNIVERSAL_SIDES = ["buy", "sell"]
UNIVERSAL_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"]
TIMEFRAMES_IN_MINUTES = [1, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080]


class Exchange:
    candles_list = None
    volume_yes_no_start = None
    volume_yes_no_end = None
    position_mode = None
    exchange_settings: ExchangeSettings = None
    timeframe_in_ms = None
    last_fetched_ms_time = None

    def __init__(
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
    ):
        self.api_key = api_key
        self.secret_key = secret_key

    def sort_dict(self, data: dict):
        sorted_data = dict(sorted(data.items()))
        return sorted_data

    def sort_list_of_dicts(self, data_list: list):
        new_list = []
        for element in data_list:
            new_list.append(dict(sorted(element.items())))
        return new_list

    def get_current_time_sec(self):
        return int(time())

    def get_current_time_ms(self):
        return self.get_current_time_sec() * 1000

    def get_current_pd_datetime(self):
        return pd.to_datetime(self.get_current_time_sec(), unit="s")

    def get_ms_time_to_pd_datetime(
        self,
        time_in_ms: int,
    ):
        return pd.to_datetime(time_in_ms / 1000, unit="s")

    def get_timeframe_in_ms(
        self,
        timeframe: str,
    ):
        return self.get_timeframe_in_s(timeframe=timeframe) * 1000

    def get_timeframe_in_s(
        self,
        timeframe: str,
    ):
        total_mins = TIMEFRAMES_IN_MINUTES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        time_delta_mins = timedelta(minutes=total_mins)
        total_seconds = int(time_delta_mins.total_seconds())
        return total_seconds

    def remove_none_from_dict(
        self,
        params: dict,
    ):
        new_params = {k: v for k, v in params.items() if v is not None}
        return new_params

    def get_params_as_dict_string(
        self,
        params: dict,
    ):
        new_params = self.remove_none_from_dict(params=params)
        dict_string = str(json.dumps(new_params))
        return dict_string

    def get_params_as_path(
        self,
        params: dict,
    ):
        params_as_path = "&".join("{key}={value}".format(key=k, value=v) for k, v in params.items() if v is not None)
        return params_as_path

    def get_since_until_timestamp(
        self,
        candles_to_dl_ms: int,
        since_datetime: datetime,
        timeframe_in_ms: int,
        until_datetime: datetime,
    ) -> tuple[int, int]:
        if until_datetime is None:
            if since_datetime is None:
                until_timestamp = self.get_current_time_ms() - timeframe_in_ms
                since_timestamp = until_timestamp - candles_to_dl_ms
            else:
                since_timestamp = int(since_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
                until_timestamp = since_timestamp + candles_to_dl_ms - 5000  # 5000 is to sub 5 seconds
        else:
            until_timestamp = int(until_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
            if since_datetime is None:
                since_timestamp = until_timestamp - candles_to_dl_ms
            else:
                since_timestamp = int(since_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
            until_timestamp -= 5000
        return since_timestamp, until_timestamp

    def last_fetched_time_to_pd_datetime(self):
        return self.get_ms_time_to_pd_datetime(time_in_ms=self.last_fetched_ms_time)

    def int_value_of_step_size(
        self,
        step_size: str,
    ):
        if "." not in step_size:
            return int(step_size)
        else:
            return step_size.index("1") - step_size.index(".")

    def create_order(self, **kwargs):
        pass

    def get_candles(self, **kwargs):
        pass

    def cancel_open_order(self, **kwargs):
        pass

    def get_filled_order_by_order_id(self, **kwargs):
        pass

    def move_open_order(self, **kwargs):
        pass

    def get_open_order_by_order_id(self, **kwargs):
        pass

    def cancel_all_open_orders_per_symbol(self, **kwargs):
        pass

    def get_wallet_info_of_asset(self, **kwargs):
        pass

    def check_if_order_filled(self, **kwargs):
        pass

    def set_leverage(self, **kwargs):
        pass

    def check_if_order_canceled(self, **kwargs):
        pass

    def check_if_order_open(self, **kwargs):
        pass

    def move_stop_order(self, **kwargs):
        pass

    def get_latest_pnl_result(self, **kwargs):
        pass

    def get_closed_pnl(self, **kwargs):
        pass

    def create_long_hedge_mode_sl_order(self, **kwargs):
        pass

    def get_long_hedge_mode_position_info(self, **kwargs):
        pass

    def create_long_hedge_mode_entry_market_order(self, **kwargs):
        pass

    def create_long_hedge_mode_tp_limit_order(self, **kwargs):
        pass

    def set_init_last_fetched_time(self, **kwargs):
        pass

    def get_exchange_timeframe(self, **kwargs):
        pass

    def set_exchange_settings(self, **kwargs):
        pass

    def get_no_fees_balance_of_asset_market_in_only(self, **kwargs):
        pass

    def create_long_hedge_mode_entry_market_order_stoploss(self, **kwargs):
        pass
