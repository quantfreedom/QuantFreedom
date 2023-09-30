import json
import time
import hashlib
import hmac

import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from requests import get, post

from quantfreedom.enums import ExchangeSettings, PositionIdxType, PositionModeType, TriggerDirectionType

MUFEX_TIMEFRAMES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]
UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]


class Mufex:
    def __init__(
        self,
        symbol: str,
        category: str,
        timeframe: str,
        api_key: str,
        secret_key: str,
        keep_volume_in_candles: bool = False,
        # position_mode: int = PositionMode.OneWayMode,
    ):
        """
        Make sure you have your position mode set to hedge or else a lot of functions will not work.
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.symbol = symbol
        self.category = category
        self.volume_yes_no = -2
        self.url_start = "https://api.mufex.finance"

        self.__set_exchange_settings()
        # self.__set_position_mode(position_mode=position_mode)

        if keep_volume_in_candles:
            self.volume_yes_no = -1
        try:
            self.timeframe = MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
            self.timeframe_in_ms = timedelta(minutes=self.timeframe).seconds * 1000
        except:
            raise TypeError(f"You need to send the following {UNIVERSAL_TIMEFRAMES}")

    def set_leverage_test(self, leverage: float, tradeMode: int = 1):
        pass

    def set_leverage(self, leverage: float, tradeMode: int = 1):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        """
        end_point = "/private/v1/account/set-isolated"
        leverage = str(leverage)
        params = {
            "symbol": self.symbol,
            "tradeMode": tradeMode,
            "buyLeverage": leverage,
            "sellLeverage": leverage,
        }
        try:
            data_orderId = self.__HTTP_post_request(end_point=end_point, params=params)
            if data_orderId == orderId:
                return True
            else:
                return False
        except KeyError as e:
            raise KeyError(f"Something is wrong set_leverage {e}")

    def __HTTP_post_request(self, end_point, params):
        time_stamp = str(int(time.time() * 1000))
        params_as_string = self.__params_as_string(params=params)
        signature = self.__genSignature(time_stamp=time_stamp, paras_as_string=params_as_string)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }
        response = post(
            url=self.url_start + end_point,
            headers=headers,
            data=params_as_string,
        )
        try:
            response_json = response.json()
            if not response_json["data"]:
                raise KeyError(f' -> {response_json["message"]}')
        except KeyError as e:
            raise KeyError(f"{e}")
        return response_json

    def __HTTP_get_request(self, end_point, params):
        time_stamp = str(int(time.time() * 1000))
        params_as_path = self.__params_to_path(params=params)
        signature = self.__genSignature(time_stamp=time_stamp, paras_as_string=params_as_path)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        response = get(
            url=self.url_start + end_point + "?" + params_as_path,
            headers=headers,
        )
        try:
            response_json = response.json()
            if not response_json["data"]:
                raise KeyError(f' -> {response_json["message"]}')
        except KeyError as e:
            raise KeyError(f"{e}")
        return response_json

    def get_buy_position_info(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": self.symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            # TODO how do you try this if the list is zero?
            order_info_og = data_order_info["data"]["list"][0]
            if float(order_info_og["entryPrice"]) > 0:
                return order_info_og
            else:
                raise KeyError("Looks like we aren't in a buy posiiton.")

        except KeyError as e:
            raise KeyError(f"Something is wrong with get_buy_position_info {e}")

    def get_sell_position_info(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": self.symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            # TODO how do you try this if the list is zero?
            order_info_og = data_order_info["data"]["list"][1]
            if float(order_info_og["entryPrice"]) > 0:
                return order_info_og
            else:
                raise KeyError("Looks like we aren't in a sell posiiton.")

        except KeyError as e:
            raise KeyError(f"Something is wrong with get_sell_position_info {e}")

    def check_if_in_sell_position(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": self.symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            # TODO how do you try this if the list is zero?
            order_info_og = data_order_info["data"]["list"][1]
            if float(order_info_og["entryPrice"]) > 0:
                return True
            else:
                return False

        except KeyError as e:
            raise KeyError(f"Something is wrong with check_if_in_sell_position {e}")

    def check_if_in_buy_position(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": self.symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            # TODO how do you try this if the list is zero?
            order_info_og = data_order_info["data"]["list"][0]
            if float(order_info_og["entryPrice"]) > 0:
                return True
            else:
                return False

        except KeyError as e:
            raise KeyError(f"Something is wrong with check_if_in_buy_position {e}")

    def check_if_order_canceled(
        self,
        orderId: str,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_getopenorder
        """
        end_point = "/private/v1/trade/activity-orders"
        params = {
            "symbol": self.symbol,
            "orderId": orderId,
        }
        try:
            order_info_og = self.__HTTP_get_request(end_point=end_point, params=params)
            # TODO how do you try this if the list is zero?
            order_status = order_info_og["data"]["list"][0]["orderStatus"]
            if order_status in ["Cancelled", "Deactivated"]:
                return True
            else:
                return False
        except KeyError as e:
            raise KeyError(f"Something is wrong checking if order is canceled {e}")

    def check_if_order_open(
        self,
        orderId: str,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_getopenorder
        """
        end_point = "/private/v1/trade/activity-orders"
        params = {
            "symbol": self.symbol,
            "orderId": orderId,
        }
        try:
            order_info_og = self.__HTTP_get_request(end_point=end_point, params=params)
            # TODO how do you try this if the list is zero?
            order_status = order_info_og["data"]["list"][0]["orderStatus"]
            if order_status in ["New", "Untriggered"]:
                return True
            else:
                return False
        except KeyError as e:
            raise KeyError(f"Something is wrong checking if order is open {e}")

    def cancel_order(
        self,
        orderId: str,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_cancelorder
        """
        end_point = "/private/v1/trade/cancel"
        params = {
            "symbol": self.symbol,
            "orderId": orderId,
        }
        try:
            data_orderId = self.__HTTP_post_request(end_point=end_point, params=params)["data"]["orderId"]
            if data_orderId == orderId:
                return True
            else:
                return False
        except KeyError as e:
            raise KeyError(f"Something is wrong cancel order {e}")

    def create_limit_entry_order(
        self,
        side: str,
        positionIdx: PositionIdxType,
        qty: float,
        price: float,
        orderLinkId: str,
        timeInForce: str = "PostOnly",
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        end_point = "/private/v1/trade/create"
        params = {
            "symbol": self.symbol,
            "side": side,
            "positionIdx": positionIdx,
            "orderType": "Limit",
            "qty": str(qty),
            "price": str(price),
            "timeInForce": timeInForce,
            "orderLinkId": orderLinkId,
        }

        try:
            order_info = self.__HTTP_post_request(end_point=end_point, params=params)["data"]
            orderId = order_info["orderId"]
            orderLinkId = order_info["orderLinkId"]
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the limit entry order {e}")
        return orderId, orderLinkId

    def create_market_entry_order(
        self,
        side: str,
        positionIdx: PositionIdxType,
        qty: float,
        orderLinkId: str,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        end_point = "/private/v1/trade/create"
        params = {
            "symbol": self.symbol,
            "side": side,
            "positionIdx": positionIdx,
            "orderType": "Market",
            "qty": str(qty),
            "timeInForce": "GoodTillCancel",
            "orderLinkId": orderLinkId,
        }

        try:
            order_info = self.__HTTP_post_request(end_point=end_point, params=params)["data"]
            orderId = order_info["orderId"]
            orderLinkId = order_info["orderLinkId"]
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the market entry order {e}")
        return orderId, orderLinkId

    def create_tp_limit_order(
        self,
        side: str,
        positionIdx: PositionIdxType,
        qty: float,
        price: float,
        orderLinkId: str,
        timeInForce: str = "PostOnly",
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        end_point = "/private/v1/trade/create"
        params = {
            "symbol": self.symbol,
            "side": side,
            "positionIdx": positionIdx,
            "orderType": "Limit",
            "qty": str(qty),
            "price": str(price),
            "timeInForce": timeInForce,
            "reduceOnly": True,
            "orderLinkId": orderLinkId,
        }
        try:
            order_info = self.__HTTP_post_request(end_point=end_point, params=params)["data"]
            orderId = order_info["orderId"]
            orderLinkId = order_info["orderLinkId"]
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the take profit order {e}")
        return orderId, orderLinkId

    def create_sl_order(
        self,
        side: str,
        positionIdx: PositionIdxType,
        qty: float,
        orderLinkId: str,
        triggerPrice: float,
        triggerDirection: TriggerDirectionType,
        timeInForce: str = "GoodTillCancel",
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        end_point = "/private/v1/trade/create"
        params = {
            "symbol": self.symbol,
            "side": side,
            "positionIdx": positionIdx,
            "orderType": "Market",
            "qty": str(qty),
            "timeInForce": timeInForce,
            "reduceOnly": True,
            "triggerPrice": str(triggerPrice),
            "triggerDirection": triggerDirection,
            "orderLinkId": orderLinkId,
        }

        try:
            order_info = self.__HTTP_post_request(end_point=end_point, params=params)["data"]
            orderId = order_info["orderId"]
            orderLinkId = order_info["orderLinkId"]
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the stop loss order {e}")
        return orderId, orderLinkId

    def get_symbol_info(
        self,
        symbol: str = None,
        category: str = "linear",
        limit: int = 1000,
    ):
        end_point = "/public/v1/instruments"
        params = {
            "category": category,
            "symbol": symbol,
            "limit": limit,
        }
        try:
            symbol_info = self.__HTTP_get_request(url=self.url_start + end_point + "?", params=params)["data"]["list"]
        except KeyError as e:
            raise KeyError(f"Something is wrong getting symbol_info {e}")

        return symbol_info

    def get_candles(
        self,
        candles_to_dl: int = None,
        since_date_ms: int = None,
        until_date_ms: int = None,
        limit: int = None,
    ):
        candles_list = []
        if until_date_ms is None:
            until_date_ms = int(datetime.now().timestamp() * 1000) - self.timeframe_in_ms

        if since_date_ms is None and candles_to_dl is not None:
            since_date_ms = until_date_ms - self.timeframe_in_ms * candles_to_dl
        else:
            since_date_ms = until_date_ms - self.timeframe_in_ms * 200

        end_point = "/public/v1/market/kline"
        params = {
            "category": self.category,
            "symbol": self.symbol,
            "interval": self.timeframe,
            "limit": limit,
            "end": until_date_ms,
        }

        # since_pd_timestamp = pd.to_datetime(int(since_date_ms / 1000), unit="s")
        # until_pd_timestamp = pd.to_datetime(int(until_date_ms / 1000), unit="s")
        # print(f"since_date_ms={since_pd_timestamp}, until_date_ms={until_pd_timestamp}")
        print(f"Downloading Candles")
        start_time = int(datetime.now().timestamp())
        while since_date_ms < until_date_ms:
            params["start"] = since_date_ms
            try:
                new_candles_og = self.__HTTP_get_request(end_point=end_point, params=params)
                new_candles = new_candles_og["data"]["list"]
            except Exception as e:
                # print(f"Got exception -> {repr(e)}")
                break

            if new_candles is None:
                break
            else:
                # print(f"Got {len(new_candles)} new candles for since={since_pd_timestamp}")
                candles_list.extend(new_candles)
                since_date_ms = int(candles_list[-1][0]) + 1000
                # since_pd_timestamp = pd.to_datetime(since_date_ms, unit="ms")
                # print(f"Getting candles since={since_pd_timestamp}")

        # if until_date_ms - int(candles_list[-1][0]) < 0:
        #     print("revmoing last candle because it is the current candle")
        #     candles_list = candles_list[:-1]
        # else:
        #     print("last candle is the right candle")
        candles_df = self.__candles_list_to_pd(candles_list=candles_list)
        print(
            f"It took {round((int(datetime.now().timestamp()) - start_time)/60,2)} minutes to create the candles dataframe"
        )
        return candles_df

    def __candles_list_to_pd(self, candles_list):
        candles = np.array(candles_list, dtype=np.float_)[:, : self.volume_yes_no]
        candles_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        candles_df = candles_df.astype({"timestamp": "int64"})
        candles_df.timestamp = pd.to_datetime(candles_df.timestamp, unit="ms")
        return candles_df

    def __params_as_string(self, params):
        params_as_string = str(json.dumps(params))
        return params_as_string

    def __params_to_path(self, params):
        entries = params.items()
        if not entries:
            pass

        paramsString = "&".join("{key}={value}".format(key=x[0], value=x[1]) for x in entries if x[1] is not None)
        if paramsString:
            return paramsString

    def __genSignature(self, time_stamp, paras_as_string):
        param_str = time_stamp + self.api_key + "5000" + paras_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def __set_exchange_settings(self):
        self.__set_fee_pcts()
        self.__set_mmr_pct()
        self.__set_min_max_leverage_and_coin_size()
        self.exchange_settings = ExchangeSettings(
            market_fee_pct=self.market_fee_pct,
            limit_fee_pct=self.limit_fee_pct,
            mmr_pct=self.mmr_pct,
            max_leverage=self.max_leverage,
            min_leverage=self.min_leverage,
            max_coin_size_value=self.max_coin_size_value,
            min_coin_size_value=self.min_coin_size_value,
        )

    def __set_fee_pcts(self):
        end_point = "/private/v1/account/trade-fee"
        params = {
            "symbol": self.symbol,
        }
        try:
            trading_fees = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"][0]
            self.market_fee_pct = float(trading_fees["takerFeeRate"])
            self.limit_fee_pct = float(trading_fees["makerFeeRate"])
        except KeyError as e:
            raise KeyError(f"Something is wrong setting fee pct {e}")

    def __set_mmr_pct(self):
        end_point = "/public/v1/position-risk"
        params = {
            "category": self.category,
            "symbol": self.symbol,
        }
        try:
            mmr_pct = self.__HTTP_get_request(end_point=end_point, params=params)
            self.mmr_pct = mmr_pct["data"]["list"][0]["maintainMargin"]
        except KeyError as e:
            raise KeyError(f"Something is wrong setting mmr pct {e}")

    def __set_min_max_leverage_and_coin_size(self):
        end_point = "/public/v1/instruments"
        params = {
            "category": self.category,
            "symbol": self.symbol,
        }
        try:
            symbol_info_og = self.__HTTP_get_request(end_point=end_point, params=params)
            symbol_info = symbol_info_og["data"]["list"][0]
            self.max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
            self.min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
            self.max_coin_size_value = float(symbol_info["lotSizeFilter"]["maxTradingQty"])
            self.min_coin_size_value = float(symbol_info["lotSizeFilter"]["minTradingQty"])

        except KeyError as e:
            raise KeyError(f"Something is wrong setting min max leveage coin size {e}")

    def __set_position_mode(self, position_mode):
        # https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": self.symbol,
            "mode": position_mode,
        }

        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"Something is wrong setting postiion mode {e}")
