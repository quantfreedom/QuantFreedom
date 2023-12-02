from ._http_manager import _V3HTTPManager
from ._websocket_stream import _FuturesWebSocketManager
from ._websocket_stream import COPY_TRADING
from . import _helpers


ws_name = COPY_TRADING
PRIVATE_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime_private"


class HTTP(_V3HTTPManager):
    def get_instruments(self):
        """Get the spec of trading symbols

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copytrade/public/instrument-info
        """
        suffix = "/contract/v3/public/copytrading/symbol/list"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix
        )

    def place_order(self, **kwargs):
        """Create Order

        Required args:
            side (string): Side
            symbol (string): Symbol
            orderType (string): Active order type
            qty (string): Active order type

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/trade/create-order
        """
        suffix = "/contract/v3/private/copytrading/order/create"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_orders(self, **kwargs):
        """Query orders

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/trade/get-order
        """
        suffix = "/contract/v3/private/copytrading/order/list"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_order(self, **kwargs):
        """Cancel Order

        Required args:
            symbol (string): Symbol

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/trade/cancel
        """
        suffix = "/contract/v3/private/copytrading/order/cancel"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def close_order(self, **kwargs):
        """Create a specific close order

        Required args:
            symbol (string): Symbol

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/trade/close-order
        """
        suffix = "/contract/v3/private/copytrading/order/close"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_trading_stop(self, **kwargs):
        """Set Trading Stop

        Required args:
            symbol (string): Symbol
            parentOrderId (string): parentOrderId

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/trade/trading-stop
        """
        suffix = "/contract/v3/private/copytrading/order/trading-stop"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_position(self, **kwargs):
        """Position List

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/position/position-info
        """
        suffix = "/contract/v3/private/copytrading/position/list"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def close_position(self, **kwargs):
        """Close Position

        Required args:
            symbol (string): Symbol
            positionIdx (string): Position idx, used to identify positions in different position modes: 0-Single side; 1-Buy side of both side mode; 2-Sell side of both side mode

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/position/close-position
        """
        suffix = "/contract/v3/private/copytrading/position/close"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_leverage(self, **kwargs):
        """Set Leverage

        Required args:
            symbol (string): Symbol
            buyLeverage (string): The value of buy_leverage must be equal to sell_leverage.
            sellLeverage (string): The value of buy_leverage must be equal to sell_leverage.

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/position/leverage
        """
        suffix = "/contract/v3/private/copytrading/position/set-leverage"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_execution_list(self, **kwargs):
        """Query users' execution list, sort by execTime in descending order

        Required args:
            symbol (string): Symbol

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/position/execution-list
        """
        suffix = "/contract/v3/private/copytrading/execution/list"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_wallet_balance(self, **kwargs):
        """Get CopyTrading Wallet Balance

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/account/wallet
        """
        suffix = "/contract/v3/private/copytrading/wallet/balance"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def transfer(self, **kwargs):
        """Transfer

        Required args:
            transferId (string): UUID, which is unique across the platform
            coin (string): Currency. USDT only
            amount (string): Exchange to amount
            fromAccountType (string): Account type
            toAccountType (string): Account type

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/account/transfer
        """
        suffix = "/contract/v3/private/copytrading/wallet/transfer"
        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_transfer_history(self, **kwargs):
        """Get the transfer history of Copy-trade wallet

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/copy-trade/account/transfer-list
        """
        suffix = "/asset/v3/private/transfer/copy-trading/list/query"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )


class WebSocket:
    def __init__(
            self,
            testnet,
            domain="",
            api_key=None,
            api_secret=None,
            ping_interval=20,
            ping_timeout=10,
            retries=10,
            restart_on_error=True,
            trace_logging=False
    ):
        self.ws_public = None
        self.ws_private = None
        self.active_connections = []
        self.args = _helpers.make_private_args(locals())

    def _ws_private_subscribe(self, topic, callback):
        if not self.ws_private:
            self.ws_private = _FuturesWebSocketManager(
                ws_name, **self.args)
            self.ws_private._connect(PRIVATE_WSS)
            self.active_connections.append(self.ws_private)
        self.ws_private.subscribe(topic, callback)

    # Private topics
    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/copy_trading/#t-websocketposition
        """
        topic = "copyTradePosition"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/copy_trading/#t-websocketexecution
        """
        topic = "copyTradeExecution"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/copy_trading/#t-websocketorder
        """
        topic = "copyTradeOrder"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def wallet_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/copy_trading/#t-websocketwallet
        """
        topic = "copyTradeWallet"
        self._ws_private_subscribe(topic=topic, callback=callback)
