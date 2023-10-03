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
from quantfreedom.exchanges.base.exchange import UNIVERSAL_TIMEFRAMES, Exchange

MUFEX_TIMEFRAMES = [1, 3, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]


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
        except Exception as e:
            raise Exception(f"{e}")
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
        except Exception as e:
            raise Exception(f"{e}")
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
        except Exception as e:
            raise Exception(f"{e}")
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
        except Exception as e:
            raise Exception(f"{e}")
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

    def get_candles_df(
        self,
        symbol: str,
        timeframe: str,
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = None,
        category: str = "linear",
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline

        timeframe: 1 3 5 15 30 60 120 240 360 720 "D" "M" "W"

        returning dict is [start, open, high, low, close, volume, turnover]

        use link to see all Request Parameters
        """
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
        }
        while params["start"] + timeframe_in_ms < until_date_ms:
            try:
                response = self.__HTTP_get_request(end_point=end_point, params=params)
                new_candles = response.get("data").get("list")
                if new_candles is not None:
                    if new_candles:
                        last_candle_time_ms = int(new_candles[-1][0])
                        if last_candle_time_ms == params["start"]:
                            sleep(0.2)
                        else:
                            candles_list.extend(new_candles)
                            # add one sec so we don't download the same candle two times
                            params["start"] = last_candle_time_ms + 1000
                    else:
                        break
                else:
                    raise Exception(f"Data or List is empty {response['message']}")

            except Exception as e:
                raise Exception(f"Something wrong with get_and_set_candles_df -> {e}")
        return self.get_candles_list_to_pd(candles_list=candles_list, col_end=-2)

    def get_symbol_ticker_info(self, category: str = "linear", params: dict = {}):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_tickerhead

        Parameters:
        symbol
        """
        end_point = "/public/v1/market/tickers"
        params["catergoy"] = category
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_symbol_ticker_info -> {e}")

    def get_symbol_info(self, category: str = "linear", limit: int = 1000, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_instrhead

        Paramaters:
        symbol
        """
        end_point = "/public/v1/instruments"
        params["limit"] = limit
        params["category"] = category
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_symbol_info -> {e}")

    def get_risk_limit_info(self, symbol: str, category: str = "linear", **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_risklimithead
        """
        end_point = "/public/v1/position-risk"
        params = {}
        params["category"] = category
        params["symbol"] = symbol
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list[0]
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_risk_limit_info -> {e}")

    def create_order(self, params: dict, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        use this website to see all the params
        """
        end_point = "/private/v1/trade/create"
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id is not None and response_order_id:
                return response_order_id
            else:
                raise Exception(f"Data or orderId is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with create_order -> {e}")

    def get_trading_fee_rates(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        end_point = "/private/v1/account/trade-fee"
        try:
            response = self.__HTTP_get_request_no_params(end_point=end_point)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_trading_fee_rates -> {e}")

    def get_symbol_trading_fee_rates(self, symbol: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder

        use link to see all Request Parameters
        """
        end_point = "/private/v1/trade/orders"
        params = {}
        params["symbol"] = symbol
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list[0]
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_symbol_trading_fee_rates -> {e}")

    def get_order_history(self, symbol: str, limit: int = 50, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder

        use link to see all Request Parameters
        """
        end_point = "/private/v1/trade/orders"
        params["symbol"] = symbol
        params["limit"] = limit
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_order_history -> {e}")

    def get_order_id_info(self, symbol: str, order_id: str, params: dict = {}, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder
        """
        params["orderId"] = order_id
        return self.get_order_history(symbol=symbol, params=params)[0]

    def get_account_position_info(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        try:
            response = self.__HTTP_get_request_no_params(end_point=end_point)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_account_position_info -> {e}")

    def get_symbol_position_info(self, symbol: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {"symbol": symbol}
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_symbol_position_info -> {e}")

    def cancel_open_order(self, symbol: str, order_id: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_cancelorder
        """
        end_point = "/private/v1/trade/cancel"
        params = {
            "symbol": symbol,
            "orderId": order_id,
        }
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id is not None and response_order_id == order_id:
                return True
            else:
                raise Exception(f'Data or orderId is empty {response["message"]}')
        except Exception as e:
            raise Exception(f"Something is wrong with cancel_open_order -> {e}")

    def adjust_open_order(self, symbol: str, order_id: str, new_price: float, asset_amount: float, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder
        """
        end_point = "/private/v1/trade/replace"
        params = {}
        params["symbol"] = symbol
        params["order_id"] = order_id
        params["price"] = new_price
        params["qty"] = asset_amount
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id is not None and response_order_id == order_id:
                return True
            else:
                raise Exception(f'Data or orderId is empty {response["message"]}')
        except Exception as e:
            raise Exception(f"Something is wrong with adjust_open_order -> {e}")

    def change_open_order_asset_amount(self, symbol: str, order_id: str, asset_amount: float, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder
        """
        end_point = "/private/v1/trade/replace"
        params = {}
        params["symbol"] = symbol
        params["order_id"] = order_id
        params["qty"] = asset_amount
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id is not None and response_order_id == order_id:
                return True
            else:
                raise Exception(f'Data or orderId is empty {response["message"]}')
        except Exception as e:
            raise Exception(f"Something is wrong with change_open_order_asset_amount -> {e}")

    def move_open_order(self, symbol: str, order_id: str, new_price: float, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder
        """
        end_point = "/private/v1/trade/replace"
        params = {}
        params["symbol"] = symbol
        params["order_id"] = order_id
        params["price"] = new_price
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id is not None and response_order_id == order_id:
                return True
            else:
                raise Exception(f'Data or orderId is empty {response["message"]}')
        except Exception as e:
            raise Exception(f"Something is wrong with move_open_order -> {e}")

    def get_wallet_info(self, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        end_point = "/private/v1/account/balance"
        try:
            response = self.__HTTP_get_request_no_params(end_point=end_point)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_wallet_info -> {e}")

    def get_wallet_info_of_asset(self, asset: str, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        end_point = "/private/v1/account/balance"
        params = {"coin": asset}
        try:
            response = self.__HTTP_get_request(end_point=end_point, params=params)
            data_list = response.get("data").get("list")
            if data_list is not None and data_list:
                return data_list[0]
            else:
                raise Exception(f"Data or List is empty {response['message']}")
        except Exception as e:
            raise Exception(f"Something is wrong with get_wallet_info_of_asset -> {e}")

    def set_position_mode(self, symbol: str, position_mode: PositionModeType, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": symbol,
            "mode": 3 if position_mode == PositionModeType.HedgeMode else 0,
        }
        try:
            message = self.__HTTP_post_request(end_point=end_point, params=params)["message"]
            if message in ["OK", "position mode not modified"]:
                return position_mode
            else:
                raise Exception(f"{message}")
        except Exception as e:
            raise Exception(f"Something is wrong with set_position_mode {e}")

    def set_leverage_value(self, symbol: str, leverage: float, **vargs):
        """
        No link yet
        """
        end_point = "/private/v1/account/set-leverage"
        leverage_str = str(leverage)
        params = {
            "symbol": symbol,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            message = self.__HTTP_post_request(end_point=end_point, params=params)["message"]
            if message in ["OK", "leverage not modified"]:
                return True
            else:
                raise Exception(f"{message}")
        except Exception as e:
            raise Exception(f"Something is wrong with set_leverage_value -> {e}")

    def set_leverage_mode(self, symbol: str, leverage_mode: LeverageModeType, leverage: int = 5, **vargs):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_marginswitch
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        end_point = "/private/v1/account/set-isolated"
        leverage_str = str(leverage)
        params = {
            "symbol": symbol,
            "tradeMode": leverage_mode,
            "buyLeverage": leverage_str,
            "sellLeverage": leverage_str,
        }
        try:
            message = self.__HTTP_post_request(end_point=end_point, params=params)["message"]
            if message in ["OK", "Isolated not modified"]:
                return leverage_mode
            else:
                raise Exception(f"{message}")
        except Exception as e:
            raise Exception(f"Something is wrong with set_leverage_mode -> {e}")

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
        return MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]

    def __set_leverage_mode_isolated(self):
        return self.set_leverage_mode(tradeMode=1)

    def __set_leverage_mode_cross(self):
        return self.set_leverage_mode(tradeMode=0)

    def __get_fee_pcts(self, symbol):
        trading_fee_info = self.get_symbol_trading_fee_rates(symbol=symbol)
        market_fee_pct = float(trading_fee_info["takerFeeRate"])
        limit_fee_pct = float(trading_fee_info["makerFeeRate"])
        return market_fee_pct, limit_fee_pct

    def __get_mmr_pct(self, symbol, category: str = "linear"):
        risk_limit_info = self.get_risk_limit_info(symbol=symbol, category=category)
        return risk_limit_info["maintainMargin"]

    def __get_min_max_leverage_and_asset_size(self, symbol):
        symbol_info = self.get_symbol_info(symbol=symbol)
        max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
        min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
        max_asset_qty = float(symbol_info["lotSizeFilter"]["maxTradingQty"])
        min_asset_qty = float(symbol_info["lotSizeFilter"]["minTradingQty"])
        return max_leverage, min_leverage, max_asset_qty, min_asset_qty

    def __set_position_mode_as_hedge_mode(self, symbol):
        self.set_position_mode(symbol=symbol, position_mode=3)

    def __set_position_mode_as_one_way_mode(self, symbol):
        self.set_position_mode(symbol=symbol, position_mode=0)

    def __set_exchange_settings(
        self,
        symbol: str,
        position_mode: PositionModeType,
        leverage_mode: LeverageModeType,
    ):
        """
        Make sure you actually set your leverage mode and position mode first before running this function
        """
        market_fee_pct, limit_fee_pct = self.__get_fee_pcts(symbol=symbol)
        max_leverage, min_leverage, max_asset_qty, min_asset_qty = self.__get_min_max_leverage_and_asset_size()
        self.exchange_settings = ExchangeSettings(
            market_fee_pct=market_fee_pct,
            limit_fee_pct=limit_fee_pct,
            mmr_pct=self.__get_mmr_pct(symbol=symbol),
            max_leverage=max_leverage,
            min_leverage=min_leverage,
            max_asset_qty=max_asset_qty,
            min_asset_qty=min_asset_qty,
            position_mode=position_mode,
            leverage_mode=leverage_mode,
        )
