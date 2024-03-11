import hmac
import hashlib
import numpy as np
from time import sleep, time
from requests import get, post
from datetime import datetime, timezone
from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionModeType,
    TriggerDirectionType,
)
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange
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
        [main docs page](https://binance-docs.github.io/apidocs/futures/en)
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            self.url_start = "https://testnet.binancefuture.com"
        else:
            self.url_start = "https://fapi.binance.com"

        self.binance_ex = UMFutures(key=api_key, secret=secret_key, base_url=self.url_start)

    def __HTTP_post_request(
        self,
        end_point: str,
        params: dict,
    ):
        timestamp = str(int(time() * 1000))
        params_as_dict_string = self.get_params_as_dict_string(params=params)
        signature = self.__gen_signature(timestamp=timestamp, params_as_string=params_as_dict_string)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": timestamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        try:
            response = post(
                url=self.url_start + end_point,
                headers=headers,
                data=params_as_dict_string,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Mufex __HTTP_post_request - > {e}")

    def __HTTP_get_request(
        self,
        end_point: str,
        params: dict,
    ):
        timestamp = str(int(time() * 1000))
        params_as_path = self.get_params_as_path(params=params)
        signature = self.__gen_signature(timestamp=timestamp, params_as_string=params_as_path)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": timestamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        try:
            response = get(
                url=self.url_start + end_point + "?" + params_as_path,
                headers=headers,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Mufex __HTTP_get_request - > {e}")

    def __gen_signature(
        self,
        timestamp: str,
        params_as_string: str,
    ):
        param_str = timestamp + self.api_key + "5000" + params_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

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
        data = self.binance_ex.new_order(
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
        order_id = data["orderId"]
        return order_id

    def get_position_info(
        self,
        symbol: str,
    ):
        response = self.binance_ex.get_position_risk(symbol=symbol)
        return response

    def get_exchange_timeframe(
        self,
        timeframe: str,
    ):
        try:
            return BINANCE_USDM_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            raise Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 1500,
    ):
        """
        Summary
        -------
        [Biance USDM candle docs](https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data)

        Explainer Video
        ---------------
        Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

        Parameters
        ----------
        symbol : str
            [Use Binance USDM API for symbol list](https://binance-docs.github.io/apidocs/futures/en/#general-info)
        timeframe : str
            "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"
        since_datetime : datetime
            The start date, in datetime format, of candles you want to download. EX: datetime(year, month, day, hour, minute)
        until_datetime : datetime
            The until date, in datetime format, of candles you want to download minus one candle so if you are on the 5 min if you say your until date is 1200 your last candle will be 1155. EX: datetime(year, month, day, hour, minute)
        candles_to_dl : int
            The amount of candles you want to download

        Returns
        -------
        np.array
            a 2 dim array with the following columns "timestamp", "open", "high", "low", "close", "volume"
        """
        ex_timeframe = self.get_exchange_timeframe(timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        since_timestamp, until_timestamp = self.get_since_until_timestamp(
            candles_to_dl_ms=candles_to_dl_ms,
            since_datetime=since_datetime,
            timeframe_in_ms=timeframe_in_ms,
            until_datetime=until_datetime,
        )

        b_candles = []
        while since_timestamp + timeframe_in_ms < until_timestamp:
            try:
                b_data = self.binance_ex.klines(
                    symbol=symbol,
                    interval=ex_timeframe,
                    startTime=since_timestamp,
                    endTime=until_timestamp,
                    limit=1500,
                )
                last_candle_timestamp = b_data[-1][0]
                if last_candle_timestamp == since_timestamp:
                    sleep(0.2)
                else:
                    b_candles.extend(b_data)
                    since_timestamp = last_candle_timestamp + 2000
            except Exception as e:
                raise Exception(f"Apex get_candles - > {e}")
        candles_np = np.array(b_candles, dtype=np.float_)[:, :6]
        return candles_np

    def get_exchange_info(self):
        """
        [Binance Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information)

        Parameters
        ----------
        None

        Returns
        -------
        Dictionary
            dictionary of info about the exchange
        """
        end_point = "/fapi/v1/exchangeInfo"
        try:
            response = get(url=self.url_start + end_point).json()
            response["symbols"][0]
            return response
        except Exception as e:
            raise Exception(f"Binance get_all_symbols_info = Data or List is empty {response['message']} -> {e}")

    def get_all_symbols_info(self):
        """
        [Binance Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information)

        Parameters
        ----------
        None

        Returns
        -------
        Dictionary
            dictionary of info about the symbols
        """
        return self.get_exchange_info()["symbols"]

    def get_symbols_list(self):
        """
        [Binance Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information)

        Parameters
        ----------
        None

        Returns
        -------
        List
            List of exchange symbols
        """
        symbols = []
        for info in self.get_all_symbols_info():
            symbols.append(info["symbol"])
            symbols.sort()
        return symbols
