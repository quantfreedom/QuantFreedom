import pandas as pd
from backtesting_class.exchanges.init_exchange import SetExchange
import logging


class PhemexTest(SetExchange):
    def __init__(
        self,
        symbol: str,
        apikey: str,
        secret: str,
        timeframe: str,
        exchange: str = "phemex",
        use_testnet: bool = False,
        candles_start_date: pd.Timestamp.timestamp = None,
        candles_end_date: pd.Timestamp.timestamp = None,
        candles_limit: pd.Timestamp.timestamp = None,
    ):
        super().__init__(
            symbol,
            apikey,
            secret,
            timeframe,
            exchange,
            use_testnet,
            candles_start_date,
            candles_end_date,
            candles_limit,
        )
        self.exchange = self._configure_exchange(
            user_exchange=exchange, use_testnet=use_testnet, apikey=apikey, secret=secret
        )
        self.symbol = symbol

    def place_market_buy_order(self, entry_size, clientOid):
        self.clientOid = clientOid
        order_created = self.exchange.create_order(
            symbol=self.symbol,
            type="market",
            side="buy",
            amount=entry_size,
            params={
                "clientOid": self.clientOid,
                "posSide": "Long",
                "ordType": "Market",
            },
        )
        self.order_id = order_created["info"]["orderID"]
        return self._market_order_successful()

    def set_leverage(self):
        pass

    def _market_order_successful(self):
        try:
            fetched_order = self.exchange.fetch_orders(symbol=self.symbol)[-1]
            return fetched_order["id"] == self.order_id and fetched_order["status"] == "closed"
        except Exception as e:
            logging.warning(f"Couldnt confirm market order was created.\n {str(self.order_id)}")
            return False
