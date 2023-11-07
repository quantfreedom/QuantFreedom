#!/usr/bin/env python
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures import UMFutures
import logging
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.lib.utils import config_logging

config_logging(logging, logging.DEBUG)

um_futures_client = UMFutures()
logging.info(um_futures_client.funding_rate("BTCUSDT", **{"limit": 100}))
