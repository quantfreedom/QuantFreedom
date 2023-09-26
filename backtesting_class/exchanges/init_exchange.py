import ccxt
import pandas as pd

from typing import Optional
from datetime import datetime

from backtesting_class.candle_downloader import DownloadCandles


class SetExchange:
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        exchange_name: str,
        apikey: str = None,
        secret: str = None,
        use_testnet: bool = False,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = None,
        limit: int = None,
    ):
        self.exchange = self._configure_exchange(
            exchange_name=exchange_name,
            apikey=apikey,
            secret=secret,
            use_testnet=use_testnet,
        )
        self.symbol = symbol
        self.candle_getter = DownloadCandles(
            exchange=self.exchange,
            exchange_name=exchange_name,
            symbol=symbol,
            timeframe=timeframe,
            since_date_ms=since_date_ms,
            until_date_ms=until_date_ms,
            candles_to_dl=candles_to_dl,
            limit=limit,
        )

    def _configure_exchange(self, exchange_name, apikey, secret, use_testnet):
        if apikey is None:
            exchange = getattr(ccxt, exchange_name)()
        else:
            exchange = getattr(ccxt, exchange_name)(
                {
                    "apiKey": apikey,
                    "secret": secret,
                },
            )
        exchange.set_sandbox_mode(use_testnet)
        print("Loading Markets")
        exchange.load_markets()
        print("Done loading markets")
        return exchange
