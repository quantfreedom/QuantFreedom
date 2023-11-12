from time import sleep
import numpy as np
from quantfreedom.exchanges.exchange import Exchange
from quantfreedom.exchanges.binance_exchange.binance_github.usdm_futures.um_futures import UMFutures

BINANCE_USDM_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]


class BinanceUSDM(Exchange):
    def __init__(
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
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
        https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
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

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = 1500,
    ):
        """
        https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data
        """
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=BINANCE_USDM_TIMEFRAMES, timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        if until_date_ms is None:
            if since_date_ms is None:
                until_date_ms = self.get_current_time_ms() - timeframe_in_ms
                since_date_ms = until_date_ms - candles_to_dl_ms
            else:
                until_date_ms = since_date_ms + candles_to_dl_ms - 5000  # 5000 is to sub 5 seconds
        else:
            if since_date_ms is None:
                since_date_ms = until_date_ms - candles_to_dl_ms
                until_date_ms -= 5000

        b_candles = []
        while since_date_ms + timeframe_in_ms < until_date_ms:
            try:
                b_data = self.binance_ex.klines(
                    symbol=symbol,
                    interval=ex_timeframe,
                    startTime=since_date_ms,
                    endTime=until_date_ms,
                    limit=1500,
                )
                last_candle_time_ms = b_data[-1][0]
                if last_candle_time_ms == since_date_ms:
                    sleep(0.2)
                else:
                    b_candles.extend(b_data)
                    since_date_ms = last_candle_time_ms + 2000
            except Exception as e:
                raise Exception(f"Apex get_candles - > {e}")
        candles_np = np.array(b_candles, dtype=np.float_)[:, :5]
        return candles_np
