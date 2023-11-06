import hmac
import hashlib
from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from time import time

from quantfreedom.exchanges.exchange import Exchange

BINANCE_FUTURES_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w", "1M"]


class BinanceUSDM(Exchange):
    def __init__(
        # Exchange Vars
        self,
        api_key: str,
        secret_key: str,
        use_test_net: bool,
    ):
        """
        main docs page https://www.mufex.finance/apidocs/derivatives/contract/index.html

        Make sure you have your position mode set to hedge or else a lot of functions will not work.
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            self.url_start = "https://testnet.binancefuture.com"
        else:
            self.url_start = "https://fapi.binance.com"

    def __HTTP_post_request(self, end_point, params):
        time_stamp = str(int(time() * 1000))
        params_as_string = self.__get_params_as_json_string(params=params)
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

    def sign_request(self, http_method, url_path, payload=None, special=False):
        if payload is None:
            payload = {}
        payload["timestamp"] = time()
        query_string = self._prepare_params(payload, special)
        payload["signature"] = self._get_sign(query_string)
        return self.send_request(http_method, url_path, payload, special)

    def _get_sign(self, payload):
        if self.private_key:
            return rsa_signature(self.private_key, payload, self.private_key_pass)
        return hmac_hashing(self.secret, payload)

    def hmac_hashing(secret, payload):
        m = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256)
        return m.hexdigest()

    def rsa_signature(private_key, payload, private_key_pass=None):
        private_key = RSA.import_key(private_key, passphrase=private_key_pass)
        h = SHA256.new(payload.encode("utf-8"))
        signature = pkcs1_15.new(private_key).sign(h)
        return b64encode(signature)
