import hashlib
import hmac
import base64
import numpy as np
from datetime import timedelta
from requests import get, post
from time import sleep, time
from quantfreedom.exchanges.apex_exchange.apexpro.http_private_stark_key_sign import HttpPrivateStark
from quantfreedom.exchanges.apex_exchange.apexpro.constants import NETWORKID_TEST, NETWORKID_MAIN
from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionModeType,
)
from quantfreedom.exchanges.exchange import Exchange

APEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]


class Apex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        api_key: str,
        secret_key: str,
        passphrase: str,
        stark_key_public: str,
        stark_key_private: str,
        stark_key_y: str,
        use_test_net: bool,
    ):
        """
        main docs page https://api-docs.pro.apex.exchange
        """
        super().__init__(api_key, secret_key, use_test_net)

        self.passphrase = passphrase
        if use_test_net:
            self.url_start = "https://testnet.pro.apex.exchange"
            # network_id = NETWORKID_TEST
        else:
            self.url_start = "https://pro.apex.exchange"
            # network_id = NETWORKID_MAIN

        self.apex_stark = HttpPrivateStark(
            endpoint=self.url_start,
            # network_id=network_id,
            stark_public_key=stark_key_public,
            stark_private_key=stark_key_private,
            stark_public_key_y_coordinate=stark_key_y,
            api_key_credentials={"key": api_key, "secret": secret_key, "passphrase": passphrase},
        )
        self.apex_stark.configs()
        self.apex_stark.get_account()

    def HTTP_get_request(self, end_point: str, params={}):
        timestamp = str(int(round(time() * 1000)))
        ending_url, params_as_path = self.__get_params_as_path(end_point=end_point, params=params)
        signature = self.__gen_signature(
            method="GET", ending_url=ending_url, timestamp=timestamp, params_as_path=params_as_path
        )
        headers = {
            "APEX-SIGNATURE": signature,
            "APEX-API-KEY": self.api_key,
            "APEX-TIMESTAMP": timestamp,
            "APEX-PASSPHRASE": self.passphrase,
        }

        try:
            response = get(
                url=self.url_start + ending_url,
                headers=headers,
                params=params,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Apex Something wrong with HTTP_get_request_no_params - > {e}")

    def __get_params_as_path(self, end_point, params):
        entries = params.items()
        if not entries:
            return end_point, ""

        params_as_path = "&".join("{key}={value}".format(key=x[0], value=x[1]) for x in entries if x[1] is not None)
        if params_as_path:
            return end_point + "?" + params_as_path, params_as_path

    def __gen_signature(
        self,
        ending_url: str,
        method: str,
        timestamp: str,
        params_as_path: dict,
    ):
        message_string = timestamp + method + ending_url + params_as_path
        hashed = hmac.new(
            base64.standard_b64encode(
                (self.secret_key).encode(encoding="utf-8"),
            ),
            msg=message_string.encode(encoding="utf-8"),
            digestmod=hashlib.sha256,
        )
        return base64.standard_b64encode(hashed.digest()).decode()

    def get_user(self, **kwargs):
        """ "
        GET Retrieve User Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-retrieve-user-data
        :returns: Request results as dictionary.
        """

        end_point = "/api/v1/user"
        response = self.HTTP_get_request(end_point=end_point)
        try:
            data_list = response["data"]
            return data_list
        except Exception as e:
            raise Exception(f"Apex get_user = Data or List is empty {response['message']} -> {e}")

    def get_all_order_history(self, **kwargs):
        """ "
        GET Retrieve User Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-all-order-history
        :returns: Request results as dictionary.
        """

        end_point = "/api/v1/history-orders"
        response = self.HTTP_get_request(end_point=end_point)
        try:
            data_list = response["data"]
            return data_list
        except Exception as e:
            raise Exception(f"Apex get_all_order_history = Data or List is empty {response['message']} -> {e}")

    def get_trade_history(self, **kwargs):
        """ "
        GET Retrieve User Data.
        :param kwargs: See
        https://api-docs.pro.apex.exchange/#privateapi-get-trade-history
        :returns: Request results as dictionary.
        """

        end_point = "/api/v1/fills"
        response = self.HTTP_get_request(end_point=end_point)
        try:
            data_list = response["data"]
            return data_list
        except Exception as e:
            raise Exception(f"Apex get_trade_history = Data or List is empty {response['message']} -> {e}")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = None,
        category: str = "linear",
        limit: int = 1500,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline

        timeframe: "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"

        returning dict is [start, open, high, low, close, volume, turnover]

        use link to see all Request Parameters
        """
        timeframe = self.get_exchange_timeframe(ex_timeframe=APEX_TIMEFRAMES, timeframe=timeframe)
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
        end_point = "/public/v1/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": timeframe,
            "start": since_date_ms,
            "end": until_date_ms,
            "limit": limit,
        }
        start_time = self.get_current_time_seconds()
        while params["start"] + timeframe_in_ms < until_date_ms:
            response = self.HTTP_get_request(end_point=end_point, params=params)
            try:
                new_candles = response["data"]["list"]
                last_candle_time_ms = int(new_candles[-1][0])
                if last_candle_time_ms == params["start"]:
                    sleep(0.2)
                else:
                    candles_list.extend(new_candles)
                    # add 2 sec so we don't download the same candle two times
                    params["start"] = last_candle_time_ms + 2000

            except Exception as e:
                raise Exception(f"Mufex get_candles_df {response.get('message')} - > {e}")

        candles_np = np.array(candles_list, dtype=np.float_)[:, :-2]
        time_it_took_in_seconds = self.get_current_time_seconds() - start_time
        td = str(timedelta(seconds=time_it_took_in_seconds)).split(":")
        print(f"It took {td[1]} mins and {td[2]} seconds to download {len(candles_list)} candles")

        return candles_np
