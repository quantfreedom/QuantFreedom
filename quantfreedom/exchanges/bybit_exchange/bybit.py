import hashlib
import hmac
import numpy as np
from time import sleep, time
from datetime import datetime, timezone
from requests import get, post
from quantfreedom.enums import ExchangeSettings, LeverageModeType, PositionModeType, TriggerDirectionType
from quantfreedom.exchanges.bybit_exchange.bybit_github.unified_trading import HTTP

from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES, Exchange

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

    def get_exchange_timeframe(
        self,
        timeframe: str,
    ):
        try:
            return BYBIT_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
        except Exception as e:
            raise Exception(f"Use one of these timeframes - {UNIVERSAL_TIMEFRAMES} -> {e}")

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
        end_point = "/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": ex_timeframe,
            "start": since_timestamp,
            "end": until_timestamp,
            "limit": 1000,
        }

        while params["end"] - self.timeframe_in_ms > since_timestamp:
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

        candles = np.flip(np.array(candles_list, dtype=np.float_)[:, :-1], axis=0)
        self.last_fetched_ms_time = int(candles[-1, 0])

        return candles

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
        triggerPrice: float = None,
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

    def create_long_hedge_mode_entry_market_order(
        self,
        asset_size: float,
        symbol: str,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=1,
            buy_sell="Buy",
            order_type="Market",
            asset_size=asset_size,
            time_in_force="GTC",
        )

    def create_long_hedge_mode_tp_limit_order(
        self,
        asset_size: float,
        symbol: str,
        tp_price: float,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=1,
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
        trigger_price: float,
    ):
        return self.create_order(
            symbol=symbol,
            position_mode=1,
            buy_sell="Sell",
            order_type="Market",
            asset_size=asset_size,
            triggerPrice=trigger_price,
            reduce_only=True,
            triggerDirection=TriggerDirectionType.Fall,
            time_in_force="GTC",
        )

    def get_position_info(
        self,
        symbol: str,
        baseCoin: str = None,
        category: str = "linear",
        limit: int = 50,
        settleCoin: str = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/position
        """
        end_point = "/v5/position/list"
        params = {}
        params["symbol"] = symbol
        params["limit"] = limit
        params["settleCoin"] = settleCoin
        params["baseCoin"] = baseCoin
        params["category"] = category
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["result"]["list"][0]
            data_list = response["result"]["list"]

            return data_list
        except Exception as e:
            raise Exception(f"Bybit get_account_position_info = Data or List is empty {response['retMsg']} -> {e}")

    def get_long_hedge_mode_position_info(
        self,
        symbol: str,
    ):
        return self.get_position_info(symbol=symbol)[0]

    def get_wallet_info(
        self,
        accountType: str = "CONTRACT",
        trading_with: str = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/account/wallet-balance
        """
        end_point = "/v5/account/wallet-balance"

        params = {}
        params["accountType"] = accountType
        params["coin"] = trading_with

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["result"]["list"]
            data_list[0]
            return data_list
        except Exception as e:
            raise Exception(f"Bybit get_wallet_info = Data or List is empty {response['retMsg']} -> {e}")

    def get_equity_of_asset(
        self,
        accountType: str = "CONTRACT",
        trading_with: str = None,
    ):
        return float(self.get_wallet_info(accountType=accountType, trading_with=trading_with)[0]["coin"][0]["equity"])

    def get_closed_pnl(
        self,
        symbol: str,
        limit: int = 50,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        category: str = "linear",
    ):
        """
        [Bybit API link to Get Closed Profit and Loss](https://bybit-exchange.github.io/docs/v5/position/close-pnl)
        """

        if since_datetime is not None:
            since_datetime = int(since_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
        if until_datetime is not None:
            until_datetime = int(until_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)

        end_point = "/v5/position/closed-pnl"
        params = {}
        params["category"] = category
        params["symbol"] = symbol
        params["limit"] = limit
        params["startTime"] = since_datetime
        params["endTime"] = until_datetime

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["result"]["list"][0]
            data_list = response["result"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"Data or List is empty {response['retMsg']} -> {e}")

    def get_latest_pnl_result(
        self,
        symbol: str,
        category: str = "linear",
    ):
        return float(self.get_closed_pnl(category=category, symbol=symbol)[0]["closedPnl"])

    def get_order_history(
        self,
        baseCoin: str = None,
        category: str = "linear",
        custom_order_id: str = None,
        limit: int = 50,
        orderFilter: str = None,
        orderStatus: str = None,
        order_id: str = None,
        settleCoin: str = None,
        since_datetime: datetime = None,
        symbol: str = None,
        until_datetime: datetime = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/order/order-list
        """
        if since_datetime is not None:
            since_datetime = int(since_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)
        if until_datetime is not None:
            until_datetime = int(until_datetime.replace(tzinfo=timezone.utc).timestamp() * 1000)

        end_point = "/v5/order/history"
        params = {}
        params["baseCoin"] = baseCoin
        params["category"] = category
        params["endTime"] = until_datetime
        params["limit"] = limit
        params["orderFilter"] = orderFilter
        params["orderId"] = order_id
        params["orderLinkId"] = custom_order_id
        params["orderStatus"] = orderStatus
        params["settleCoin"] = settleCoin
        params["startTime"] = since_datetime
        params["symbol"] = symbol
        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["result"]["list"]
            data_list[0]  # try this to see if anything is in here
            return data_list
        except Exception as e:
            raise Exception(f"Bybit get_order_history = Data or List is empty {response['retMsg']} -> {e}")

    def check_if_order_open(
        self,
        order_id: str,
        symbol: str = None,
    ):
        data_list = self.get_order_history(order_id=order_id)
        try:
            if data_list[0]["orderId"] == order_id:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Bybit check_if_order_canceled -> {e}")

    def get_filled_order_by_order_id(
        self,
        order_id: str,
        symbol: str = None,
    ):
        return self.get_order_history(order_id=order_id)[0]

    def get_open_order_by_order_id(
        self,
        order_id: str,
        symbol: str = None,
    ):
        return self.get_order_history(order_id=order_id)[0]

    def check_if_order_filled(
        self,
        order_id: str,
        symbol: str = None,
    ):
        data_dict = self.get_filled_order_by_order_id(order_id=order_id)
        try:
            if data_dict["orderId"] == order_id:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"bybit check_if_order_filled -> {e}")

    def cancel_all_open_orders(
        self,
        symbol: str = None,
        category: str = "linear",
        baseCoin: str = None,
        settleCoin: str = None,
        orderFilter: str = None,
        stopOrderType: str = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/order/cancel-all
        """
        end_point = "/v5/order/cancel-all"
        params = {}
        params["symbol"] = symbol
        params["stopOrderType"] = stopOrderType
        params["orderFilter"] = orderFilter
        params["settleCoin"] = settleCoin
        params["baseCoin"] = baseCoin
        params["category"] = category
        try:
            response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
            if response["retMsg"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Bybit cancel_all_open_orders_per_symbol message = {response['retMsg']} -> {e}")

    def cancel_all_open_orders_per_symbol(
        self,
        symbol: str,
    ):
        return self.cancel_all_open_orders(symbol=symbol)

    def set_leverage(
        self,
        symbol: str,
        leverage: float,
        category: str = "linear",
    ):
        """
        https://bybit-exchange.github.io/docs/v5/position/leverage
        """
        end_point = "/v5/position/set-leverage"
        leverage_str = str(leverage)

        params = {}
        params["symbol"] = symbol
        params["category"] = category
        params["buyLeverage"] = leverage_str
        params["sellLeverage"] = leverage_str

        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["retMsg"] in ["OK", "Set leverage not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Bybit set_leverage = Data or List is empty {response['retMsg']} -> {e}")

    def set_leverage_mode(
        self,
        symbol: str,
        leverage_mode: LeverageModeType,
        category: str = "linear",
        leverage: int = 5,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/position/cross-isolate
        Cross/isolated mode. 0: cross margin mode; 1: isolated margin mode
        """
        end_point = "/v5/position/switch-isolated"
        leverage_str = str(leverage)
        params = {}
        params["symbol"] = symbol
        params["category"] = category
        params["tradeMode"] = leverage_mode
        params["buyLeverage"] = leverage_str
        params["sellLeverage"] = leverage_str
        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["retMsg"] in ["OK", "Cross/isolated margin mode is not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Bybit set_leverage_mode = Data or List is empty {response['retMsg']} -> {e}")

    def adjust_order(
        self,
        symbol: str,
        asset_size: float = None,
        category: str = "linear",
        custom_order_id: str = None,
        orderIv: str = None,
        order_id: str = None,
        price: float = None,
        slLimitPrice: float = None,
        slTriggerBy: float = None,
        stopLoss: float = None,
        takeProfit: float = None,
        tpLimitPrice: float = None,
        tpslMode: str = None,
        tpTriggerBy: float = None,
        triggerBy: float = None,
        triggerPrice: float = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/order/amend-order
        """
        end_point = "/v5/order/amend"
        params = {}
        params["category"] = category
        params["orderId"] = order_id
        params["orderIv"] = orderIv
        params["orderLinkId"] = custom_order_id
        params["price"] = str(price) if price else price
        params["qty"] = str(asset_size)
        params["slLimitPrice"] = str(slLimitPrice) if slLimitPrice else slLimitPrice
        params["slTriggerBy"] = str(slTriggerBy) if slTriggerBy else slTriggerBy
        params["stopLoss"] = str(stopLoss) if stopLoss else stopLoss
        params["symbol"] = symbol.upper()
        params["takeProfit"] = str(takeProfit) if takeProfit else takeProfit
        params["tpLimitPrice"] = str(tpLimitPrice) if tpLimitPrice else tpLimitPrice
        params["tpLimitPrice"] = str(tpLimitPrice) if tpLimitPrice else tpLimitPrice
        params["tpslMode"] = tpslMode
        params["tpTriggerBy"] = str(tpTriggerBy) if tpTriggerBy else tpTriggerBy
        params["triggerBy"] = str(triggerBy) if triggerBy else triggerBy
        params["triggerPrice"] = str(triggerPrice) if triggerPrice else triggerPrice

        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            response_order_id = response["result"]["orderId"]
            if response_order_id == order_id or response["retMsg"] == "OK":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"bybit adjust_order message = {response['retMsg']} -> {e}")

    def move_stop_order(
        self,
        symbol: str,
        order_id: str,
        new_price: float,
        asset_size: float,
    ):
        return self.adjust_order(
            symbol=symbol,
            order_id=order_id,
            triggerPrice=new_price,
            asset_size=asset_size,
        )

    def get_risk_limit_info(
        self,
        symbol: str,
        category: str = "linear",
    ):
        """
        [Bybit API link to Get Risk Limit](https://bybit-exchange.github.io/docs/v5/market/risk-limit)
        """
        end_point = "/v5/market/risk-limit"
        params = {}
        params["symbol"] = symbol
        params["category"] = category

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["result"]["list"][0]

            return data_list
        except Exception as e:
            raise Exception(f"Bybit get_risk_limit_info = Data or List is empty {response['retMsg']} -> {e}")

    def __get_mmr_pct(
        self,
        symbol: str,
        category: str = "linear",
    ):
        risk_limit_info = self.get_risk_limit_info(symbol=symbol, category=category)
        mmr_pct = float(risk_limit_info["maintenanceMargin"])

        return mmr_pct

    def set_position_mode(
        self,
        position_mode: PositionModeType,
        symbol: str,
        category: str = "linear",
        trading_with: str = None,
    ):
        """
        https://bybit-exchange.github.io/docs/v5/position/position-mode
        """
        end_point = "/v5/position/switch-mode"

        params = {}
        params["category"] = category
        params["symbol"] = symbol
        params["coin"] = trading_with
        params["mode"] = position_mode

        response: dict = self.__HTTP_post_request(end_point=end_point, params=params)
        try:
            if response["retMsg"] in ["OK", "Position mode is not modified"]:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Bybit set_position_mode - {response['retMsg']} -> {e}")

    def get_all_symbols_info(
        self,
        category: str = "linear",
        limit: int = 500,
        symbol: str = None,
        status: str = None,
        baseCoin: str = None,
    ):
        """
        [Bybit API link to Get Instrument Info](https://bybit-exchange.github.io/docs/v5/market/instrument)
        """
        end_point = "/v5/market/instruments-info"

        params = {}
        params["limit"] = limit
        params["category"] = category
        params["symbol"] = symbol.upper()
        params["status"] = status
        params["baseCoin"] = baseCoin

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            response["result"]["list"][0]
            data_list = response["result"]["list"]

            return data_list
        except Exception as e:
            raise Exception(f"Bybit get_all_symbols_info = Data or List is empty {response['retMsg']} -> {e}")

    def __get_min_max_leverage_and_asset_size(
        self,
        symbol: str,
    ):
        symbol_info = self.get_all_symbols_info(symbol=symbol)[0]
        max_leverage = float(symbol_info["leverageFilter"]["maxLeverage"])
        min_leverage = float(symbol_info["leverageFilter"]["minLeverage"])
        max_asset_size = float(symbol_info["lotSizeFilter"]["maxOrderQty"])
        min_asset_size = float(symbol_info["lotSizeFilter"]["minOrderQty"])
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

    def get_trading_fee_rates(
        self,
        symbol: str = None,
        baseCoin: str = None,
        category: str = "linear",
    ):
        """
        https://bybit-exchange.github.io/docs/v5/account/fee-rate
        """
        end_point = "/v5/account/fee-rate"

        params = {}
        params["symbol"] = symbol
        params["category"] = category
        params["baseCoin"] = baseCoin

        response: dict = self.__HTTP_get_request(end_point=end_point, params=params)
        try:
            data_list = response["result"]["list"]
            return data_list
        except Exception as e:
            raise Exception(f"bybit get_symbol_trading_fee_rates {response['retMsg']} -> {e}")

    def get_symbol_trading_fee_rates(
        self,
        symbol: str,
        baseCoin: str = None,
        category: str = "linear",
    ):
        return self.get_trading_fee_rates(symbol=symbol, baseCoin=baseCoin, category=category)[0]

    def __get_fee_pcts(
        self,
        symbol: str,
    ):
        trading_fee_info = self.get_symbol_trading_fee_rates(symbol=symbol)
        market_fee_pct = float(trading_fee_info["takerFeeRate"])
        limit_fee_pct = float(trading_fee_info["makerFeeRate"])

        return market_fee_pct, limit_fee_pct

    def set_leverage_mode_cross(
        self,
        symbol: str,
    ):
        true_false = self.set_leverage_mode(symbol=symbol, leverage_mode=0)

        return true_false

    def set_leverage_mode_isolated(
        self,
        symbol: str,
    ):
        true_false = self.set_leverage_mode(symbol=symbol, leverage_mode=1)

        return true_false

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

    def set_exchange_settings(
        self,
        leverage_mode: LeverageModeType,
        position_mode: PositionModeType,
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
