from datetime import timedelta
import hashlib
import hmac
import json
import time

from requests import get, post

from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

APEX_TIMEFRAMES = ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"]
# ------------ API URLs ------------
APEX_HTTP_MAIN = "https://pro.apex.exchange"
APEX_HTTP_TEST = "https://testnet.pro.apex.exchange"
APEX_WS_MAIN = "wss://quote.pro.apex.exchange"
APEX_WS_TEST = "wss://quote-qa.pro.apex.exchange"

# ------------ network_id ------------
NETWORKID_MAIN = 1
NETWORKID_TEST = 5


class Apex(Exchange):
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        use_test_net: bool,
        stark_public_key: str,
        stark_private_key: str,
        stark_public_key_y_coordinate: str,
    ):
        super().__init__(api_key, secret_key, use_test_net)
        if use_test_net:
            self.url_start = "https://testnet.pro.apex.exchange"
            self.network_id = NETWORKID_TEST
        else:
            self.url_start = "https://pro.apex.exchange"
            self.network_id = NETWORKID_TEST

    headers = {
        "APEX-SIGNATURE": signature,
        "APEX-API-KEY": self.api_key_credentials.get("key"),
        "APEX-TIMESTAMP": str(now_iso),
        "APEX-PASSPHRASE": self.api_key_credentials.get("passphrase"),
    }

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
            raise Exception(f"Mufex Something wrong with __HTTP_post_request - > {e}")

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
            raise Exception(f"Mufex Something wrong with __HTTP_post_request_no_params - > {e}")

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
            raise Exception(f"Mufex Something wrong with HTTP_get_request - > {e}")

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
            raise Exception(f"Mufex Something wrong with HTTP_get_request_no_params - > {e}")

    def __params_as_string(self, params):
        params_as_string = str(json.dumps(params))
        return params_as_string

    def __params_to_path(self, params):
        entries = params.items()
        if not entries:
            pass

        paramsString = "&".join("{key}={value}")key=x[0], value=x[1]) for x in entries if x[1] is not None)
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
