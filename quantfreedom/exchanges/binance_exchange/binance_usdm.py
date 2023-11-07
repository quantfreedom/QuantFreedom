from quantfreedom.exchanges.exchange import Exchange
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures import UMFutures

BINANCE_FUTURES_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w", "1M"]


class BinanceUSDM(Exchange):
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        use_test_net: bool,
    ):
        """
        main docs page https://binance-docs.github.io/apidocs/futures/en
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            self.url_start = "https://testnet.binancefuture.com"
        else:
            self.url_start = "https://fapi.binance.com"

        self.binance_ex = UMFutures(key=api_key, secret=secret_key, base_url=self.url_start)

    def create_order(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: float = None,
        positionSide: str = None,
        timeInForce: str = "GTC",
        reduceOnly: str = None,
        price: float = None,
        newClientOrderId: str = None,
        stopPrice: float = None,
        closePosition: str = None,
        activationPrice: float = None,
        callbackRate=None,
        workingType: str = None,
        priceProtect: str = None,
        newOrderRespType: str = None,
        priceMatch=None,
        selfTradePreventionMode=None,
        goodTillDate=None,
        recvWindow=None,
    ):
        """
        |
        | **New Order (TRADE)**
        | *Send a new order*

        :API endpoint: ``POST /fapi/v1/order``
        :API doc: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade

        :parameter symbol: string
        :parameter side: string
        :parameter type: string
        :parameter positionSide: optional string. Default BOTH for One-way Mode; LONG or SHORT for Hedge Mode. It must be passed in Hedge Mode.
        :parameter timeInForce: optional string
        :parameter quantity: optional float
        :parameter reduceOnly: optional string
        :parameter price: optional float
        :parameter newClientOrderId: optional string. An unique ID among open orders. Automatically generated if not sent.
        :parameter stopPrice: optional float. Use with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
        :parameter closePosition: optional string. true or false; Close-All, use with STOP_MARKET or TAKE_PROFIT_MARKET.
        :parameter activationPrice: optional float. Use with TRAILING_STOP_MARKET orders, default is the latest price (supporting different workingType).
        :parameter callbackRate: optional float. Use with TRAILING_STOP_MARKET orders, min 0.1, max 5 where 1 for 1%.
        :parameter workingType: optional string. stopPrice triggered by: "MARK_PRICE", "CONTRACT_PRICE". Default "CONTRACT_PRICE".
        :parameter priceProtect: optional string. "TRUE" or "FALSE", default "FALSE". Use with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
        :parameter newOrderRespType: optional float. "ACK" or "RESULT", default "ACK".
        :parameter recvWindow: optional int
        |
        """
        return self.binance_ex.new_order(
            symbol=symbol,
            side=side,
            positionSide=positionSide,
            type=type,
            timeInForce=timeInForce,
            quantity=quantity,
            reduceOnly=reduceOnly,
            price=price,
            newClientOrderId=newClientOrderId,
            stopPrice=stopPrice,
            closePosition=closePosition,
            activationPrice=activationPrice,
            callbackRate=callbackRate,
            workingType=workingType,
            priceProtect=priceProtect,
            newOrderRespType=newOrderRespType,
            priceMatch=priceMatch,
            selfTradePreventionMode=selfTradePreventionMode,
            goodTillDate=goodTillDate,
            recvWindow=recvWindow,
        )
