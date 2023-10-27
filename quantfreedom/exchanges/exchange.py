from decimal import Decimal
import json
import pandas as pd
import numpy as np

from datetime import datetime, timedelta

from requests import get

from quantfreedom.enums import ExchangeSettings
from quantfreedom.exchanges.binance_exchange.binance_futures import BINANCE_FUTURES_TIMEFRAMES

UNIVERSAL_SIDES = ["buy", "sell"]
UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
TIMEFRAMES_IN_MINUTES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]


class Exchange:
    candles_list = None
    volume_yes_no_start = None
    volume_yes_no_end = None
    exchange_settings: ExchangeSettings = None

    def __init__(
        self,
        api_key: str = None,
        secret_key: str = None,
        use_test_net: bool = None,
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.use_test_net = use_test_net

    def get_candles(self, **vargs):
        pass

    def cancel_open_order(self, *vargs):
        pass

    def get_filled_orders_by_order_id(self, *vargs):
        pass

    def move_open_order(self, *vargs):
        pass

    def get_open_order_by_order_id(self, *vargs):
        pass

    def cancel_all_open_order_per_symbol(self, *vargs):
        pass

    def get_wallet_info_of_asset(self, *vargs):
        pass

    def check_if_order_filled(self, *vargs):
        pass

    def set_leverage_value(self, *vargs):
        pass

    def check_if_order_canceled(self, *vargs):
        pass

    def check_if_order_open(self, *vargs):
        pass

    def get_equity_of_asset(self, *vargs):
        pass

    def move_stop_order(self, *vargs):
        pass

    def get_latest_pnl_result(self, *vargs):
        pass

    def get_closed_pnl(self, *vargs):
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

    def get_timeframe_in_ms(self, timeframe):
        timeframe_in_ms = int(
            timedelta(minutes=TIMEFRAMES_IN_MINUTES[UNIVERSAL_TIMEFRAMES.index(timeframe)]).seconds * 1000
        )
        return timeframe_in_ms

    def get_exchange_timeframe(self, ex_timeframe, timeframe):
        try:
            timeframe = ex_timeframe[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")
        return timeframe

    def get_params_as_string(self, params):
        params_as_string = str(json.dumps(params))
        return params_as_string

    def get_params_as_path(self, params):
        entries = params.items()
        if not entries:
            pass

        paramsString = "&".join("{key}={value}".format(key=x[0], value=x[1]) for x in entries if x[1] is not None)
        if paramsString:
            return paramsString

    def get_binance_futures_candles(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = None,
        limit: int = 1500,
    ):
        """
        https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data

        timeframe: "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"

        Response is
        [
        [
            1499040000000,      // Open time
            "0.01634790",       // Open
            "0.80000000",       // High
            "0.01575800",       // Low
            "0.01577100",       // Close
            "148976.11427815",  // Volume
            1499644799999,      // Close time
            "2434.19055334",    // Quote asset volume
            308,                // Number of trades
            "1756.87402397",    // Taker buy base asset volume
            "28.46694368",      // Taker buy quote asset volume
            "17928899.62484339" // Ignore.
        ]
        ]
            but i remove everything after the close
            use link to see all Request Parameters
        """
        param_timeframe = self.get_exchange_timeframe(ex_timeframe=BINANCE_FUTURES_TIMEFRAMES, timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = self.get_candles_to_dl_in_ms(candles_to_dl, timeframe_in_ms=timeframe_in_ms, limit=limit)

        if until_date_ms is None:
            if since_date_ms is None:
                until_date_ms = self.get_current_time_ms() - timeframe_in_ms
                since_date_ms = until_date_ms - candles_to_dl_ms
            else:
                until_date_ms = since_date_ms + candles_to_dl_ms - 5000  # 5000 is to add 5 seconds
        else:
            if since_date_ms is None:
                since_date_ms = until_date_ms - candles_to_dl_ms - 5000  # 5000 is to sub 5 seconds

        candles_list = []
        params = {
            "symbol": symbol,
            "interval": param_timeframe,
            "startTime": since_date_ms,
            "endTime": until_date_ms,
            "limit": limit,
        }

        start_time = self.get_current_time_seconds()
        while params["startTime"] + timeframe_in_ms < until_date_ms:
            params_as_path = self.get_params_as_path(params=params)
            new_candles = get(url="https://fapi.binance.com/fapi/v1/klines?" + params_as_path).json()
            try:
                last_candle_time_ms = int(new_candles[-1][0])
                if last_candle_time_ms == params["startTime"]:
                    pass
                else:
                    candles_list.extend(new_candles)
                    # add 2 sec so we don't download the same candle two times
                    params["startTime"] = last_candle_time_ms + 2000

            except Exception as e:
                raise Exception(f"Binance Futures get_candles_main_no_keys {new_candles['msg']} - > {e}")

        candles_np = np.array(candles_list, dtype=np.float_)[:, :5]
        time_it_took_in_seconds = self.get_current_time_seconds() - start_time
        td = str(timedelta(seconds=time_it_took_in_seconds)).split(":")
        print(f"It took {td[1]} mins and {td[2]} seconds to download {len(candles_list)} candles")
        return candles_np
