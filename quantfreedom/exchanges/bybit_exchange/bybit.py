import hashlib
import hmac
import numpy as np
from time import sleep, time
from datetime import datetime
from requests import get, post
from quantfreedom.enums import PositionModeType, TriggerDirectionType
from quantfreedom.exchanges.bybit_exchange.bybit_github.unified_trading import HTTP

from quantfreedom.exchanges.exchange import Exchange

BYBIT_TIMEFRAMES = ["1", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W"]


class Bybit(Exchange):
    def __init__(
        # Exchange Vars
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
    ):
        """
        main docs page https://bybit-exchange.github.io/docs/v5/intro
        """
        if api_key:
            self.api_key = api_key
            self.secret_key = secret_key
            self.bybit_ex = HTTP(testnet=use_test_net, api_key=api_key, api_secret=secret_key)

        if use_test_net:
            self.url_start = "https://api-testnet.bybit.com"
        else:
            self.url_start = "https://api.bybit.com"

    """
    ################################################################
    ################################################################
    ###################                          ###################
    ###################                          ###################
    ################### Sending Info Functionsns ###################
    ###################                          ###################
    ###################                          ###################
    ################################################################
    ################################################################
    """

    def __HTTP_post_request(self, end_point: str, params: dict):
        str_timestamp = str(int(time() * 1000))
        params_as_dict_string = self.get_params_as_dict_string(params=params)
        signature = self.__gen_signature(str_timestamp=str_timestamp, params_as_string=params_as_dict_string)
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-SIGN-TYPE": "2",
            "X-BAPI-TIMESTAMP": str_timestamp,
            "X-BAPI-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
            "referer": "Rx000377",
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
            raise Exception(f"Bybit __HTTP_post_request - > {e}")

    def __HTTP_get_request(self, end_point: str, params: dict):
        str_timestamp = str(int(time() * 1000))
        params_as_path = self.get_params_as_path(params=params)
        signature = self.__gen_signature(str_timestamp=str_timestamp, params_as_string=params_as_path)
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-SIGN-TYPE": "2",
            "X-BAPI-TIMESTAMP": str_timestamp,
            "X-BAPI-RECV-WINDOW": "5000",
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
            raise Exception(f"Bybit __HTTP_get_request - > {e}")

    def __gen_signature(self, str_timestamp: str, params_as_string: str):
        param_str = str_timestamp + self.api_key + "5000" + params_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    """
    ###################################################################
    ###################################################################
    ###################                             ###################
    ###################                             ###################
    ################### Functions no default params ###################
    ###################                             ###################
    ###################                             ###################
    ###################################################################
    ###################################################################
    """

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 1000,
        category: str = "linear",
    ):
        """
        Summary
        -------
        [Bybit candle docs](https://bybit-exchange.github.io/docs/v5/market/kline)

        Explainer Video
        ---------------
        Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

        Parameters
        ----------
        symbol : str
            [Use Bybit API for symbol list](https://bybit-exchange.github.io/docs/v5/intro)
        timeframe : str
            "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"
        since_datetime : datetime
            The start date, in datetime format, of candles you want to download. EX: datetime(year, month, day, hour, minute)
        until_datetime : datetime
            The until date, in datetime format, of candles you want to download minus one candle so if you are on the 5 min if you say your until date is 1200 your last candle will be 1155. EX: datetime(year, month, day, hour, minute)
        candles_to_dl : int
            The amount of candles you want to download
        category : str
            [Bybit categories link](https://bybit-exchange.github.io/docs/v5/enum#category)

        Returns
        -------
        np.array
            a 2 dim array with the following columns "timestamp", "open", "high", "low", "close", "volume"
        """
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=BYBIT_TIMEFRAMES, timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        since_timestamp, until_timestamp = self.get_since_until_timestamp(
            candles_to_dl_ms=candles_to_dl_ms,
            since_datetime=since_datetime,
            timeframe_in_ms=timeframe_in_ms,
            until_datetime=until_datetime,
        )

        candles_list = []
        end_point = "/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": ex_timeframe,
            "start": since_timestamp,
            "end": until_timestamp,
            "limit": 1000,
        }

        while params["end"] - timeframe_in_ms > since_timestamp:
            try:
                response: dict = get(url=self.url_start + end_point, params=params).json()
                new_candles = response["result"]["list"]
                last_candle_timestamp = int(new_candles[-1][0])
                if last_candle_timestamp == params["start"]:
                    sleep(0.2)
                else:
                    candles_list.extend(new_candles)
                    # add 2 sec so we don't download the same candle two times
                    params["end"] = last_candle_timestamp - 2000
                1 + 1

            except Exception as e:
                raise Exception(f"Bybit get_candles {response.get('message')} - > {e}")

        candles_np = np.flip(np.array(candles_list, dtype=np.float_)[:, :-1], axis=0)

        return candles_np

    def create_order(
        self,
        symbol: str,
        buy_sell: str,
        position_mode: PositionModeType,
        order_type: str,
        asset_size: float,
        category: str = "linear",
        time_in_force: str = "GTC",
        price: float = None,
        triggerDirection: TriggerDirectionType = None,
        triggerPrice: str = None,
        triggerBy: str = None,
        tpTriggerBy: str = None,
        slTriggerBy: str = None,
        custom_order_id: str = None,
        takeProfit: float = None,
        stopLoss: float = None,
        reduce_only: bool = None,
        closeOnTrigger: bool = None,
        isLeverage: int = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/order/create-order

        time_in_force:
            GoodTillCancel
            ImmediateOrCancel
            FillOrKill
            PostOnly

        position_mode: used to identify positions in different position modes. Required if you are under Hedge Mode:
            0-One-Way Mode
            1-Buy side of both side mode
            2-Sell side of both side mode

        """
        end_point = "/v5/order/create"
        params = {}
        params["symbol"] = symbol.upper()
        params["side"] = buy_sell.capitalize()
        params["category"] = category
        params["isLeverage"] = isLeverage
        params["positionIdx"] = position_mode
        params["orderType"] = order_type.capitalize()
        params["qty"] = str(asset_size)
        params["price"] = str(price) if price else price
        params["triggerDirection"] = triggerDirection
        params["triggerPrice"] = str(triggerPrice) if triggerPrice else triggerPrice
        params["triggerBy"] = triggerBy
        params["tpTriggerBy"] = tpTriggerBy
        params["slTriggerBy"] = slTriggerBy
        params["timeInForce"] = time_in_force
        params["orderLinkId"] = custom_order_id
        params["takeProfit"] = str(takeProfit) if takeProfit else takeProfit
        params["stopLoss"] = str(stopLoss) if stopLoss else stopLoss
        params["reduceOnly"] = reduce_only
        params["closeOnTrigger"] = closeOnTrigger

        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            order_id = response["result"]["orderId"]
            return order_id
        except Exception as e:
            raise Exception(f"Bybit create_order {response['retMsg']} -> {e}")
