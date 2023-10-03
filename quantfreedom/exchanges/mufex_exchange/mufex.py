import json
import logging
import hashlib
import hmac
from uuid import uuid4

from requests import get, post
from time import sleep, time

from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    LongOrShortType,
    PositionModeType,
)
from quantfreedom.exchanges.base.exchange import Exchange
from quantfreedom.exchanges.base.live_exchange import UNIVERSAL_TIMEFRAMES

MUFEX_TIMEFRAMES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 10080, 43800]


class Mufex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        symbol: str,
        timeframe: str,
        api_key: str,
        secret_key: str,
        long_or_short: LongOrShortType,
        candles_to_dl: int = None,
        keep_volume_in_candles: bool = False,
        use_test_net: bool = False,
        position_mode: PositionModeType = PositionModeType.HedgeMode,
        leverage_mode: LeverageModeType = LeverageModeType.Isolated,
        # Mufex Vars
        category: str = "linear",
    ):
        """
        main docs page https://www.mufex.finance/apidocs/derivatives/contract/index.html

        Make sure you have your position mode set to hedge or else a lot of functions will not work.
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        super().__init__(
            symbol,
            timeframe,
            api_key,
            secret_key,
            long_or_short,
            position_mode,
            leverage_mode,
            candles_to_dl,
            keep_volume_in_candles,
            use_test_net,
        )
        timeframe = MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        self.category = category

        if not use_test_net:
            self.url_start = "https://api.mufex.finance"
        else:
            self.url_start = "https://api.testnet.mufex.finance"

        if keep_volume_in_candles:
            self.volume_yes_no = -1
        else:
            self.volume_yes_no = -2

        if long_or_short == LongOrShortType.Long:
            self.side_num = 0
        else:
            self.side_num = 1

        if position_mode == PositionModeType.HedgeMode:
            self.position_mode = 3
            self.__set_position_mode_as_hedge_mode()
        else:
            self.__set_position_mode_as_one_way_mode()

        if leverage_mode == LeverageModeType.Isolated:
            self.__set_leverage_mode_isolated()
        elif leverage_mode == LeverageModeType.Cross:
            self.__set_leverage_mode_cross()

        self.__set_exchange_settings()

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

    def __HTTP_post_request(self, end_point, params):
        time_stamp = str(int(time() * 1000))
        params_as_string = self.__params_as_string(params=params)
        signature = self.__gen_signature(time_stamp=time_stamp, params_as_string=params_as_string)
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
        except KeyError as e:
            raise KeyError(f"{e}")
        return response_json

    def __HTTP_post_request_no_params(self, end_point):
        time_stamp = str(int(time() * 1000))
        signature = self.__gen_signature_no_params(time_stamp=time_stamp)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }
        response = post(url=self.url_start + end_point, headers=headers)
        try:
            response_json = response.json()
        except KeyError as e:
            raise KeyError(f"{e}")
        return response_json

    def __HTTP_get_request(
        self,
        end_point,
        params,
    ):
        time_stamp = str(int(time() * 1000))
        params_as_path = self.__params_to_path(params=params)
        signature = self.__gen_signature(time_stamp=time_stamp, params_as_string=params_as_path)
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
        except KeyError as e:
            raise KeyError(f"{e}")
        return response_json

    def __HTTP_get_request_no_params(self, end_point):
        time_stamp = str(int(time() * 1000))
        signature = self.__gen_signature_no_params(time_stamp=time_stamp)
        headers = {
            "MF-ACCESS-API-KEY": self.api_key,
            "MF-ACCESS-SIGN": signature,
            "MF-ACCESS-SIGN-TYPE": "2",
            "MF-ACCESS-TIMESTAMP": time_stamp,
            "MF-ACCESS-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }

        response = get(
            url=self.url_start + end_point,
            headers=headers,
        )
        try:
            response_json = response.json()
        except KeyError as e:
            raise KeyError(f"{e}")
        return response_json

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

    def __gen_signature(self, time_stamp, params_as_string):
        param_str = time_stamp + self.api_key + "5000" + params_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def __gen_signature_no_params(self, time_stamp):
        param_str = time_stamp + self.api_key + "5000"
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

    def get_order_history(self, symbol: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder
        """
        end_point = "/private/v1/trade/orders"
        params = {
            "symbol": symbol,
        }
        try:
            order_info_list = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"]
            if order_info_list:
                return order_info_list
            else:
                KeyError("Nothing sent back in the list")
        except KeyError as e:
            raise KeyError(f"Something is wrong with get_symbol_order_history -> {e}")

    def get_order_id_info(self, symbol: str, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder
        """
        end_point = "/private/v1/trade/orders"
        params = {
            "symbol": symbol,
            "orderId": order_id,
        }
        try:
            order_info_list = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"][0]
            if order_info_list:
                return order_info_list
            else:
                KeyError("Nothing sent back in the list")
        except KeyError as e:
            raise KeyError(f"Something is wrong with get_order_id_info -> {e}")

    def get_and_set_candles_df(
        self,
        symbol: str,
        timeframe: [int, str],
        since_date_ms: int = None,
        until_date_ms: int = None,
        **vargs,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline

        timeframe: 1 3 5 15 30 60 120 240 360 720 "D" "M" "W"

        returning dict is [start, open, high, low, close, volume, turnover]
        """

        if until_date_ms is None:
            until_date_ms = self.__get_current_pd_datetime() - timeframe_in_ms

        if since_date_ms is None:
            since_date_ms = until_date_ms - timeframe_in_ms - self.candles_to_dl_in_ms

        self.candles_list = []
        end_point = "/public/v1/market/kline"
        params = {
            "category": self.category,
            "symbol": symbol,
            "interval": timeframe,
            "start": since_date_ms,
            "end": until_date_ms,
        }
        while params["start"] < until_date_ms:
            try:
                new_candles_og = self.__HTTP_get_request(end_point=end_point, params=params)
                candles = new_candles_og["data"]["list"]
                if not candles:
                    break
                last_candle_time_ms = int(candles[-1][0])
                if last_candle_time_ms == self.last_fetched_ms_time:
                    logging.info(
                        f"\nLast candle {self.__convert_to_pd_datetime(last_candle_time_ms)} == last fetched time {self.last_fetched_time_to_pd_datetime()}. Trying again in .2 seconds"
                    )
                    sleep(0.2)
                else:
                    self.candles_list.extend(candles)
                    params["start"] = last_candle_time_ms + 1000
                    self.last_fetched_ms_time = last_candle_time_ms

            except Exception as e:
                raise Exception(f"{e}")
        return self.__candles_list_to_pd()

    def get_and_set_init_last_fetched_time(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline
        The default collation within the array is start, open, high, low, close, volume, turnover
        """
        init_end = self.get_ms_current_time() - timeframe_in_ms
        init_start = init_end - timeframe_in_ms

        end_point = "/public/v1/market/kline"
        params = {
            "category": self.category,
            "symbol": symbol,
            "interval": timeframe,
            "start": init_start,
            "end": init_end,
        }
        try:
            self.last_fetched_ms_time = int(
                self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"][-1][0]
            )
            return self.last_fetched_ms_time
        except KeyError as e:
            raise KeyError(f"Somethinig is wrong with get_and_set_init_last_fetched_time -< {e}")

    def get_position_info_current_symbol_and_long_or_short(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            order_info = data_order_info["data"]["list"][self.side_num]
            if order_info:
                return order_info
            else:
                raise KeyError("Returned an empty list")

        except KeyError as e:
            raise KeyError(f"Something is wrong with get_position_info_current_symbol_and_long_or_short {e}")

    def get_position_info(self, symbol: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            order_info = data_order_info["data"]["list"]
            if order_info:
                return order_info
            else:
                raise KeyError("Returned an empty list")

        except KeyError as e:
            raise KeyError(f"Something is wrong with get_position_info {e}")

    def get_position_info_current_symbol(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {
            "symbol": symbol,
        }
        try:
            data_order_info = self.__HTTP_get_request(end_point=end_point, params=params)
            order_info = data_order_info["data"]["list"]
            if order_info:
                return order_info
            else:
                raise KeyError("Returned an empty list")

        except KeyError as e:
            raise KeyError(f"Something is wrong with get_position_info {e}")

    def check_if_current_symbol_in_position(self, **vargs):
        if float(self.get_order_history_current_symbol()["entryPrice"]) > 0:
            return True
        else:
            return False

    def check_if_current_symbol_order_filled(self, order_id: str, **vargs):
        if self.get_order_history_current_symbol_order_id(order_id=order_id)["orderStatus"] == "Filled":
            return True
        else:
            return False

    def check_if_current_symbol_order_canceled(self, order_id: str, **vargs):
        if self.get_order_history_current_symbol_order_id(order_id=order_id)["orderStatus"] in [
            "Cancelled",
            "Deactivated",
        ]:
            return True
        else:
            return False

    def check_if_current_symbol_order_active(self, order_id: str, **vargs):
        if self.get_order_history_current_symbol_order_id(order_id=order_id)["orderStatus"] in ["New", "Untriggered"]:
            return True
        else:
            return False

    def cancel_order(self, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_cancelorder
        """
        end_point = "/private/v1/trade/cancel"
        params = {
            "symbol": symbol,
            "orderId": order_id,
        }
        try:
            data_orderId = self.__HTTP_post_request(end_point=end_point, params=params)["data"]["orderId"]
            if data_orderId == order_id:
                return True
            else:
                return False
        except KeyError as e:
            raise KeyError(f"Something is wrong cancel order {e}")

    def adjust_order(self, order_id: str, new_price: float, asset_amount: float = None, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder
        """
        end_point = "/private/v1/trade/replace"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "price": str(new_price),
            "qty": str(asset_amount),
        }

        try:
            data = self.__HTTP_post_request(end_point=end_point, params=params)
            if data["message"] == "OK":
                return True
            else:
                raise KeyError(f"{data['message']}")
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the limit entry order {e}")

    def move_order(self, order_id: str, new_price: float, asset_amount: float = None, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder
        """
        end_point = "/private/v1/trade/replace"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "price": str(new_price),
            "qty": str(asset_amount),
        }

        try:
            data = self.__HTTP_post_request(end_point=end_point, params=params)
            if data["message"] == "OK":
                return True
            else:
                raise KeyError(f"{data['message']}")
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the limit entry order {e}")

    def create_order(self, params: dict, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        end_point = "/private/v1/trade/create"

        try:
            order_info = self.__HTTP_post_request(end_point=end_point, params=params)["data"]
            orderId = order_info["orderId"]
            # orderLinkId = order_info["orderLinkId"]
        except KeyError as e:
            raise KeyError(f"Something is wrong setting the limit entry order {e}")
        # return orderId, orderLinkId
        return orderId

    def create_long_entry_market_order(self, asset_amount: float, time_in_force: str = "ImmediateOrCancel", **vargs):
        params = {
            "symbol": symbol,
            "positionIdx": 1,
            "side": "Buy",
            "orderType": "Market",
            "qty": str(asset_amount),
            "timeInForce": time_in_force,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_long_entry_limit_order(
        self, asset_amount: float, entry_price: float, time_in_force: str = "PostOnly", **vargs
    ):
        params = {
            "symbol": symbol,
            "positionIdx": 1,
            "side": "Buy",
            "orderType": "Limit",
            "qty": str(asset_amount),
            "price": str(entry_price),
            "timeInForce": time_in_force,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_long_tp_market_order(self, asset_amount: float, time_in_force: str = "ImmediateOrCancel", **vargs):
        params = {
            "symbol": symbol,
            "positionIdx": 1,
            "side": "Sell",
            "orderType": "Market",
            "qty": str(asset_amount),
            "timeInForce": time_in_force,
            "reduceOnly": True,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_long_tp_limit_order(
        self, asset_amount: float, tp_price: float, time_in_force: str = "PostOnly", **vargs
    ):
        params = {
            "symbol": symbol,
            "side": "Sell",
            "positionIdx": 1,
            "orderType": "Limit",
            "qty": str(asset_amount),
            "price": str(tp_price),
            "timeInForce": time_in_force,
            "reduceOnly": True,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_long_sl_order(
        self, asset_amount: float, trigger_price: float, time_in_force: str = "ImmediateOrCancel", **vargs
    ):
        params = {
            "symbol": symbol,
            "side": "Sell",
            "positionIdx": 1,
            "orderType": "Market",
            "qty": str(asset_amount),
            "timeInForce": time_in_force,
            "reduceOnly": True,
            "triggerPrice": str(trigger_price),
            "triggerDirection": 2,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_short_entry_market_order(self, asset_amount: float, time_in_force: str = "ImmediateOrCancel", **vargs):
        params = {
            "symbol": symbol,
            "positionIdx": 2,
            "side": "Buy",
            "orderType": "Market",
            "qty": str(asset_amount),
            "timeInForce": time_in_force,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_short_entry_limit_order(
        self, asset_amount: float, entry_price: float, time_in_force: str = "PostOnly", **vargs
    ):
        params = {
            "symbol": symbol,
            "positionIdx": 2,
            "side": "Buy",
            "orderType": "Limit",
            "qty": str(asset_amount),
            "price": str(entry_price),
            "timeInForce": time_in_force,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_short_tp_market_order(self, asset_amount: float, time_in_force: str = "ImmediateOrCancel", **vargs):
        params = {
            "symbol": symbol,
            "positionIdx": 2,
            "side": "Buy",
            "orderType": "Market",
            "qty": str(asset_amount),
            "timeInForce": time_in_force,
            "reduceOnly": True,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_short_tp_limit_order(
        self, asset_amount: float, tp_price: float, time_in_force: str = "PostOnly", **vargs
    ):
        params = {
            "symbol": symbol,
            "side": "Buy",
            "positionIdx": 2,
            "orderType": "Limit",
            "qty": str(asset_amount),
            "price": str(tp_price),
            "timeInForce": time_in_force,
            "reduceOnly": True,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def create_short_sl_order(
        self, asset_amount: float, trigger_price: float, time_in_force: str = "ImmediateOrCancel", **vargs
    ):
        params = {
            "symbol": symbol,
            "side": "Buy",
            "positionIdx": 2,
            "orderType": "Market",
            "qty": str(asset_amount),
            "timeInForce": time_in_force,
            "reduceOnly": True,
            "triggerPrice": str(trigger_price),
            "triggerDirection": 1,
            "orderLinkId": uuid4().hex,
        }
        return self.create_order(params=params)

    def get_symbol_info(self, symbol: str = None, category: str = "linear", limit: int = 1000, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_instrhead
        """
        end_point = "/public/v1/instruments"
        params = {
            "category": category,
            "symbol": symbol,
            "limit": limit,
        }
        try:
            symbol_info = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"]
        except KeyError as e:
            raise KeyError(f"Something is wrong getting symbol_info {e}")

        return symbol_info

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

    def get_wallet_info_all_coins(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        end_point = "/private/v1/account/balance"
        params = {}
        try:
            coin_info = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"]
            if coin_info:
                return coin_info
            else:
                raise KeyError("Nothing sent back in the list for get_wallet_info")
        except KeyError as e:
            raise KeyError(f"Something is wrong get_wallet_info {e}")

    def get_usdt_wallet_info(self):
        return self.get_wallet_info(asset="USDT")

    def get_all_symbols_trading_fee_info(self, symbol: str = None):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        end_point = "/private/v1/account/trade-fee"
        params = {
            "symbol": symbol,
        }
        try:
            trading_fee_info = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"]
            if trading_fee_info:
                return trading_fee_info
            else:
                raise KeyError("Nothing sent back in the list for get_trading_fee_info")
        except KeyError as e:
            raise KeyError(f"Something is wrong -> {e}")

    def __set_fee_pcts(self):
        trading_fee_info = self.get_trading_fee_info()
        self.market_fee_pct = float(trading_fee_info["takerFeeRate"])
        self.limit_fee_pct = float(trading_fee_info["makerFeeRate"])

    def get_risk_limit_info(self):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_risklimithead
        """
        end_point = "/public/v1/position-risk"
        params = {
            "category": self.category,
            "symbol": symbol,
        }
        try:
            risk_limit_info = self.__HTTP_get_request(end_point=end_point, params=params)["data"]["list"][0]
            if risk_limit_info:
                return risk_limit_info
            else:
                raise KeyError("Nothing sent back in the list for get_risk_limit_info")
        except KeyError as e:
            raise KeyError(f"Something is wrong setting mmr pct {e}")

    def __set_mmr_pct(self):
        risk_limit_info = self.get_risk_limit_info()
        self.mmr_pct = risk_limit_info["maintainMargin"]

    def __set_min_max_leverage_and_coin_size(self):
        symbol_info = self.get_symbol_info(symbol=symbol)
        self.max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
        self.min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
        self.max_coin_size_value = float(symbol_info["lotSizeFilter"]["maxTradingQty"])
        self.min_asset_qty = float(symbol_info["lotSizeFilter"]["minTradingQty"])

    def set_position_mode(self, position_mode: int, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": symbol,
            "mode": position_mode,
        }
        try:
            message = self.__HTTP_post_request(end_point=end_point, params=params)["message"]
            if message not in ["OK", "position mode not modified"]:
                raise KeyError("Something is wrong with setting the position mode")
        except KeyError as e:
            raise KeyError(f"Something is wrong setting postiion mode {e}")

    def __set_position_mode_as_hedge_mode(self):
        self.set_position_mode(position_mode=3)

    def __set_position_mode_as_one_way_mode(self):
        self.set_position_mode(position_mode=0)

    def set_leverage_value(self, leverage: float, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        """
        end_point = "/private/v1/account/set-leverage"
        leverage_str = str(leverage)
        params = {
            "symbol": symbol,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            self.__HTTP_post_request(end_point=end_point, params=params)
        except KeyError as e:
            raise KeyError(f"Something is wrong set_leverage {e}")

    def set_leverage_mode(self, tradeMode: int, leverage: int = 5, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        end_point = "/private/v1/account/set-isolated"
        leverage_str = str(leverage)
        params = {
            "symbol": symbol,
            "tradeMode": tradeMode,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            message = self.__HTTP_post_request(end_point=end_point, params=params)["message"]
            if message not in ["OK", "Isolated not modified"]:
                raise KeyError("Something is wrong with setting the position mode")
        except KeyError as e:
            raise KeyError(f"More than likely lev mode already set {e}")

    def __set_leverage_mode_isolated(self):
        self.set_leverage_mode(tradeMode=1)

    def __set_leverage_mode_cross(self):
        self.set_leverage_mode(tradeMode=0)
