from typing import Optional
import hmac
import hashlib
import inspect
import numpy as np
from time import sleep, time
from requests import get, post
from datetime import datetime, timezone

from quantfreedom.core.enums import (
    ExchangeSettings,
    FootprintCandlesTuple,
    LeverageModeType,
    PositionModeType,
    TriggerDirectionType,
)
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

MUFEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W"]


class Mufex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        use_testnet: bool,
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
        if use_testnet:
            self.url_start = "https://api.testnet.mufex.finance"
        else:
            self.url_start = "https://api.mufex.finance"

    ################################################################
    ################################################################
    ###################                          ###################
    ###################                          ###################
    ################### Sending Info Functionsns ###################
    ###################                          ###################
    ###################                          ###################
    ################################################################
    ################################################################

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
            "X-Referer": "AKF3CWKDT",
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

    ###################################################################
    ###################################################################
    ###################                             ###################
    ###################                             ###################
    ################### Functions no default params ###################
    ###################                             ###################
    ###################                             ###################
    ###################################################################
    ###################################################################

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 1500,
        category: str = "linear",
    ) -> FootprintCandlesTuple:
        """
        [mufex candle docs](https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_querykline)

        Parameters
        ----------
        symbol : str
            [Mufex Symbol List](https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#symbol-symbol)
        timeframe : str
            "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w"
        since_datetime : datetime
            The start date, in datetime format, of candles you want to download. EX: datetime(year, month, day, hour, minute)
        until_datetime : datetime
            The until date, in datetime format, of candles you want to download minus one candle so if you are on the 5 min if you say your until date is 1200 your last candle will be 1155. EX: datetime(year, month, day, hour, minute)
        candles_to_dl : int
            The amount of candles you want to download
        category : str
            [mufex categories link](https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#contract-type-contracttype)

        Returns
        -------
        np.array
            a 2 dim array with the following columns "timestamp", "open", "high", "low", "close", "volume"
        """
        ex_timeframe = self.get_exchange_timeframe(timeframe=timeframe)
        self.timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * self.timeframe_in_ms

        since_timestamp, until_timestamp = self.get_since_until_timestamp(
            candles_to_dl_ms=candles_to_dl_ms,
            since_datetime=since_datetime,
            timeframe_in_ms=self.timeframe_in_ms,
            until_datetime=until_datetime,
        )

        candles_list = []
        end_point = "/public/v1/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": ex_timeframe,
            "start": since_timestamp,
            "end": until_timestamp,
            "limit": 1500,
        }
        the_url = self.url_start + end_point
        while params["start"] + self.timeframe_in_ms < until_timestamp:
            try:
                response: dict = get(url=the_url, params=params).json()
                new_candles = response["data"]["list"]
                last_candle_timestamp = int(new_candles[-1][0])
                if last_candle_timestamp == params["start"]:
                    print("sleeping .2 seconds")
                    sleep(0.2)
                else:
                    candles_list.extend(new_candles)
                    # add 2 sec so we don't download the same candle two times
                    params["start"] = last_candle_timestamp + 2000

            except Exception as e:
                raise Exception(f"Mufex get_candles {response.get('message')} - > {e}")

        candles = np.array(candles_list, dtype=np.float_)[:, :-1]

        open_timestamps = candles[:, 0].astype(np.int64)

        Footprint_Candles_Tuple = FootprintCandlesTuple(
            candle_open_datetimes=open_timestamps.astype("datetime64[ms]"),
            candle_open_timestamps=open_timestamps,
            candle_durations_seconds=np.full(candles.shape[0], int(self.timeframe_in_ms / 1000)),
            candle_open_prices=candles[:, 1],
            candle_high_prices=candles[:, 2],
            candle_low_prices=candles[:, 3],
            candle_close_prices=candles[:, 4],
            candle_asset_volumes=candles[:, 5],
            candle_usdt_volumes=np.around(a=candles[:, 5] * candles[:, 4], decimals=3),
        )
        self.last_fetched_ms_time = int(candles[-1, 0])

        return Footprint_Candles_Tuple

    def get_closed_pnl(
        self,
        symbol: str,
        limit: int = 200,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
    ):
        """
        [Mufex API link to Get Closed Profit and Loss](https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_closedprofitandloss)
        """

        if since_datetime is not None:
            since_datetime = int(since_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
        if until_datetime is not None:
            until_datetime = int(until_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)

        end_point = "/private/v1/account/closed-pnl"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["startTime"] = since_datetime
        params["endTime"] = until_datetime

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Data or List is empty {response['message']} -> {e}")

    def get_latest_pnl_result(
        self,
        symbol: str,
    ):
        return float(self.get_closed_pnl(symbol=symbol)[0]["closedPnl"])

    def get_symbols_list(self):
        """
        Returns a list of the symbols in alphabetical order

        Parameters
        ----------
        None

        Returns
        -------
        list
            symbols
        """
        symbols = []
        for info in self.get_all_symbols_info():
            symbols.append(info["symbol"])
            symbols.sort()
        return symbols

    def get_all_symbols_info(
        self,
        category: str = "linear",
        limit: int = 1000,
        symbol: str = None,
    ):
        """
        [Mufex API link to Get Instrument Info](https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_instrhead)

        Parameters
        ----------
        category : str
            If category is not passed, then return ""For now, default:linear
        limit : int
            Limit for data size per page, max size is 1000. Default as showing 500 pieces of data per page.It's not sorted by time
        symbol : str
            Symbol

        Returns
        -------
        _type_
            _description_
        """
        end_point = "/public/v1/instruments"
        params = {}
        params["limit"] = limit
        params["category"] = category
        params["symbol"] = symbol
        try:
            new_params = self.remove_none_from_dict(params=params)
            response: dict = get(url=self.url_start + end_point, params=new_params).json()
            response["data"]["list"][0]
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            if response.get("error_msg") == "404 Route Not Found":
                print("404 Route Not Found")
                sleep(0.5)
            else:
                raise Exception(f"Mufex get_all_symbols_info = Data or List is empty {response['message']} -> {e}")

    def get_risk_limit_info(
        self,
        symbol: str,
        category: str = "linear",
    ):
        """
        [Mufex API link to Get Risk Limit](https://www.mufex.finance/apidocs/derivatives/contract/index.html?console#t-dv_risklimithead)

        Parameters
        ----------
        symbol : str
            Symbol
        category : str
            If category is not passed, then return ""For now, default:linear

        Returns
        -------
        _type_
            _description_
        """
        end_point = "/public/v1/position-risk"
        params = {}
        params["category"] = category
        params["symbol"] = symbol
        try:
            new_params = self.remove_none_from_dict(params=params)
            response: dict = get(url=self.url_start + end_point, params=new_params).json()
            data_list = response["data"]["list"][0]

            return data_list
        except Exception as e:
            if response.get("error_msg") == "404 Route Not Found":
                print("404 Route Not Found")
                sleep(0.5)
            else:
                raise Exception(f"Mufex get_risk_limit_info = Data or List is empty {response['message']} -> {e}")

    def create_order(
        self,
        symbol: str,
        buy_sell: str,
        position_mode: PositionModeType,  # type: ignore
        order_type: str,
        asset_size: float,
        time_in_force: str = "GoodTillCancel",
        price: Optional[float] = None,
        triggerDirection: TriggerDirectionType = None,  # type: ignore
        triggerPrice: str = None,
        triggerBy: str = None,
        tpTriggerBy: str = None,
        slTriggerBy: str = None,
        custom_order_id: str = None,
        takeProfit: Optional[float] = None,
        stopLoss: Optional[float] = None,
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

        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            order_id = response["data"]["orderId"]
            return order_id
        except Exception as e:
            raise Exception(f"Mufex create_order {response['message']} -> {e}")

    def get_trading_fee_rates(
        self,
        symbol: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        end_point = "/private/v1/account/trade-fee"
        params = {}
        params["symbol"] = symbol
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"][0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_trading_fee_rates = Data or List is empty {response['message']} -> {e}")

    def get_symbol_trading_fee_rates(
        self,
        symbol: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-tradingfeerate
        """
        end_point = "/private/v1/account/trade-fee"
        params = {}
        params["symbol"] = symbol
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
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
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"]
            data_list[0]  # try this to see if anything is in here
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_order_history = Data or List is empty {response['message']} -> {e}")

    def get_order_history_by_order_id(
        self,
        symbol: str,
        order_id: str,
    ):
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
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_open_orders = {response['message']} -> {e}")

    def get_open_order_by_order_id(
        self,
        symbol: str,
        order_id: str,
    ):
        open_order = self.get_open_orders(symbol=symbol, order_id=order_id)[0]
        return open_order

    def get_filled_orders(
        self,
        symbol: str,
        limit: int = 200,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        execType: str = None,
        order_id: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-usertraderecords

        Get user's trading records. The results are ordered in descending order (the first item is the latest). Returns records up to 2 years old.

        use link to see all Request Parameters
        """
        if since_datetime is not None:
            since_datetime = int(since_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
        if until_datetime is not None:
            until_datetime = int(until_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)

        end_point = "/private/v1/trade/fills"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["execType"] = execType
        params["orderId"] = order_id
        params["startTime"] = since_datetime
        params["endTime"] = until_datetime

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["data"]["list"][0]
            data_list = response["data"]["list"]

            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_filled_orders = Data or List is empty {response['message']} -> {e}")

    def get_filled_order_by_order_id(
        self,
        symbol: str,
        order_id: str,
    ):
        filled_order = self.get_filled_orders(symbol=symbol, order_id=order_id)[0]
        return filled_order

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
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"]

            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_account_position_info = {response['message']} -> {e}")

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
            response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
            response_order_id = response.get("data").get("orderId")
            if response_order_id == order_id or response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex cancel_open_order message= {response['message']} -> {e}")

    def cancel_all_open_orders_per_symbol(
        self,
        symbol: str,
    ):
        """
        no link yet
        """
        end_point = "/private/v1/trade/cancel-all"
        params = {
            "symbol": symbol,
        }
        try:
            response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
            if response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex cancel_all_open_orders_per_symbol message = {response['message']} -> {e}")

    def adjust_order(
        self,
        params: dict = {},
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-contract_replaceorder

        you basically have to use the same info that you would for create order
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-dv_placeorder
        """
        end_point = "/private/v1/trade/replace"
        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            response_order_id = response.get("data").get("orderId")
            if response_order_id == params["orderId"] or response["message"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex adjust_order message = {response['message']} -> {e}")

    def move_limit_order(
        self,
        symbol: str,
        order_id: str,
        new_price: float,
        asset_size: float,
    ):
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        params["qty"] = str(asset_size)
        params["price"] = str(new_price)
        return self.adjust_order(params=params)

    def move_stop_order(
        self,
        symbol: str,
        order_id: str,
        new_price: float,
        asset_size: float,
    ):
        params = {}
        params["symbol"] = symbol
        params["orderId"] = order_id
        params["qty"] = str(asset_size)
        params["triggerPrice"] = str(new_price)
        return self.adjust_order(params=params)

    def get_wallet_info(
        self,
        trading_with: str = None,
    ):
        """
        https://www.mufex.finance/apidocs/derivatives/contract/index.html#t-balance
        """
        end_point = "/private/v1/account/balance"
        params = {
            "coin": trading_with,
        }
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["data"]["list"]
            data_list[0]
            return data_list
        except Exception as e:
            raise Exception(f"Mufex get_wallet_info = Data or List is empty {response['message']} -> {e}")

    def get_no_fees_balance_of_asset_market_in_only(
        self,
        trading_with: str,
        symbol: str,
    ):
        coins = self.get_wallet_info(trading_with=trading_with)
        for coin in coins:
            if coin["coin"] == trading_with:
                wallet_balance = float(coin["walletBalance"])
                break

        market_fee_pct = self.get_fee_pcts(symbol=symbol)[0]
        pos_info = self.get_position_info(symbol=symbol)

        long_fees = float(pos_info[0]["positionValue"]) * market_fee_pct
        short_fees = float(pos_info[1]["positionValue"]) * market_fee_pct

        total_fees = long_fees + short_fees
        no_fee_wallet_balance = wallet_balance + total_fees

        return no_fee_wallet_balance

    def set_position_mode(
        self,
        position_mode: PositionModeType,  # type: ignore
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
        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "position mode not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex: set_position_mode= {response['message']} -> {e}")

    def set_leverage(
        self,
        symbol: str,
        leverage: float,
    ):
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
        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "leverage not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_leverage = Data or List is empty {response['message']} -> {e}")

    def set_leverage_mode(
        self,
        symbol: str,
        leverage_mode: LeverageModeType,  # type: ignore
        leverage: int = 5,
    ):
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
        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["message"] in ["OK", "Isolated not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex set_leverage_mode = Data or List is empty {response['message']} -> {e}")

    def check_if_order_filled(
        self,
        symbol: str,
        order_id: str,
    ):
        data_list = self.get_filled_orders(symbol=symbol, order_id=order_id)
        try:
            if data_list[0]["orderId"] == order_id:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex check_if_order_filled -> {e}")

    def check_if_order_canceled(
        self,
        symbol: str,
        order_id: str,
    ):
        data_list = self.get_order_history(symbol=symbol, order_id=order_id)
        try:
            if data_list[0]["orderId"] == order_id:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex check_if_order_canceled -> {e}")

    def check_if_order_open(
        self,
        symbol: str,
        order_id: str,
    ):
        data_list = self.get_open_orders(symbol=symbol, order_id=order_id)
        try:
            if data_list[0]["orderId"] == order_id:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Mufex check_if_order_canceled -> {e}")

    def set_leverage_mode_isolated(
        self,
        symbol: str,
    ):
        true_false = self.set_leverage_mode(symbol=symbol, leverage_mode=1)

        return true_false

    def set_leverage_mode_cross(
        self,
        symbol: str,
    ):
        true_false = self.set_leverage_mode(symbol=symbol, leverage_mode=0)

        return true_false

    def get_fee_pcts(
        self,
        symbol: str,
    ):
        trading_fee_info = self.get_symbol_trading_fee_rates(symbol=symbol)
        market_fee_pct = float(trading_fee_info["takerFeeRate"])
        limit_fee_pct = float(trading_fee_info["makerFeeRate"])

        return market_fee_pct, limit_fee_pct

    def __get_mmr_pct(
        self,
        symbol,
        category: str = "linear",
    ):
        risk_limit_info = self.get_risk_limit_info(symbol=symbol, category=category)
        mmr_pct = float(risk_limit_info["maintainMargin"])

        return mmr_pct

    def set_position_mode_as_hedge_mode(
        self,
        symbol: str,
    ):
        true_false = self.set_position_mode(symbol=symbol, position_mode=3)

        return true_false

    def set_position_mode_as_one_way_mode(
        self,
        symbol: str,
    ):
        true_false = self.set_position_mode(symbol=symbol, position_mode=0)

        return true_false

    def __get_min_max_leverage_and_asset_size(
        self,
        symbol: str,
    ):
        symbol_info = self.get_all_symbols_info(symbol=symbol, limit=1)[0]
        max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
        min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
        max_asset_size = float(symbol_info["lotSizeFilter"]["maxTradingQty"])
        min_asset_size = float(symbol_info["lotSizeFilter"]["minTradingQty"])
        asset_tick_step = self.int_value_of_step_size(symbol_info["lotSizeFilter"]["qtyStep"])
        price_tick_step = self.int_value_of_step_size(symbol_info["priceFilter"]["tickSize"])
        leverage_tick_step = self.int_value_of_step_size(symbol_info["leverageFilter"]["leverageStep"])

        return (
            max_leverage,
            min_leverage,
            max_asset_size,
            min_asset_size,
            asset_tick_step,
            price_tick_step,
            leverage_tick_step,
        )

    def set_and_get_exchange_settings_tuple(
        self,
        leverage_mode: LeverageModeType,  # type: ignore
        position_mode: PositionModeType,  # type: ignore
        symbol: str,
    ):
        self.position_mode = position_mode
        if position_mode == PositionModeType.HedgeMode:
            self.set_position_mode_as_hedge_mode(symbol=symbol)
        else:
            self.set_position_mode_as_one_way_mode(symbol=symbol)

        if leverage_mode == LeverageModeType.Isolated:
            self.set_leverage_mode_isolated(symbol=symbol)
        else:
            self.set_leverage_mode_cross(symbol=symbol)

        market_fee_pct, limit_fee_pct = self.get_fee_pcts(symbol=symbol)
        (
            max_leverage,
            min_leverage,
            max_asset_size,
            min_asset_size,
            asset_tick_step,
            price_tick_step,
            leverage_tick_step,
        ) = self.__get_min_max_leverage_and_asset_size(symbol=symbol)

        return ExchangeSettings(
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

    def get_balance(
        self,
    ):
        endpoint = "/private/v1/account/balance"
        params = {}
        try:
            response: dict = self.__HTTP_get_request(end_point=endpoint, params=params)
            ret = response.json()

            code = ret["code"]
            if code != 0:
                return ret["message"] + f"error code {code}"

            equity = ret["data"]["list"][0]["equity"]
            balance = ret["data"]["list"][0]["walletBalance"]

            return {"equity": equity, "balance": balance}

        except Exception as e:
            print(f"Unexpected error: {e}")
            response_content = e.response.text if e.response else "No content"
            status_code = e.response.status_code if e.response else "No status code"
            print(f"HTTP Response Content: {response_content}")
            print(f"HTTP Status Code: {status_code}")

            return {"message": str(e)}

    def get_exchange_timeframe(
        self,
        timeframe: str,
    ):
        try:
            return MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            raise Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")

    #######################################################
    #######################################################
    #######################################################
    ##################      Live     ######################
    ##################      Live     ######################
    ##################      Live     ######################
    #######################################################
    #######################################################
    #######################################################

    def check_long_hedge_mode_if_in_position(
        self,
        symbol: str,
    ):
        if float(self.get_position_info(symbol=symbol)[0]["entryPrice"]) > 0:
            return True
        else:
            return False

    def create_long_hedge_mode_entry_market_order_with_stoploss(
        self,
        asset_size: float,
        symbol: str,
        sl_price: float,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=PositionModeType.BuySide,
            buy_sell="Buy",
            order_type="Market",
            asset_size=asset_size,
            time_in_force="GoodTillCancel",
            stopLoss=sl_price,
        )

    def create_long_hedge_mode_entry_market_order(
        self,
        asset_size: float,
        symbol: str,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=PositionModeType.BuySide,
            buy_sell="Buy",
            order_type="Market",
            asset_size=asset_size,
            time_in_force="GoodTillCancel",
        )

    def create_long_hedge_mode_tp_limit_order(
        self,
        asset_size: float,
        symbol: str,
        tp_price: float,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=PositionModeType.BuySide,
            buy_sell="Sell",
            order_type="Limit",
            asset_size=asset_size,
            price=tp_price,
            reduce_only=True,
            time_in_force="PostOnly",
        )

    def create_long_hedge_mode_sl_order(
        self,
        asset_size: float,
        symbol: str,
        sl_price: float,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=PositionModeType.BuySide,
            buy_sell="Sell",
            order_type="Market",
            asset_size=asset_size,
            triggerPrice=sl_price,
            reduce_only=True,
            triggerDirection=TriggerDirectionType.Fall,
            time_in_force="GoodTillCancel",
        )

    def get_long_hedge_mode_position_info(
        self,
        symbol: str,
    ):
        pos_info = self.get_position_info(symbol=symbol)[0]
        return pos_info

    def list_of_functions(self):
        func_list = inspect.getmembers(Mufex, predicate=inspect.isfunction)
        new_list = []
        for func in func_list:
            func_name = func[0]
            if not "_" in func_name[0]:
                new_list.append(func[0])
        return new_list

    def close_hedge_positions_and_orders(
        self,
        symbol: str = None,
        settleCoin: str = None,
    ):
        """
        Parameters
        ----------
        symbol : str
        """

        position_info = self.get_position_info(symbol=symbol, settleCoin=settleCoin)

        order_type = "Market"

        asset_size_0 = float(position_info[0]["size"])
        # Return buy or sale based on pos side (if in a short, side == sell)
        if asset_size_0 > 0:
            position_mode = int(position_info[0]["positionIdx"])
            buy_sell = "Sell" if position_mode == 1 else "Buy"
            self.create_order(
                symbol=symbol,
                order_type=order_type,
                asset_size=asset_size_0,
                buy_sell=buy_sell,
                position_mode=position_mode,
            )

        asset_size_1 = float(position_info[1]["size"])
        if asset_size_1 > 0:
            position_mode = int(position_info[1]["positionIdx"])
            buy_sell = "Buy" if position_mode == 2 else "Sell"
            self.create_order(
                symbol=symbol,
                order_type=order_type,
                asset_size=asset_size_1,
                buy_sell=buy_sell,
                position_mode=position_mode,
            )

        self.cancel_all_open_orders_per_symbol(symbol=symbol)

        sleep(1)

        open_order_list = self.get_open_orders(symbol=symbol)

        position_info = self.get_position_info(symbol=symbol)

        asset_size_0 = float(position_info[0]["size"])
        asset_size_1 = float(position_info[1]["size"])

        if open_order_list or asset_size_0 > 0 or asset_size_1 > 0:
            return False
        else:
            return True
