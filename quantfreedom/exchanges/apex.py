from datetime import timedelta
from quantfreedom.enums import ExchangeSettings
from quantfreedom.exchanges.apex_github.apexpro.constants import NETWORKID_TEST
from quantfreedom.exchanges.apex_github.apexpro.http_private import HttpPrivate
from quantfreedom.exchanges.apex_github.apexpro.http_private_stark_key_sign import HttpPrivateStark
from quantfreedom.exchanges.apex_github.apexpro.http_public import HttpPublic

APEX_TIMEFRAMES = ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"]
UNIVERSAL_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "d", "w", "m"]


class Apex:
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        api_key: str,
        secret_key: str,
        passphrase: str,
        stark_private_key: str,
        stark_public_key: str,
        stark_public_key_y_coordinate: str,
        keep_volume_in_candles: bool = False,
        use_test_net: bool = False,
    ):
        self.symbol = symbol
        self.volume_yes_no = -2
        if use_test_net:
            self.url_start = "https://testnet.pro.apex.exchange"
            self.network_id = NETWORKID_TEST
        else:
            self.url_start = "https://pro.apex.exchange"
            self.network_id = NETWORKID_TEST

        self.__set_exchange_settings()
        # self.__set_position_mode(position_mode=position_mode)

        if keep_volume_in_candles:
            self.volume_yes_no = -1
        try:
            self.timeframe = APEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
            self.timeframe_in_ms = timedelta(minutes=self.timeframe).seconds * 1000
        except:
            raise TypeError(f"You need to send the following {UNIVERSAL_TIMEFRAMES}")

        self.public_client = HttpPublic(endpoint=self.url_start)
        self.public_configs = self.public_client.configs()

        self.private_client = HttpPrivate(
            endpoint=self.url_start,
            network_id=self.network_id,
            api_key_credentials={
                "key": api_key,
                "secret": secret_key,
                "passphrase": passphrase,
            },
        )
        self.private_configs = self.private_client.configs()
        self.private_configs.get_user()

        self.private_stark_client = HttpPrivateStark(
            endpoint=self.url_start,
            network_id=self.network_id,
            stark_private_key=stark_private_key,
            stark_public_key=stark_public_key,
            stark_public_key_y_coordinate=stark_public_key_y_coordinate,
            api_key_credentials={
                "key": api_key,
                "secret": secret_key,
                "passphrase": passphrase,
            },
        )
        self.private_configs = self.private_client.configs()
        self.private_configs.get_user()

    def create_limit_entry_order(
        self,
        symbol,
        side,
        type,
        size,
        limitFeeRate=None,
        limitFee=None,
        price=None,
        accountId=None,
        timeInForce="GOOD_TIL_CANCEL",
        reduceOnly=False,
        triggerPrice=None,
        triggerPriceType=None,
        trailingPercent=None,
        clientId=None,
        expiration=None,
        expirationEpochSeconds=None,
        isPositionTpsl=False,
        signature=None,
    ):
        self.private_stark_client.create_order(
            symbol,
            side,
            type,
            size,
            limitFeeRate=None,
            limitFee=None,
            price=None,
            accountId=None,
            timeInForce="GOOD_TIL_CANCEL",
            reduceOnly=False,
            triggerPrice=None,
            triggerPriceType=None,
            trailingPercent=None,
            clientId=None,
            expiration=None,
            expirationEpochSeconds=None,
            isPositionTpsl=False,
            signature=None,
        )

    def __set_exchange_settings(self):
        account_info = self.private_client.get_account_v2()['data']['accounts'][0]
        self.__set_mmr_pct()
        self.__set_min_max_leverage_and_coin_size()
        self.exchange_settings = ExchangeSettings(
            market_fee_pct=float(account_info['takerFeeRate']),
            limit_fee_pct=float(account_info['makerFeeRate']),
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