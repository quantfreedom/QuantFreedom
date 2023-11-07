import json

from ._websocket_stream import _identify_ws_method, _make_public_kwargs, _WebSocketManager, \
    _ApexWebSocketManager, PUBLIC_WSS, PRIVATE_WSS

from concurrent.futures import ThreadPoolExecutor



class WebSocket(_ApexWebSocketManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ws_public = None
        self.ws_private = None
        self.kwargs = kwargs
        self.public_kwargs = _make_public_kwargs(self.kwargs)

    def _ws_public_subscribe(self, sendStr, topic, callback):
        if not self.ws_public:
            self.ws_public = _ApexWebSocketManager(
                **self.public_kwargs)
            self.ws_public._connect(self.endpoint + PUBLIC_WSS)
        self.ws_public.subscribe(sendStr, topic, callback)

    def _ws_private_subscribe(self,topic, callback):
        if not self.ws_private:
            self.ws_private = _ApexWebSocketManager(
                **self.kwargs)
            self.ws_private._connect(self.endpoint + PRIVATE_WSS)
        self.ws_private.subscribe("", topic, callback)

    def custom_topic_stream(self, topic, callback, wss_url):
        subscribe = _identify_ws_method(
            wss_url,
            {
                PUBLIC_WSS: self._ws_public_subscribe,
                PRIVATE_WSS: self._ws_private_subscribe
            })
        subscribe(topic, callback)

    def depth_stream(self, callback, symbol, limit):
        """
        https://api-docs.pro.apex.exchange/#public-websocket-depth
        """
        arg = "orderBook" + str(limit) + ".H." + symbol
        topic = \
            {
                "op": "subscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)
    def unsub_depth_topic_stream(self, callback, arg):
        """
        https://api-docs.pro.apex.exchange/#public-websocket-depth
        """
        topic = \
            {
                "op": "unsubscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)
    def depth_topic_stream(self, callback, arg):
        """
        https://api-docs.pro.apex.exchange/#public-websocket-depth
        """
        topic = \
            {
                "op": "subscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)
    def ticker_stream(self, callback, symbol):
        """
        https://api-docs.pro.apex.exchange/#public-websocket-ticker
        """
        arg = "instrumentInfo" + ".H." + symbol
        topic = \
            {
                "op": "subscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)

    def all_ticker_stream(self, callback):
        """
        https://api-docs.pro.apex.exchange/#public-websocket-ticker
        """
        arg = "instrumentInfo.all"
        topic = \
            {
                "op": "subscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)

    def klines_stream(self, callback, symbol, interval):
        """
        https://api-docs.pro.apex.exchange/#public-websocket-candlestick-chart
        """
        arg = "candle" + "." + str(interval) + "." + symbol
        topic = \
            {
                "op": "subscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)

    def trade_stream(self, callback, symbol):
        """
       https://api-docs.pro.apex.exchange/#public-websocket-trade
        """
        arg = "recentlyTrade" + ".H." + symbol
        topic = \
            {
                "op": "subscribe",
                "args": [arg]
            }
        topicStr = json.dumps(topic, sort_keys=True, separators=(",", ":"))
        self._ws_public_subscribe(topicStr, arg, callback)


    def account_info_stream(self, callback):
        """
        https://api-docs.pro.apex.exchange/#private-websocket
        """
        topic = "ws_accounts_v1"
        self._ws_private_subscribe(topic=topic, callback=callback)
