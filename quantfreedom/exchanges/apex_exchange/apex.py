from datetime import timedelta
from quantfreedom.exchanges.apex_exchange.apex_github.http_private_stark_key_sign import HttpPrivateStark
from quantfreedom.exchanges.exchange import Exchange
from time import time

APEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]
UNIVERSAL_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]
TIMEFRAMES_IN_MINUTES = [1, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]


class Apex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        api_key: str,
        secret_key: str,
        passphrase: str,
        stark_key_public: str,
        stark_key_private: str,
        stark_key_y: str,
        use_test_net: bool,
    ):
        """
        main docs page https://api-docs.pro.apex.exchange
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            url_start = "https://testnet.pro.apex.exchange"
        else:
            url_start = "https://pro.apex.exchange"

        self.apex_stark = HttpPrivateStark(
            endpoint=url_start,
            stark_public_key=stark_key_public,
            stark_private_key=stark_key_private,
            stark_public_key_y_coordinate=stark_key_y,
            api_key_credentials={"key": api_key, "secret": secret_key, "passphrase": passphrase},
        )
        self.apex_stark.configs()
        self.apex_stark.get_account()

    def __get_exchange_timeframe(self, timeframe):
        try:
            timeframe = APEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")
        return timeframe

    def __get_timeframe_in_ms(self, timeframe):
        timeframe_in_ms = int(
            timedelta(minutes=TIMEFRAMES_IN_MINUTES[UNIVERSAL_TIMEFRAMES.index(timeframe)]).seconds * 1000
        )
        return timeframe_in_ms

    def create_order(
        self,
        symbol,
        side,
        type,
        size,
        limitFee=None,
        price=None,
        accountId=None,
        timeInForce="GOOD_TIL_CANCEL",
        reduceOnly=False,
        triggerPrice=None,
        triggerPriceType=None,
        trailingPercent=None,
        clientId=None,
        expiration=None,
        isPositionTpsl=False,
        signature=None,
        sourceFlag=None,
    ):
        """
        https://api-docs.pro.apex.exchange/#privateapi-post-creating-orders

        Use this website to see all the params
        """
        return self.apex_stark.create_order(
            symbol=symbol,
            side=side,
            type=type,
            size=size,
            limitFeeRate=self.apex_stark.account["takerFeeRate"],
            limitFee=limitFee,
            price=price,
            accountId=accountId,
            timeInForce=timeInForce,
            reduceOnly=reduceOnly,
            triggerPrice=triggerPrice,
            triggerPriceType=triggerPriceType,
            trailingPercent=trailingPercent,
            clientId=clientId,
            expiration=expiration,
            expirationEpochSeconds=time(),
            isPositionTpsl=isPositionTpsl,
            signature=signature,
            sourceFlag=sourceFlag,
        )

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = None,
        category: str = "linear",
        limit: int = 1500,
    ):
        ex_timeframe = self.__get_exchange_timeframe(timeframe=timeframe)
        timeframe_in_ms = self.__get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = self.get_candles_to_dl_in_ms(candles_to_dl, timeframe_in_ms=timeframe_in_ms, limit=limit)

        if until_date_ms is None:
            if since_date_ms is None:
                until_date_ms = self.get_current_time_ms() - timeframe_in_ms
                since_date_ms = until_date_ms - candles_to_dl_ms
            else:
                until_date_ms = since_date_ms + candles_to_dl_ms - 5000  # 5000 is to add 5 seconds
        else:
            if since_date_ms is None:
                since_date_ms = until_date_ms - candles_to_dl_ms - 5000  # 5000 is to sub 5 seconds

        candles_list = []
        end_point = "/public/v1/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": ex_timeframe,
            "start": since_date_ms,
            "end": until_date_ms,
            "limit": limit,
        }
        start_time = self.get_current_time_seconds()
        pass
