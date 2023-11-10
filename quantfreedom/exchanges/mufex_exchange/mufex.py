import hashlib
import hmac
import json
import numpy as np
from datetime import timedelta
from requests import get, post
from time import sleep, time

from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionModeType,
    TriggerDirectionType,
)
from quantfreedom.exchanges.exchange import Exchange

MUFEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W"]


class Mufex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
    ):
        """
        main docs page https://www.mufex.finance/apidocs/derivatives/contract/index.html

        Make sure you have your position mode set to hedge or else a lot of functions will not work.
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        self.api_key = api_key
        self.secret_key = secret_key
        if use_test_net:
            self.url_start = "https://api.testnet.mufex.finance"
        else:
            self.url_start = "https://api.mufex.finance"

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
        timestamp = str(int(time() * 1000))
        params_as_dict_string = self.__get_params_as_json_string(params=params)
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

    def __HTTP_get_request(self, end_point, params):
        timestamp = str(int(time() * 1000))
        params_as_path = self.__get_params_as_string(params=params)
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

    def __gen_signature(self, timestamp, params_as_string):
        param_str = timestamp + self.api_key + "5000" + params_as_string
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash.hexdigest()

    def __get_params_as_json_string(self, params):
        new_params = {k: v for k, v in params.items() if v is not None}
        params_as_dict_string = str(json.dumps(new_params))
        return params_as_dict_string

    def __get_params_as_string(self, params):
        params_string = "&".join("{key}={value}".format(key=x[0], value=x[1]) for x in params if x[1] is not None)
        return params_string

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
        since_date_ms: int = None,
        until_date_ms: int = None,
        candles_to_dl: int = 1500,
        category: str = "linear",
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline

        timeframe: "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"

        returning dict is [start, open, high, low, close, volume, turnover]

        use link to see all Request Parameters
        """
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=MUFEX_TIMEFRAMES, timeframe=timeframe)
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

        candles_list = []
        end_point = "/public/v1/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": ex_timeframe,
            "start": since_date_ms,
            "end": until_date_ms,
        }
        start_time = self.get_current_time_sec()
        while params["start"] + timeframe_in_ms < until_date_ms:
            try:
                response = get(url=self.url_start + end_point, params=params).json()
                new_candles = response["data"]["list"]
                last_candle_time_ms = int(new_candles[-1][0])
                if last_candle_time_ms == params["start"]:
                    sleep(0.2)
                else:
                    candles_list.extend(new_candles)
                    # add 2 sec so we don't download the same candle two times
                    params["start"] = last_candle_time_ms + 2000

            except Exception as e:
                raise Exception(f"Mufex get_candles_df {response.get('message')} - > {e}")

        candles_np = np.array(candles_list, dtype=np.float_)[:, :-2]
        # time_it_took_in_seconds = self.get_current_time_sec() - start_time
        # td = str(timedelta(seconds=time_it_took_in_seconds)).split(":")
        # print(f"It took {td[1]} mins and {td[2]} seconds to download {len(candles_list)} candles")

        return candles_np

    def get_closed_pnl(
        self,
        symbol: str,
        limit: int = 200,
        since_date_ms: int = None,
        until_date_ms: int = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_closedprofitandloss
        """
        end_point = "/private/v1/account/closed-pnl"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["startTime"] = since_date_ms
        params["endTime"] = until_date_ms
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Data or List is empty {response['message']} -> {e}")

    def get_latest_pnl_result(self, symbol: str):
        return float(self.get_closed_pnl(symbol=symbol)[0]["closedPnl"])

    def get_all_symbols_info(self, category: str = "linear", limit: int = 1000, symbol: str = None):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_instrhead

        Paramaters:
        symbol
        """
        end_point = "/public/v1/instruments"
        params = {}
        params["limit"] = limit
        params["category"] = category
        params["symbol"] = symbol
        try:
            new_params = {k: v for k, v in params.items() if v is not None}
            response = get(url=self.url_start + end_point, params=new_params).json()
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_all_symbols_info = Data or List is empty {response['message']} -> {e}")

    def get_risk_limit_info(self, symbol: str, category: str = "linear"):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_risklimithead
        """
        end_point = "/public/v1/position-risk"
        params = {}
        params["category"] = category
        params["symbol"] = symbol
        try:
            response = get(url=self.url_start + end_point, params=params).json()
            data_list = response["data"]["list"][0]

            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_risk_limit_info = Data or List is empty {response['message']} -> {e}")

    def create_order(
        self,
        symbol: str,
        buy_sell: str,
        position_mode: PositionModeType,
        order_type: str,
        asset_size: float,
        time_in_force: str,
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
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder

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
        end_point = "/private/v1/trade/create"
        params = {}
        params["symbol"] = symbol.upper()
        params["side"] = buy_sell.capitalize()
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
            order_id = response["data"]["orderId"]
            return order_id
        except Exception as e:
            raise Exception(f"Mufex create_order {response['message']} -> {e}")

    def get_trading_fee_rates(self, symbol: str = None):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        end_point = "/private/v1/account/trade-fee"
        params = {}
        params["symbol"] = symbol
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_trading_fee_rates = Data or List is empty {response['message']} -> {e}")

    def get_symbol_trading_fee_rates(self, symbol: str = None):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        end_point = "/private/v1/account/trade-fee"
        params = {}
        params["symbol"] = symbol
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_symbol_trading_fee_rates = Data or List is empty {response['message']} -> {e}")

    def get_order_history(
        self,
        symbol: str,
        limit: int = 50,
        order_id: str = None,
        custom_order_id: str = None,
        orderStatus: str = None,
        orderFilter: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getorder

        use link to see all Request Parameters
        """
        end_point = "/private/v1/trade/orders"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["orderId"] = order_id
        params["orderLinkId"] = custom_order_id
        params["orderStatus"] = orderStatus
        params["orderFilter"] = orderFilter
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"]
            data_list[0]  # try this to see if anything is in here
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_order_history = Data or List is empty {response['message']} -> {e}")

    def get_order_history_by_order_id(self, symbol: str, order_id: str):
        return self.get_order_history(symbol=symbol, order_id=order_id)[0]

    def get_open_orders(
        self,
        symbol: str,
        limit: int = 50,
        order_id: str = None,
        custom_order_id: str = None,
        orderFilter: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_getopenorder

        Query real-time order information. If only orderId or orderLinkId are passed, a single order will be returned; otherwise, returns up to 500 unfilled orders

        orderId
        limit
        """
        end_point = "/private/v1/trade/activity-orders"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["orderId"] = order_id
        params["orderLinkId"] = custom_order_id
        params["orderFilter"] = orderFilter
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_open_orders = Data or List is empty {response['message']} -> {e}")

    def get_open_order_by_order_id(self, symbol: str, order_id: str):
        return self.get_open_orders(symbol=symbol, order_id=order_id)[0]

    def get_filled_orders(
        self,
        symbol: str,
        limit: int = 200,
        since_date_ms: int = None,
        until_date_ms: int = None,
        execType: str = None,
        order_id: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-usertraderecords

        Get user's trading records. The results are ordered in descending order (the first item is the latest). Returns records up to 2 years old.

        use link to see all Request Parameters
        """
        end_point = "/private/v1/trade/fills"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["execType"] = execType
        params["orderId"] = order_id
        params["startTime"] = since_date_ms
        params["endTime"] = until_date_ms
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]

            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_filled_orders = Data or List is empty {response['message']} -> {e}")

    def get_filled_orders_by_order_id(self, symbol: str, order_id: str):
        return self.get_filled_orders(symbol=symbol, order_id=order_id)[0]

    def get_position_info(
        self,
        symbol: str = None,
        settleCoin: str = None,
        limit: int = 50,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_myposition
        """
        end_point = "/private/v1/account/positions"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["settleCoin"] = settleCoin
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]

            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_account_position_info = Data or List is empty {response['message']} -> {e}")

    def cancel_open_order(
        self,
        symbol: str,
        order_id: str = None,
        custom_order_id: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-contract_cancelorder
        """
        end_point = "/private/v1/trade/cancel"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "orderLinkId": custom_order_id,
        }
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id == order_id or response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex cancel_open_order message= {response['message']} -> {e}")

    def cancel_all_open_orders_per_symbol(self, symbol: str):
        """
        no link yet
        """
        end_point = "/private/v1/trade/cancel-all"
        params = {
            "symbol": symbol,
        }
        try:
            response = self.__HTTP_post_request(end_point=end_point, params=params)
            if response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex cancel_all_open_orders_per_symbol message = {response['message']} -> {e}")

    def adjust_order(self, params: dict = {}):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder

        you basically have to use the same info that you would for create order
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
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

    def move_limit_order(self, symbol: str, order_id: str, new_price: float, asset_size: float):
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        params["qty"] = str(asset_size)
        params["price"] = str(new_price)
        return self.adjust_order(params=params)

    def move_stop_order(self, symbol: str, order_id: str, new_price: float, asset_size: float):
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        params["qty"] = str(asset_size)
        params["triggerPrice"] = str(new_price)
        return self.adjust_order(params=params)

    def get_wallet_info(self, trading_with: str = None):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        end_point = "/private/v1/account/balance"
        params = {
            "coin": trading_with,
        }
        response = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"]
            data_list[0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_wallet_info = Data or List is empty {response['message']} -> {e}")

    def get_equity_of_asset(self, trading_with: str):
        return float(self.get_wallet_info(trading_with=trading_with)[0]["equity"])

    def set_position_mode(
        self,
        position_mode: PositionModeType,
        trading_with: str = None,
        symbol: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_switchpositionmode
        """
        end_point = "/private/v1/account/set-position-mode"
        params = {
            "symbol": symbol,
            "mode": position_mode,
            "coin": trading_with,
        }
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "position mode not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex: set_position_mode= {response['message']} -> {e}")

    def set_leverage_value(self, symbol: str, leverage: float):
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
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "leverage not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_leverage_value = Data or List is empty {response['message']} -> {e}")

    def set_leverage_mode(self, symbol: str, leverage_mode: LeverageModeType, leverage: int = 5):
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
        response = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "Isolated not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_leverage_mode = Data or List is empty {response['message']} -> {e}")

    def check_if_order_filled(self, symbol: str, order_id: str):
        response = self.get_filled_orders(symbol=symbol, order_id=order_id)
        try:
            if response["message"] == "OK":
                return True
            else:
                response["data"]["list"][0]
                if response["orderId"] == order_id:
                    return True
                else:
                    raise Exception
        except Exception as e:
            raise Exception(f"Mufex check_if_order_filled{response['message']} -> {e}")

    def check_if_order_canceled(self, symbol: str, order_id: str):
        response = self.get_order_history(symbol=symbol, order_id=order_id)
        try:
            if response["message"] == "OK":
                return True
            else:
                response["data"]["list"][0]
                if response["orderId"] == order_id:
                    return True
                else:
                    raise Exception
        except Exception as e:
            raise Exception(f"Mufex check_if_order_canceled= {response['message']} -> {e}")

    def check_if_order_open(self, symbol: str, order_id: str):
        response = self.get_open_orders(symbol=symbol, order_id=order_id)
        try:
            if response["message"] == "OK":
                return True
            else:
                response["data"]["list"][0]
                if response["orderId"] == order_id:
                    return True
                else:
                    raise Exception
        except Exception as e:
            raise Exception(f"Mufex check_if_order_canceled= {response['message']} -> {e}")

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

    def set_leverage_mode_isolated(self, symbol: str):
        true_false = self.set_leverage_mode(symbol=symbol, leverage_mode=1)

        return true_false

    def set_leverage_mode_cross(self, symbol: str):
        true_false = self.set_leverage_mode(symbol=symbol, leverage_mode=0)

        return true_false

    def __get_fee_pcts(self, symbol):
        trading_fee_info = self.get_symbol_trading_fee_rates(symbol=symbol)
        market_fee_pct = float(trading_fee_info["takerFeeRate"])
        limit_fee_pct = float(trading_fee_info["makerFeeRate"])

        return market_fee_pct, limit_fee_pct

    def __get_mmr_pct(self, symbol, category: str = "linear"):
        risk_limit_info = self.get_risk_limit_info(symbol=symbol, category=category)
        mmr_pct = float(risk_limit_info["maintainMargin"])

        return mmr_pct

    def set_position_mode_as_hedge_mode(self, symbol):
        true_false = self.set_position_mode(symbol=symbol, position_mode=1)

        return true_false

    def set_position_mode_as_one_way_mode(self, symbol):
        true_false = self.set_position_mode(symbol=symbol, position_mode=0)

        return true_false

    def __int_value_of_step_size(self, step_size: str):
        return step_size.index("1") - step_size.index(".")

    def __get_min_max_leverage_and_asset_size(self, symbol):
        symbol_info = self.get_all_symbols_info(symbol=symbol, limit=1)[0]
        max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
        min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
        max_asset_size = float(symbol_info["lotSizeFilter"]["maxTradingQty"])
        min_asset_size = float(symbol_info["lotSizeFilter"]["minTradingQty"])
        asset_tick_step = self.__int_value_of_step_size(symbol_info["lotSizeFilter"]["qtyStep"])
        price_tick_step = self.__int_value_of_step_size(symbol_info["priceFilter"]["tickSize"])
        leverage_tick_step = self.__int_value_of_step_size(symbol_info["leverageFilter"]["leverageStep"])

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
