from ._http_manager import _USDCHTTPManager
from ._websocket_stream import _USDCWebSocketManager
from ._websocket_stream import USDC_PERPETUAL
from . import _helpers


ws_name = USDC_PERPETUAL
PUBLIC_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/perpetual/ws/v1/realtime_public"
PRIVATE_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/trade/option/usdc/private/v1"


class HTTP(_USDCHTTPManager):
    def query_kline(self, **kwargs):
        """
        Get kline.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-querykline.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/kline/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_mark_price_kline(self, **kwargs):
        """
        Query mark price kline (like query_kline but for mark price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-markkline.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/mark-price-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def orderbook(self, **kwargs):
        """
        Get the orderbook.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdcorderbook.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/order-book"
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

        suffix = "/perpetual/usdc/openapi/public/v1/symbols"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def latest_information_for_symbol(self, **kwargs):
        """
        Get the latest information for symbol.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdctickerinfo.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/tick"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_index_price_kline(self, **kwargs):
        """
        Query index price kline (like query_kline but for index price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-indexkline.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/index-price-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_premium_index_kline(self, **kwargs):
        """
        Query premium index kline (like query_kline but for the premium index
        discount).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-premiumkline.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/premium-index-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def open_interest(self, **kwargs):
        """
        Gets the total amount of unsettled contracts. In other words, the total
        number of contracts held in open positions.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-queryopeninterest.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/perpetual/usdc/openapi/public/v1/open-interest",
            query=kwargs
        )

    def latest_big_deal(self, **kwargs):
        """
        Obtain filled orders worth more than 500,000 USD within the last 24h.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-bigdealorder.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/perpetual/usdc/openapi/public/v1/big-deal",
            query=kwargs
        )

    def long_short_ratio(self, **kwargs):
        """
        Gets the Bybit long-short ratio.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-accountratio.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/perpetual/usdc/openapi/public/v1/account-ratio",
            query=kwargs
        )

    def place_active_order(self, **kwargs):
        """
        Places an active order. For more information, see
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdcplaceorder.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdcplaceorder.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/private/v1/place-order"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_active_order(self, **kwargs):
        """
        Cancels an active order. For more information, see
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdccancelorder.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdccancelorder.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/private/v1/cancel-order"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_all_active_orders(self, **kwargs):
        """
        Cancel all active orders that are unfilled or partially filled. Fully
        filled orders cannot be cancelled.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdccancelall.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/private/v1/cancel-all"

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
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-usdcreplaceorder.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/private/v1/replace-order"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def wallet_fund_records(self, **kwargs):
        """
        Gets transaction log. For more information, see
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-transactionlog.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-transactionlog.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/query-transaction-log"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_leverage(self, **kwargs):
        """
        Change user leverage.
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-setpositionleverage

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-setpositionleverage.
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/private/v1/position/leverage/save"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_settlement_history(self, **kwargs):
        """
        Get settlement history.
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-querysettlelogs

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-querysettlelogs.
        :returns: Request results as dictionary.
        """

        suffix = "/option/usdc/openapi/private/v1/session-settlement"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_risk_limit(self, **kwargs):
        """
        Get risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-queryrisklimits
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/public/v1/risk-limit/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_risk_limit(self, **kwargs):
        """
        Set risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/usdc/perpetual/#t-setrisklimits
        :returns: Request results as dictionary.
        """

        suffix = "/perpetual/usdc/openapi/private/v1/position/set-risk-limit"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )


class WebSocket(_USDCWebSocketManager):
    def __init__(self, **kwargs):
        super().__init__(ws_name, **kwargs)

        self.ws_public = None
        self.ws_private = None
        self.active_connections = []
        self.kwargs = kwargs
        self.public_kwargs = _helpers.make_public_kwargs(self.kwargs)

    def is_connected(self):
        return self._are_connections_connected(self.active_connections)

    def _ws_public_subscribe(self, topic, callback, symbol):
        if not self.ws_public:
            self.ws_public = _USDCWebSocketManager(
                ws_name, **self.public_kwargs)
            self.ws_public._connect(PUBLIC_WSS)
            self.active_connections.append(self.ws_public)
        self.ws_public.subscribe(topic, callback, symbol)

    def _ws_private_subscribe(self, topic, callback):
        if not self.ws_private:
            self.ws_private = _USDCWebSocketManager(
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
        This topic always returns messages in the "snapshot" format for a
        simplified user experience. pybit processes the delta/snapshot
        messages for you. Read the Bybit API documentation for more information.

        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorderbook
        """
        topic = "orderBookL2_25.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def orderbook_200_stream(self, callback, symbol):
        """
        This topic always returns messages in the "snapshot" format for a
        simplified user experience. pybit processes the delta/snapshot
        messages for you. Read the Bybit API documentation for more information.

        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorderbook
        """
        topic = "orderBook_200.100ms.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def trade_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websockettrade
        """
        topic = "trade.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def instrument_info_stream(self, callback, symbol):
        """
        This topic always returns messages in the "snapshot" format for a
        simplified user experience. pybit processes the delta/snapshot
        messages for you. Read the Bybit API documentation for more information.

        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.100ms.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def kline_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketkline
        """
        topic = "candle.{}.{}"
        topic = topic.format(str(interval), "{}")
        self._ws_public_subscribe(topic, callback, symbol)

    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketposition
        """
        topic = "user.openapi.perp.position"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketexecution
        """
        topic = "user.openapi.perp.trade"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/usdc/perpetual/#t-websocketorder
        """
        topic = "user.openapi.perp.order"
        self._ws_private_subscribe(topic=topic, callback=callback)
