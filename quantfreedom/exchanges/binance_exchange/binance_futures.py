import hmac
import hashlib
from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from time import time
BINANCE_FUTURES_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w", "1M"]


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
