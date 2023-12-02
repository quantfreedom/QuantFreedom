from ._http_manager import _USDCHTTPManager
from ._websocket_stream import _USDCOptionsWebSocketManager
from ._websocket_stream import USDC_OPTIONS
from . import _helpers


ws_name = USDC_OPTIONS
PUBLIC_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/trade/option/usdc/public/v1"
PRIVATE_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/trade/option/usdc/private/v1"


class HTTP(_USDCHTTPManager):
    def orderbook(self, **kwargs):
        """
        Get the orderbook.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdcorderbook.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/public/v1/order-book"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_symbol(self, **kwargs):
        """
        Get symbol info.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/public/v1/symbols"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def latest_information_for_symbol(self, **kwargs):
        """
        Get the latest information for symbol.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdctickerinfo.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/public/v1/tick"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def delivery_price(self, **kwargs):
        """

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-querydeliveryprice.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/public/v1/delivery-price"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def place_active_order(self, **kwargs):
        """
        Places an active order. For more information, see
        https://bybit-exchange.github.io/docs/usdc/option/#t-usdcplaceorder.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdcplaceorder.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/place-order"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def batch_place_active_orders(self, orders: list):
        """
        Each request supports a max. of four orders. The reduceOnly parameter
        should be separate and unique for each order in the request.
        https://bybit-exchange.github.io/docs/usdc/option/#t-usdcbatchorders.

        :param orders: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdcbatchorders.
        :returns: Request results as dictionary.
        """

        query = {"orderRequest": orders}
        suffix = "/option/usdc/openapi/private/v1/batch-place-orders"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=query,
            auth=True
        )

    def cancel_active_order(self, **kwargs):
        """
        Cancels an active order. For more information, see
        https://bybit-exchange.github.io/docs/usdc/option/#t-usdccancelorder.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdccancelorder.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/cancel-order"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def batch_cancel_active_order(self, orders: list):
        """
        Cancels an active order. For more information, see
        https://bybit-exchange.github.io/docs/usdc/option/#t-usdcbatchcancelorders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdcbatchcancelorders.
        :returns: Request results as dictionary.
        """

        query = {"cancelRequest": orders}
        suffix = "/option/usdc/openapi/private/v1/batch-cancel-orders"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=query,
            auth=True
        )

    def cancel_all_active_orders(self, **kwargs):
        """
        Cancel all active orders that are unfilled or partially filled. Fully
        filled orders cannot be cancelled.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdccancelall.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/cancel-all"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def replace_active_order(self, **kwargs):
        """
        Replace order can modify/amend your active orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdcreplaceorder.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/replace-order"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def batch_replace_active_orders(self, orders: list):
        """
        Each request supports a max. of four orders. The reduceOnly parameter
        should be separate and unique for each order in the request.
        https://bybit-exchange.github.io/docs/usdc/option/#t-usdcbatchreplaceorders.

        :param orders: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-usdcbatchreplaceorders.
        :returns: Request results as dictionary.
        """

        query = {"replaceOrderRequest": orders}
        suffix = "/option/usdc/openapi/private/v1/batch-replace-orders"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=query,
            auth=True
        )

    def wallet_fund_records(self, **kwargs):
        """
        Gets transaction log. For more information, see
        https://bybit-exchange.github.io/docs/usdc/option/#t-transactionlog.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-transactionlog.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/query-transaction-log"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def query_delivery_history(self, **kwargs):
        """

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-querydeliverylog.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/query-delivery-list"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def query_position_expiration_date(self, **kwargs):
        """

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-querypositioninfo.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/query-position-exp-date"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def modify_mmp(self, **kwargs):
        """

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-modifymmp.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/mmp-modify"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def reset_mmp(self, **kwargs):
        """

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-resetmmp.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/mmp-reset"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def query_mmp(self, **kwargs):
        """

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/option/#t-querymmpstate.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/get-mmp-state"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )


class WebSocket(_USDCOptionsWebSocketManager):
    def __init__(self, **kwargs):
        super().__init__(ws_name, **kwargs)

        self.ws_public = None
        self.ws_private = None
        self.active_connections = []
        self.kwargs = kwargs
        self.public_kwargs = _helpers.make_public_kwargs(self.kwargs)

    def is_connected(self):
        return self._are_connections_connected(self.active_connections)

    def _ws_public_subscribe(self, topic, callback, symbol=None):
        if not self.ws_public:
            self.ws_public = _USDCOptionsWebSocketManager(
                ws_name, **self.public_kwargs)
            self.ws_public._connect(PUBLIC_WSS)
            self.active_connections.append(self.ws_public)
        self.ws_public.subscribe(topic, callback, symbol)

    def _ws_private_subscribe(self, topic, callback):
        if not self.ws_private:
            self.ws_private = _USDCOptionsWebSocketManager(
                ws_name, **self.kwargs)
            self.ws_private._connect(PRIVATE_WSS)
            self.active_connections.append(self.ws_private)
        self.ws_private.subscribe(topic, callback)

    def custom_topic_stream(self, wss_url, topic, callback):
        subscribe = _helpers.identify_ws_method(
            wss_url,
            {
                PUBLIC_WSS: self._ws_public_subscribe,
                PRIVATE_WSS: self._ws_private_subscribe
            })
        symbol = self._extract_symbol(topic)
        if symbol:
            subscribe(topic, callback, symbol)
        else:
            subscribe(topic, callback)

    def orderbook_25_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorderbook
        """
        topic = "orderbook25.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def orderbook_100_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorderbook
        """
        topic = "orderbook100.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def delta_orderbook_100_stream(self, callback, symbol):
        """
        This topic always returns messages in the "snapshot" format for a
        simplified user experience. pybit processes the delta/snapshot
        messages for you. Read the Bybit API documentation for more information.

        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorderbook
        """
        topic = "delta.orderbook100.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def trade_stream(self, callback, symbol):
        """
        symbol should be the currency. Eg, "BTC" instead of
        "BTC-13MAY22-25000-C"
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websockettrade
        """
        topic = "recenttrades.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def instrument_info_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def insurance_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketinsurance
        """
        topic = "platform.insurance.USDC"
        self._ws_public_subscribe(topic, callback)

    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketposition
        """
        topic = "user.openapi.option.position"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketexecution
        """
        topic = "user.openapi.option.trade"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorder
        """
        topic = "user.openapi.option.order"
        self._ws_private_subscribe(topic=topic, callback=callback)
