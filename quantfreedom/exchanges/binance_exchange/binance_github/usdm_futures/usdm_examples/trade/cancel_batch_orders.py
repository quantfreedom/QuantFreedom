#!/usr/bin/env python
import logging
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures import UMFutures
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.lib_usdm.utils import config_logging
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.error import ClientError

config_logging(logging, logging.DEBUG)

key = ""
secret = ""

um_futures_client = UMFutures(key=key, secret=secret)

try:
    response = um_futures_client.cancel_batch_order(
        symbol="BTCUSDT", orderIdList=[], origClientOrderIdList=[], recvWindow=2000
    )
    logging.info(response)
except ClientError as error:
    logging.error(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
