from quantfreedom.exchanges.apex_exchange.apex_github.http_private_stark_key_sign import HttpPrivateStark
from quantfreedom.exchanges.apex_exchange.apex_github.http_public import HttpPublic
from quantfreedom.exchanges.exchange import Exchange
from time import sleep, time
import numpy as np
from datetime import datetime


APEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W"]


class Apex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        use_test_net: bool,
        api_key: str = None,
        secret_key: str = None,
        passphrase: str = None,
        stark_key_public: str = None,
        stark_key_private: str = None,
        stark_key_y: str = None,
    ):
        """
        main docs page https://api-docs.pro.apex.exchange
        """
        if use_test_net:
            url_start = "https://testnet.pro.apex.exchange"
        else:
            url_start = "https://pro.apex.exchange"

        if api_key is None:
            self.apex_ex = HttpPublic(endpoint=url_start)
        else:
            self.apex_ex = HttpPrivateStark(
                endpoint=url_start,
                stark_public_key=stark_key_public,
                stark_private_key=stark_key_private,
                stark_public_key_y_coordinate=stark_key_y,
                api_key_credentials={"key": api_key, "secret": secret_key, "passphrase": passphrase},
            )
            self.apex_ex.configs_v2()
            self.apex_ex.get_account_v2()
            self.limitFeeRate = self.apex_ex.get_account()["data"]["takerFeeRate"]

    def create_order(
        self,
        symbol: str,
        buy_sell: str,
        order_type: str,
        asset_size: float,
        limitFeeRate=None,
        limitFee=None,
        price: float = None,
        accountId=None,
        time_in_force: str = "GOOD_TIL_CANCEL",
        reduceOnly=False,
        triggerPrice=None,
        triggerPriceType=None,
        trailingPercent=None,
        clientId=None,
        expiration=None,
        isPositionTpsl=False,
        signature=None,
        sourceFlag=None,
    ):
        """
        [Apex API for Creating Orders](https://api-docs.pro.apex.exchange/#privateapi-post-creating-orders)
        """
        return self.apex_ex.create_order_v2(
            symbol=symbol,
            side=buy_sell.upper(),
            type=order_type.upper(),
            size=str(asset_size),
            limitFeeRate=limitFeeRate,
            limitFee=limitFee,
            price=price,
            accountId=accountId,
            timeInForce=time_in_force,
            reduceOnly=reduceOnly,
            triggerPrice=triggerPrice,
            triggerPriceType=triggerPriceType,
            trailingPercent=trailingPercent,
            clientId=clientId,
            expiration=expiration,
            expirationEpochSeconds=time(),
            isPositionTpsl=isPositionTpsl,
            signature=signature,
            sourceFlag=sourceFlag,
        )

    def create_entry_market_order(
        self,
        symbol: str,
        buy_sell: str,
        asset_size: float,
    ):
        try:
            price = self.apex_ex.get_worst_price(symbol=symbol, side=buy_sell.upper(), size="0.1")["data"]["worstPrice"]
            response_data = self.create_order(
                symbol=symbol,
                buy_sell=buy_sell,
                order_type="market",
                asset_size=asset_size,
                price=price,
                limitFeeRate=self.limitFeeRate,
            )
            order_id = response_data["data"]["id"]
            return order_id
        except Exception as e:
            raise Exception(f"Apex create_entry_market_order -> {e}")

    def create_entry_limit_order(
        self,
        symbol: str,
        buy_sell: str,
        asset_size: float,
        price: float,
    ):
        try:
            response_data = self.create_order(
                symbol=symbol,
                buy_sell=buy_sell,
                order_type="limit",
                asset_size=asset_size,
                price=str(price),
                limitFeeRate=self.limitFeeRate,
                time_in_force="POST_ONLY",
            )
            order_id = response_data["data"]["id"]
            return order_id
        except Exception as e:
            raise Exception(f"Apex create_entry_limit_order -> {e}")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        since_datetime: datetime = None,
        until_datetime: datetime = None,
        candles_to_dl: int = 200,
    ):
        """
        Summary
        -------
        [Apex candle docs](https://api-docs.pro.apex.exchange/#publicapi_v2-get-candlestick-chart-data-v2)

        Explainer Video
        ---------------
        Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

        Parameters
        ----------
        symbol : str
            [Use APEX API for symbol list](https://api-docs.pro.apex.exchange/#introduction)
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
        symbol = symbol.replace("-", "")
        ex_timeframe = self.get_exchange_timeframe(ex_timeframes=APEX_TIMEFRAMES, timeframe=timeframe)
        timeframe_in_ms = self.get_timeframe_in_ms(timeframe=timeframe)
        candles_to_dl_ms = candles_to_dl * timeframe_in_ms

        since_timestamp, until_timestamp = self.get_since_until_timestamp(
            candles_to_dl_ms=candles_to_dl_ms,
            since_datetime=since_datetime,
            timeframe_in_ms=timeframe_in_ms,
            until_datetime=until_datetime,
        )

        apex_candles = []
        while since_timestamp + timeframe_in_ms < until_timestamp:
            try:
                apex_data = self.apex_ex.klines(
                    symbol=symbol,
                    interval=ex_timeframe,
                    start=int(since_timestamp / 1000),
                    end=int(until_timestamp / 1000),
                    limit=200,
                )
                apex_candle_list = apex_data["data"][symbol]
                last_candle_timestamp = apex_candle_list[-1]["t"]
                if last_candle_timestamp == since_timestamp:
                    sleep(0.2)
                else:
                    apex_candles.extend(apex_candle_list)
                    since_timestamp = last_candle_timestamp + 2000
            except Exception as e:
                raise Exception(f"Apex get_candles - > {e}")

        candle_list = []
        keys = ["t", "o", "h", "l", "c", "v"]
        for candle in apex_candles:
            candle_list.append([candle.get(key) for key in keys])
        candles_np = np.array(candle_list, dtype=np.float_)
        return candles_np

    def get_closed_pnl(
        self,
        beginTimeInclusive: int = None,
        endTimeExclusive: int = None,
        pos_type: str = None,
        symbol: str = None,
        page: int = None,
        limit: int = None,
    ):
        return (
            self.apex_ex.historical_pnl(
                beginTimeInclusive=beginTimeInclusive,
                endTimeExclusive=endTimeExclusive,
                type=pos_type,
                symbol=symbol,
                page=page,
                limit=limit,
            )
            .get("data")
            .get("historicalPnl")
        )

    def get_latest_pnl_result(self, symbol: str):
        return float(self.get_closed_pnl(symbol=symbol)[0].get("totalPnl"))

    def get_wallet_info_of_asset(self):
        return self.apex_ex.get_account()

    def account_data(self):
        return self.apex_ex.get_account()

    def get_equity_of_asset(self, **kwargs):
        return float(self.apex_ex.get_account_balance()["data"]["totalEquityValue"])

    def check_if_order_filled(self, order_id: str, **kwargs):
        try:
            if self.apex_ex.get_order(id=order_id)["data"]["status"] == "FILLED":
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Apex check_if_order_filled -> {e}")

    def cancel_all_open_orders_per_symbol(self, symbol: str):
        try:
            if self.apex_ex.delete_open_orders(symbol=symbol).get("code") is None:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Apex cancel_all_open_orders_per_symbol -> {e}")

    def cancel_open_order(self, order_id: str):
        try:
            if self.apex_ex.delete_order(id=order_id).get("data") == order_id:
                return True
            else:
                raise Exception
        except Exception as e:
            raise Exception(f"Apex cancel_open_order -> {e}")

    def set_leverage(self, symbol: str, leverage: float):
        """
        [Apex API for initial margin rate of a contract](https://api-docs.pro.apex.exchange/#privateapi-post-sets-the-initial-margin-rate-of-a-contract)
        """
        new_leverage = round(leverage, 2)
        initialMarginRate = str(round(1 / new_leverage, 5))

        response = self.apex_ex.set_initial_margin_rate_v2(symbol=symbol, initialMarginRate=initialMarginRate)
        try:
            if type(response.get("timeCost")) == int:
                return True
            else:
                return False
        except Exception as e:
            raise Exception(f"Apex set_leverage -> {e}")
