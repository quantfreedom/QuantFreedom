import json
import logging
import hashlib
import hmac
import numpy as np
from datetime import timedelta
from quantfreedom.utils import pretty_qf
from requests import get, post
from time import sleep, time

from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionModeType,
)
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

candles_dt = np.dtype(
    [
        ("timestamp", np.int64),
        ("open", np.float_),
        ("high", np.float_),
        ("low", np.float_),
        ("close", np.float_),
    ],
    align=True,
)

BINANCE_FUTURES_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w", "1M"]


class BinanceFutures(Exchange):
    def __init__(
        # Exchange Vars
        self,
        api_key: str,
        secret_key: str,
        use_test_net: bool,
    ):
        """
        main docs page https://binance-docs.github.io/apidocs/futures/en/
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            self.url_start = "https://testnet.binancefuture.com"
        else:
            self.url_start = "https://fapi.binance.com"

    """
    ################################################################
    ################################################################
    ###################                          ###################
    ###################                          ###################
    ################### Sending Info Functionsns ###################
    ###################                          ###################
    ###################                          ###################
    ################################################################
    ################################################################
    """

    def __HTTP_post_request(self, end_point, params):
        time_stamp = str(int(time() * 1000))
        params_as_string = self.__params_as_string(params=params)
        signature = self.__gen_signature(time_stamp=time_stamp, params_as_string=params_as_string)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        try:
            response = post(
                url=self.url_start + end_point,
                headers=headers,
                data=params_as_string,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Binance Futures Something wrong with __HTTP_post_request - > {e}")

    def __HTTP_post_request_no_params(self, end_point):
        time_stamp = str(int(time() * 1000))
        signature = self.__gen_signature_no_params(time_stamp=time_stamp)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }
        try:
            response = post(url=self.url_start + end_point, headers=headers)
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Binance Futures Something wrong with __HTTP_post_request_no_params - > {e}")

    def HTTP_get_request(self, end_point, params):
        time_stamp = str(int(time() * 1000))
        params_as_path = self.__params_to_path(params=params)
        signature = self.__gen_signature(time_stamp=time_stamp, params_as_string=params_as_path)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        try:
            response = get(
                url=self.url_start + end_point + "?" + params_as_path,
                headers=headers,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Binance Futures Something wrong with HTTP_get_request - > {e}")

    def HTTP_get_request_no_params(self, end_point):
        time_stamp = str(int(time() * 1000))
        signature = self.__gen_signature_no_params(time_stamp=time_stamp)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        try:
            response = get(
                url=self.url_start + end_point,
                headers=headers,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Binance Futures Something wrong with HTTP_get_request_no_params - > {e}")

    def __params_as_string(self, params):
        params_as_string = str(json.dumps(params))
        return params_as_string

    def __params_to_path(self, params):
        entries = params.items()
        if not entries:
            pass

        paramsString = "&".join("{key}={value}".format(key=x[0], value=x[1]) for x in entries if x[1] is not None)
        if paramsString:
            return paramsString

    def __gen_signature(self, time_stamp, params_as_string):
        param_str = time_stamp + self.api_key + "5000" + params_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def __gen_signature_no_params(self, time_stamp):
        param_str = time_stamp + self.api_key + "5000"
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    """
    ###################################################################
    ###################################################################
    ###################                             ###################
    ###################                             ###################
    ################### Functions no default params ###################
    ###################                             ###################
    ###################                             ###################
    ###################################################################
    ###################################################################
    """

    def get_candles_main_no_keys(
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
        param_timeframe = self.get_exchange_timeframe(
            ex_timeframe=BINANCE_FUTURES_TIMEFRAMES, timeframe=timeframe
        )
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
            params_as_path = self.__params_to_path(params=params)
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
