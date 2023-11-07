#!/usr/bin/env python
import logging
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures import UMFutures
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.lib.utils import config_logging

config_logging(logging, logging.DEBUG)

key = ""

um_futures_client = UMFutures(key)
logging.info(um_futures_client.renew_listen_key("the_listen_key"))
