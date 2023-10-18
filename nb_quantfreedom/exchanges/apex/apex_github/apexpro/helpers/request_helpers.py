import json
import random
import time
from datetime import datetime

import dateutil.parser as dp
from web3 import Web3

from apexpro.eth_signing.util import strip_hex_prefix
from apexpro.starkex.helpers import serialize_signature, deserialize_signature, int_to_hex_32
from apexpro.starkex.starkex_resources.proxy import sign, verify, get_hash
from apexpro.starkex.starkex_resources.python_signature import inv_mod_curve_size


def generate_query_path(url, params):
    entries = params.items()
    if not entries:
        return url

    paramsString = '&'.join('{key}={value}'.format(
        key=x[0], value=x[1]) for x in entries if x[1] is not None)
    if paramsString:
        return url + '?' + paramsString

    return url


def json_stringify(data):
    return json.dumps(data, separators=(',', ':'))

def json_msg_stringify(data):
    return json.dumps(data, separators=(',', ': '), indent=2)


def random_client_id():
    return str(int(float(str(random.random())[2:])))


def generate_now_iso():
    return datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%S.%f',
    )[:-3] + 'Z'


def generate_now():
    now = time.time()
    return int(round(now * 1000))


def iso_to_epoch_seconds(iso):
    return dp.parse(iso).timestamp()


def epoch_seconds_to_iso(epoch):
    return datetime.utcfromtimestamp(epoch).strftime(
        '%Y-%m-%dT%H:%M:%S.%f',
    )[:-3] + 'Z'


def remove_nones(original):
    return {k: v for k, v in original.items() if v is not None}


def calc_bind_owner_key_sig_hash(star_key_hex, owner_key):
    data_bytes = "UserRegistration:"
    owner_key_bytes = bytes.fromhex(strip_hex_prefix(owner_key))
    data = Web3.solidityKeccak(
        [
            'string',
            'bytes20',
            'uint256',
        ],
        [
            data_bytes,
            owner_key_bytes,
            int(star_key_hex, 16),
        ]
    )
    print(data.hex())
    return data


def starkex_sign(hash, private_key_hex):
    """Sign the hash of the object using the given private key."""
    EC_ORDER = 3618502788666131213697322783095070105526743751716087489154079457884512865583
    hash_mod = int(hash.hex(), 16) % EC_ORDER
    print("hash_mod:" + int_to_hex_32(hash_mod))
    r, s = sign(hash_mod, int(private_key_hex, 16))
    return serialize_signature(r, s)

def starkex_verify(hash, sign, pub_key):
    EC_ORDER = 3618502788666131213697322783095070105526743751716087489154079457884512865583
    hash_mod = int(hash.hex(), 16) % EC_ORDER
    r, s = deserialize_signature(sign)
    return verify(hash_mod, r, s, int(pub_key, 16))
