import json
import logging
import hashlib
import hmac

import pandas as pd
import numpy as np

from datetime import datetime
from requests import get, post
from time import sleep, time

from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionIdxType,
    PositionModeType,
    TriggerDirectionType,
)
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

MUFEX_TIMEFRAMES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]


def __init__(
    self,
    category: str = "linear",
):
    """
    Make sure you have your position mode set to hedge or else a lot of functions will not work.
    https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
    """
    self.timeframe = MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(self.timeframe)]
    self.side = self.side.capitalize()
    self.category = category

    if not self.use_test_net:
        self.url_start = "https://api.mufex.finance"
    else:
        self.url_start = "https://api.testnet.mufex.finance"

    if self.position_mode == PositionModeType.HedgeMode:
        self.position_mode = 3

    if self.keep_volume_in_candles:
        self.volume_yes_no = -1
    else:
        self.volume_yes_no = -2

    if self.side == "Buy":
        self.side_num = 0
    else:
        self.side_num = 1

    self.__set_exchange_settings()


class Mufex(Exchange):
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        api_key: str,
        secret_key: str,
        side: str,
        position_mode: PositionModeType,
        leverage_mode: LeverageModeType,
        candles_to_dl: int = None,
        keep_volume_in_candles: bool = False,
        use_test_net: bool = False,
        category: str = "linear",
    ):
        """
        Make sure you have your position mode set to hedge or else a lot of functions will not work.
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        super().__init__(
            symbol,
            timeframe,
            api_key,
            secret_key,
            side,
            position_mode,
            leverage_mode,
            candles_to_dl,
            keep_volume_in_candles,
            use_test_net,
        )
        self.timeframe = MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(self.timeframe)]
        self.side = self.side.capitalize()
        self.category = category

        if not self.use_test_net:
            self.url_start = "https://api.mufex.finance"
        else:
            self.url_start = "https://api.testnet.mufex.finance"

        if self.keep_volume_in_candles:
            self.volume_yes_no = -1
        else:
            self.volume_yes_no = -2

        if self.side == "Buy":
            self.side_num = 0
        else:
            self.side_num = 1

        if self.position_mode == PositionModeType.HedgeMode:
            self.position_mode = 3
        
        if leverage_mode == LeverageModeType.Isolated:
            self.__set_leverage_mode_isolated()
        elif leverage_mode == LeverageModeType.Cross:
            self.__set_leverage_mode_cross()

        self.__set_exchange_settings()

    def get_and_set_candles_df(
        self,
        since_date_ms: int = None,
        until_date_ms: int = None,
    ):
        if until_date_ms is None:
            until_date_ms = self.__get_current_pd_datetime() - self.timeframe_in_ms

        if since_date_ms is None:
            since_date_ms = until_date_ms - self.timeframe_in_ms - self.candles_to_dl_in_ms

        self.candles_list = []
        end_point = "/public/v1/market/kline"
        params = {
            "category": self.category,
            "symbol": self.symbol,
            "interval": self.timeframe,
            "start": since_date_ms,
            "end": until_date_ms,
        }
        start_time = self.__get_current_time_seconds()
        while params["start"] < until_date_ms:
            try:
                new_candles_og = self.__HTTP_get_request(end_point=end_point, params=params)
                candles = new_candles_og["data"]["list"]
                if not candles:
                    break
                last_candle_time_ms = int(candles[-1][0])
                if last_candle_time_ms == self.last_fetched_ms_time:
                    logging.info(
                        f"\nLast candle {self.__convert_to_pd_datetime(last_candle_time_ms)} == last fetched time {self.__last_fetched_time_to_pd_datetime()}. Trying again in .2 seconds"
                    )
                    sleep(0.2)
                else:
                    self.candles_list.extend(candles)
                    params["start"] = last_candle_time_ms + 1000
                    self.last_fetched_ms_time = last_candle_time_ms

            except Exception as e:
                logging.error(e)

        logging.info(f"Got {len(self.candles_list)} new candles.")

        logging.info(
            f"It took {round((self.__get_current_time_seconds() - start_time),4)} seconds to create the candles\n"
        )
        return self.__candles_list_to_pd()

    def __set_init_last_fetched_time(self):
        logging.info("Starting execution for user")
        init_end = self.__get_ms_current_time() - self.timeframe_in_ms
        init_start = init_end - self.timeframe_in_ms

        end_point = "/public/v1/market/kline"
        params = {
            "category": self.category,
            "symbol": self.symbol,
            "interval": self.timeframe,
            "start": init_start,
            "end": init_end,
        }
        try:
            self.last_fetched_ms_time = int(
                self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"][-1][0]
            )
        except KeyError as e:
            logging.error(f"Somethinig is wrong with __set_init_last_fetched_time -< {e}")

    def __HTTP_post_request(self, end_point, params):
        time_stamp = str(int(time() * 1000))
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
        time_stamp = str(int(time() * 1000))
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

    def get_position_info(self):
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
            order_info_og = data_order_info["data"]["list"][self.side_num]
            if float(order_info_og["entryPrice"]) > 0:
                return order_info_og
            else:
                raise KeyError("Looks like we aren't in a buy posiiton.")

        except KeyError as e:
            raise KeyError(f"Something is wrong with get_buy_position_info {e}")

    def check_if_in_position(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": self.symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            order_info_og = data_order_info["data"]["list"][self.side_num]
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
            max_asset_qty=self.max_coin_size_value,
            min_asset_qty=self.min_asset_qty,
            position_mode=self.position_mode,
            leverage_mode=self.leverage_mode,
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
            self.min_asset_qty = float(symbol_info["lotSizeFilter"]["minTradingQty"])

        except KeyError as e:
            raise KeyError(f"Something is wrong setting min max leveage coin size {e}")

    def set_position_mode(self, position_mode: int):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        Position mode. 0: One-Way mode. 3: Hedge mode
        """
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": self.symbol,
            "mode": position_mode,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"Something is wrong setting postiion mode {e}")

    def __set_position_as_hedge_mode(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        Position mode. 0: One-Way mode. 3: Hedge mode
        """
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": self.symbol,
            "mode": 3,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"Something is wrong setting postiion mode {e}")

    def __set_position_as_one_way_mode(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        Position mode. 0: One-Way mode. 3: Hedge mode
        """
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": self.symbol,
            "mode": 0,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"Something is wrong setting postiion mode {e}")

    def set_leverage_value(self, leverage: float):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        """
        end_point = "/private/v1/account/set-leverage"
        leverage_str = str(leverage)
        params = {
            "symbol": self.symbol,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"Something is wrong set_leverage {e}")

    def set_leverage_mode(self, tradeMode: int, leverage: int = 5):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        end_point = "/private/v1/account/set-isolated"
        leverage_str = str(leverage)
        params = {
            "symbol": self.symbol,
            "tradeMode": tradeMode,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"More than likely lev mode already set {e}")

    def __set_leverage_mode_isolated(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        end_point = "/private/v1/account/set-isolated"
        leverage_str = "5"
        params = {
            "symbol": self.symbol,
            "tradeMode": 1,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"More than likely isolated lev mode already set {e}")

    def __set_leverage_mode_cross(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        end_point = "/private/v1/account/set-isolated"
        leverage_str = "5"
        params = {
            "symbol": self.symbol,
            "tradeMode": 0,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"More than likely cross lev mode already set {e}")
