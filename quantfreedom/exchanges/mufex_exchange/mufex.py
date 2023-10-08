from datetime import timedelta
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
    PositionModeType,
)
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

MUFEX_TIMEFRAMES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]

info_logger = logging.getLogger("info")


class Mufex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        api_key: str,
        secret_key: str,
        use_test_net: bool = False,
    ):
        """
        main docs page https://www.mufex.finance/apidocs/derivatives/contract/index.html

        Make sure you have your position mode set to hedge or else a lot of functions will not work.
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        super().__init__(api_key, secret_key, use_test_net)

        if not use_test_net:
            self.url_start = "https://api.mufex.finance"
        else:
            self.url_start = "https://api.testnet.mufex.finance"

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
        info_logger.debug("")
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

        try:
            response = post(
                url=self.url_start + end_point,
                headers=headers,
                data=params_as_string,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Mufex Something wrong with __HTTP_post_request - > {e}")

    def __HTTP_post_request_no_params(self, end_point):
        info_logger.debug("")
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
        try:
            response = post(url=self.url_start + end_point, headers=headers)
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Mufex Something wrong with __HTTP_post_request_no_params - > {e}")

    def HTTP_get_request(self, end_point, params):
        info_logger.debug("")
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

        try:
            response = get(
                url=self.url_start + end_point + "?" + params_as_path,
                headers=headers,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Mufex Something wrong with HTTP_get_request - > {e}")

    def HTTP_get_request_no_params(self, end_point):
        info_logger.debug("")
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

        try:
            response = get(
                url=self.url_start + end_point,
                headers=headers,
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            raise Exception(f"Mufex Something wrong with HTTP_get_request_no_params - > {e}")

    def __params_as_string(self, params):
        info_logger.debug("")
        params_as_string = str(json.dumps(params))
        return params_as_string

    def __params_to_path(self, params):
        info_logger.debug("")
        entries = params.items()
        if not entries:
            pass

        paramsString = "&".join("{key}={value}".format(key=x[0], value=x[1]) for x in entries if x[1] is not None)
        if paramsString:
            return paramsString

    def __gen_signature(self, time_stamp, params_as_string):
        info_logger.debug("")
        param_str = time_stamp + self.api_key + "5000" + params_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def __gen_signature_no_params(self, time_stamp):
        info_logger.debug("")
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

    def get_candles_df(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = None,
        category: str = "linear",
        limit: int = 200,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline

        timeframe: 1 3 5 15 30 60 120 240 360 720 "D" "M" "W"

        returning dict is [start, open, high, low, close, volume, turnover]

        use link to see all Request Parameters
        """
        info_logger.debug("")
        mufex_timeframe = self.__get_mufex_timeframe(timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = self.get_candles_to_dl_in_ms(candles_to_dl, timeframe_in_ms=timeframe_in_ms, limit=200)

        if until_date_ms is None:
            until_date_ms = self.get_current_time_ms() - timeframe_in_ms

        if since_date_ms is None:
            since_date_ms = until_date_ms - candles_to_dl_ms

        candles_list = []
        end_point = "/public/v1/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": mufex_timeframe,
            "start": since_date_ms,
            "end": until_date_ms,
            "limit": limit,
        }
        start_time = self.get_current_time_seconds()
        while params["start"] + timeframe_in_ms < until_date_ms:
            response = self.HTTP_get_request(end_point=end_point, params=params)
            try:
                new_candles = response["data"]["list"]
                last_candle_time_ms = int(new_candles[-1][0])
                if last_candle_time_ms == params["start"]:
                    sleep(0.2)
                else:
                    candles_list.extend(new_candles)
                    # add one sec so we don't download the same candle two times
                    params["start"] = last_candle_time_ms + 1000
            except Exception as e:
                raise Exception(f"Mufex Something is wrong with get_candles_df {response.get('message')} - > {e}")
        time_it_took_in_seconds = self.get_current_time_seconds() - start_time
        td = str(timedelta(seconds=time_it_took_in_seconds)).split(":")
        print(f"It took {td[1]} mins and {td[2]} seconds to download the candles")
        return self.get_candles_list_to_pd(candles_list=candles_list, col_end=-2)

    def get_all_symbols_info(self, category: str = "linear", limit: int = 1000, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_instrhead

        Paramaters:
        symbol
        """
        info_logger.debug("")
        end_point = "/public/v1/instruments"
        params["limit"] = limit
        params["category"] = category
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_all_symbols_info = Data or List is empty {response['message']} -> {e}")

    def get_symbol_info(self, symbol: str, **vargs):
        info_logger.debug("")
        return self.get_all_symbols_info(params={"symbol": symbol})[0]

    def get_risk_limit_info(self, symbol: str, category: str = "linear", **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_risklimithead
        """
        info_logger.debug("")
        end_point = "/public/v1/position-risk"
        params = {}
        params["category"] = category
        params["symbol"] = symbol
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_risk_limit_info = Data or List is empty {response['message']} -> {e}")

    def create_order(self, params: dict, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        use this website to see all the params
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/create"
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            order_id = response["data"]["orderId"]
            return order_id
        except Exception as e:
            raise Exception(f"Mufex Something is wrong with create_order {response['message']} -> {e}")

    def get_trading_fee_rates(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        info_logger.debug("")
        end_point = "/private/v1/account/trade-fee"
        response = self.HTTP_get_request_no_params(end_point=end_point)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_trading_fee_rates = Data or List is empty {response['message']} -> {e}")

    def get_symbol_trading_fee_rates(self, symbol: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        info_logger.debug("")
        end_point = "/private/v1/account/trade-fee"
        params = {}
        params["symbol"] = symbol
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_symbol_trading_fee_rates = Data or List is empty {response['message']} -> {e}")

    def get_order_history(self, symbol: str, limit: int = 50, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder

        use link to see all Request Parameters
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/orders"
        params["symbol"] = symbol
        params["limit"] = limit
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_order_history = Data or List is empty {response['message']} -> {e}")

    def get_order_history_by_order_id(self, symbol: str, order_id: str, params: dict = {}, **vargs):
        info_logger.debug("")
        params["orderId"] = order_id
        return self.get_order_history(symbol=symbol, params=params)[0]

    def get_open_orders(self, symbol: str, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getopenorder

        Query real-time order information. If only orderId or orderLinkId are passed, a single order will be returned; otherwise, returns up to 500 unfilled orders

        orderId
        limit
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/activity-orders"
        params["symbol"] = symbol
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_open_orders = Data or List is empty {response['message']} -> {e}")

    def get_open_order_by_order_id(self, symbol: str, order_id: str, params: dict = {}, **vargs):
        info_logger.debug("")
        params["orderId"] = order_id
        return self.get_open_orders(symbol=symbol, params=params)[0]

    def get_filled_orders(self, symbol: str, limit: int = 200, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-usertraderecords

        Get user's trading records. The results are ordered in descending order (the first item is the latest). Returns records up to 2 years old.

        use link to see all Request Parameters
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/fills"
        params["symbol"] = symbol
        params["limit"] = limit
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_filled_orders = Data or List is empty {response['message']} -> {e}")

    def get_filled_orders_by_order_id(self, symbol: str, order_id: str, params: dict = {}, **vargs):
        info_logger.debug("")
        params["orderId"] = order_id
        return self.get_filled_orders(symbol=symbol, params=params)[0]

    def get_account_position_info(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        info_logger.debug("")
        end_point = "/private/v1/account/positions"
        response = self.HTTP_get_request_no_params(end_point=end_point)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_account_position_info = Data or List is empty {response['message']} -> {e}")

    def get_symbol_position_info(self, symbol: str, limit: int = 20, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        info_logger.debug("")
        end_point = "/private/v1/account/positions"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_symbol_position_info = Data or List is empty {response['message']} -> {e}")

    def cancel_open_order(self, symbol: str, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_cancelorder
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/cancel"
        params = {
            "symbol": symbol,
            "orderId": order_id,
        }
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            return response_order_id == order_id or response["message"] == "OK"
        except Exception as e:
            raise Exception(f"Mufex cancel_open_order message = {response['message']} -> {e}")

    def cancel_all_open_order_per_symbol(self, symbol: str, **vargs):
        """
        no link yet
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/cancel-all"
        params = {
            "symbol": symbol,
        }
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            return response["message"] == "OK"
        except Exception as e:
            raise Exception(f"Mufex cancel_open_order message = {response['message']} -> {e}")

    def adjust_order(self, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder

        you basically have to use the same info that you would for create order
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/replace"
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            response_order_id = response.get("data").get("orderId")
            if response_order_id == params["orderId"] or response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex adjust_order message = {response['message']} -> {e}")

    def move_limit_order(self, symbol: str, order_id: str, new_price: float, asset_amount: float, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/replace"
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        params["qty"] = str(asset_amount)
        params["price"] = str(new_price)
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            response_order_id = response.get("data").get("orderId")
            if response_order_id == params["orderId"] or response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex move_limit_order message = {response['message']} -> {e}")

    def move_stop_order(self, symbol: str, order_id: str, new_price: float, asset_amount: float, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder

        """
        info_logger.debug("")
        end_point = "/private/v1/trade/replace"
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        params["qty"] = str(asset_amount)
        params["triggerPrice"] = str(new_price)
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            response_order_id = response.get("data").get("orderId")
            if response_order_id == params["orderId"] or response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex move_stop_order message = {response['message']} -> {e}")

    def get_wallet_info(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        info_logger.debug("")
        end_point = "/private/v1/account/balance"
        response = self.HTTP_get_request_no_params(end_point=end_point)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_wallet_info = Data or List is empty {response['message']} -> {e}")

    def get_wallet_info_of_asset(self, trading_in: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        info_logger.debug("")
        end_point = "/private/v1/account/balance"
        params = {"coin": trading_in}
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_wallet_info_of_asset = Data or List is empty {response['message']} -> {e}")

    def get_equity_of_asset(self, trading_in: str, **vargs):
        info_logger.debug("")
        try:
            return float(self.get_wallet_info_of_asset(trading_in=trading_in)["equity"])
        except Exception as e:
            raise Exception(f"Mufex Something is wrong with get_equity_of_asset -> {e}")

    def set_position_mode(self, symbol: str, position_mode: PositionModeType, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        info_logger.debug("")
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": symbol,
            "mode": 3 if position_mode == PositionModeType.HedgeMode else 0,
        }
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "position mode not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_position_mode = Data or List is empty {response['message']} -> {e}")

    def set_leverage_value(self, symbol: str, leverage: float, **vargs):
        """
        No link yet
        """
        info_logger.debug("")
        end_point = "/private/v1/account/set-leverage"
        leverage_str = str(leverage)
        params = {
            "symbol": symbol,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "leverage not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_leverage_value = Data or List is empty {response['message']} -> {e}")

    def set_leverage_mode(self, symbol: str, leverage_mode: LeverageModeType, leverage: int = 5, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        info_logger.debug("")
        end_point = "/private/v1/account/set-isolated"
        leverage_str = str(leverage)
        params = {
            "symbol": symbol,
            "tradeMode": leverage_mode,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "Isolated not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_leverage_mode = Data or List is empty {response['message']} -> {e}")

    def check_if_order_filled(self, symbol: str, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-usertraderecords

        Get user's trading records. The results are ordered in descending order (the first item is the latest). Returns records up to 2 years old.

        use link to see all Request Parameters
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/fills"
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            if response["message"] == "OK":
                return True
            else:
                data_list = response.get("data").get("list")
                if data_list:
                    return data_list[0]["orderId"]
        except Exception as e:
            raise Exception(f"Mufex check_if_order_filled = Something wrong {response['message']} -> {e}")

    def check_if_order_canceled(self, symbol: str, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder

        use link to see all Request Parameters
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/orders"
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            if response["message"] == "OK":
                return True
            else:
                data_list = response.get("data").get("list")
                if data_list:
                    return data_list[0]["orderId"]
        except Exception as e:
            raise Exception(f"Mufex check_if_order_canceled = Something wrong {response['message']} -> {e}")

    def check_if_order_open(self, symbol: str, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getopenorder

        use link to see all Request Parameters
        """
        info_logger.debug("")
        end_point = "/private/v1/trade/activity-orders"
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        response = self.HTTP_get_request(end_point=end_point, params=params)
        try:
            if response["message"] == "OK":
                return True
            else:
                data_list = response.get("data").get("list")
                if data_list:
                    return data_list[0]["orderId"]
        except Exception as e:
            raise Exception(f"Mufex check_if_order_canceled = Something wrong {response['message']} -> {e}")

    """
    ##############################################################
    ##############################################################
    ###################                        ###################
    ###################                        ###################
    ################### Functions for exchange ###################
    ###################                        ###################
    ###################                        ###################
    ##############################################################
    ##############################################################
    """

    def __get_mufex_timeframe(self, timeframe):
        info_logger.debug("")
        return MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]

    def set_leverage_mode_isolated(self, symbol: str):
        info_logger.debug("")
        return self.set_leverage_mode(symbol=symbol, leverage_mode=1)

    def set_leverage_mode_cross(self, symbol: str):
        info_logger.debug("")
        return self.set_leverage_mode(symbol=symbol, leverage_mode=0)

    def __get_fee_pcts(self, symbol):
        info_logger.debug("")
        trading_fee_info = self.get_symbol_trading_fee_rates(symbol=symbol)
        market_fee_pct = float(trading_fee_info["takerFeeRate"])
        limit_fee_pct = float(trading_fee_info["makerFeeRate"])
        return market_fee_pct, limit_fee_pct

    def __get_mmr_pct(self, symbol, category: str = "linear"):
        info_logger.debug("")
        risk_limit_info = self.get_risk_limit_info(symbol=symbol, category=category)
        return float(risk_limit_info["maintainMargin"])

    def set_position_mode_as_hedge_mode(self, symbol):
        info_logger.debug("")
        self.set_position_mode(symbol=symbol, position_mode=1)

    def set_position_mode_as_one_way_mode(self, symbol):
        info_logger.debug("")
        self.set_position_mode(symbol=symbol, position_mode=0)

    def __get_min_max_leverage_and_asset_size(self, symbol):
        info_logger.debug("")
        symbol_info = self.get_symbol_info(symbol=symbol)
        max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
        min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
        leverage_tick_step = float(symbol_info["leverageFilter"]["leverageStep"])
        max_asset_size = float(symbol_info["lotSizeFilter"]["maxTradingQty"])
        min_asset_size = float(symbol_info["lotSizeFilter"]["minTradingQty"])
        asset_tick_step = float(symbol_info["lotSizeFilter"]["qtyStep"])
        price_tick_step = float(symbol_info["priceFilter"]["tickSize"])
        return (
            max_leverage,
            min_leverage,
            max_asset_size,
            min_asset_size,
            asset_tick_step,
            price_tick_step,
            leverage_tick_step,
        )

    def set_exchange_settings(
        self,
        symbol: str,
        position_mode: PositionModeType,
        leverage_mode: LeverageModeType,
    ):
        """
        Make sure you actually set your leverage mode and position mode first before running this function
        """
        info_logger.debug("")
        market_fee_pct, limit_fee_pct = self.__get_fee_pcts(symbol=symbol)
        (
            max_leverage,
            min_leverage,
            max_asset_size,
            min_asset_size,
            asset_tick_step,
            price_tick_step,
            leverage_tick_step,
        ) = self.__get_min_max_leverage_and_asset_size(symbol=symbol)

        self.exchange_settings = ExchangeSettings(
            asset_tick_step=asset_tick_step,
            market_fee_pct=market_fee_pct,
            limit_fee_pct=limit_fee_pct,
            mmr_pct=self.__get_mmr_pct(symbol=symbol),
            max_leverage=max_leverage,
            min_leverage=min_leverage,
            max_asset_size=max_asset_size,
            min_asset_size=min_asset_size,
            position_mode=position_mode,
            leverage_mode=leverage_mode,
            price_tick_step=price_tick_step,
            leverage_tick_step=leverage_tick_step,
        )
