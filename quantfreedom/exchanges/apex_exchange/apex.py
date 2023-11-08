from datetime import timedelta
from quantfreedom.exchanges.apex_exchange.apex_github.http_private_stark_key_sign import HttpPrivateStark
from quantfreedom.exchanges.apex_exchange.apex_github.http_public import HttpPublic
from quantfreedom.exchanges.exchange import Exchange
from time import time
import numpy as np

APEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W"]


class Apex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
        passphrase: str = None,
        stark_key_public: str = None,
        stark_key_private: str = None,
        stark_key_y: str = None,
    ):
        """
        main docs page https://api-docs.pro.apex.exchange
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            url_start = "https://testnet.pro.apex.exchange"
        else:
            url_start = "https://pro.apex.exchange"

        if api_key is None:
            self.apex_ex = HttpPublic(endpoint=url_start)
        else:
            self.apex_ex = HttpPrivateStark(
                endpoint=url_start,
                stark_public_key=stark_key_public,
                stark_private_key=stark_key_private,
                stark_public_key_y_coordinate=stark_key_y,
                api_key_credentials={"key": api_key, "secret": secret_key, "passphrase": passphrase},
            )
            self.apex_ex.configs()
            self.apex_ex.get_account()

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
        return self.apex_ex.create_order(
            symbol=symbol,
            side=side,
            type=type,
            size=size,
            limitFeeRate=self.apex_ex.account["takerFeeRate"],
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
        candles_to_dl: int = 200,
    ):
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=APEX_TIMEFRAMES, timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        if until_date_ms is None:
            if since_date_ms is None:
                until_date_ms = self.get_current_time_ms() - timeframe_in_ms
                since_date_ms = until_date_ms - candles_to_dl_ms
            else:
                until_date_ms = since_date_ms + candles_to_dl_ms - 5000  # 5000 is to add 5 seconds
        else:
            if since_date_ms is None:
                since_date_ms = until_date_ms - candles_to_dl_ms - 5000  # 5000 is to sub 5 seconds

        apex_data = self.apex_ex.klines(
            symbol=symbol,
            interval=ex_timeframe,
            start=int(since_date_ms / 1000),
            end=int(until_date_ms / 1000),
        )
        apex_candles = apex_data["data"][symbol]
        candle_list = []
        keys = ["t", "o", "h", "l", "c"]
        for candle in apex_candles:
            candle_list.append([candle.get(key) for key in keys])
        candles_np = np.array(candle_list, dtype=np.float_)
        return candles_np
