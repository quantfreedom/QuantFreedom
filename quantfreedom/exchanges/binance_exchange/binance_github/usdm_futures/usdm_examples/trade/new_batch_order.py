#!/usr/bin/env python
import logging
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures import UMFutures
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.lib.utils import config_logging
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.error import ClientError

config_logging(logging, logging.DEBUG)

key = ""
secret = ""

um_futures_client = UMFutures(key=key, secret=secret)

params = [
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": "0.001",
        "timeInForce": "GTC",
        "price": "10000.1",
    },
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": "0.01",
        "timeInForce": "GTC",
        "price": "8000.1",
    },
]

try:
    response = um_futures_client.new_batch_order(params)
    logging.info(response)
except ClientError as error:
    logging.error(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
