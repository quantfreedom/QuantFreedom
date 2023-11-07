import hashlib
import hmac
import base64
import numpy as np
from datetime import timedelta
from requests import get, post
from time import sleep, time
from quantfreedom.exchanges.apex_exchange.apex_github.http_private_stark_key_sign import HttpPrivateStark
from quantfreedom.exchanges.apex_exchange.apex_github.constants import NETWORKID_TEST, NETWORKID_MAIN
from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionModeType,
)
from quantfreedom.exchanges.exchange import Exchange

APEX_TIMEFRAMES = [1, 5, 15, 30, 60, 120, 240, 360, 720, "D", "W", "M"]


class Apex(Exchange):
    def __init__(
        # Exchange Vars
        self,
        api_key: str,
        secret_key: str,
        passphrase: str,
        stark_key_public: str,
        stark_key_private: str,
        stark_key_y: str,
        use_test_net: bool,
    ):
        """
        main docs page https://api-docs.pro.apex.exchange
        """
        super().__init__(api_key, secret_key, use_test_net)

        if use_test_net:
            url_start = "https://testnet.pro.apex.exchange"
            # network_id = NETWORKID_TEST
        else:
            url_start = "https://pro.apex.exchange"
            # network_id = NETWORKID_MAIN

        self.apex_stark = HttpPrivateStark(
            endpoint=url_start,
            # network_id=network_id,
            stark_public_key=stark_key_public,
            stark_private_key=stark_key_private,
            stark_public_key_y_coordinate=stark_key_y,
            api_key_credentials={"key": api_key, "secret": secret_key, "passphrase": passphrase},
        )
        self.apex_stark.configs()
        self.apex_stark.get_account()

    def create_order(
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
        sourceFlag=None,
    ):
        return self.apex_stark.create_order(
            symbol=symbol,
            side=side,
            type=type,
            size=size,
            limitFeeRate=limitFeeRate,
            limitFee=limitFee,
            price=price,
            accountId=accountId,
            timeInForce=timeInForce,
            reduceOnly=reduceOnly,
            triggerPrice=triggerPrice,
            triggerPriceType=triggerPriceType,
            trailingPercent=trailingPercent,
            clientId=clientId,
            expiration=expiration,
            expirationEpochSeconds=expirationEpochSeconds,
            isPositionTpsl=isPositionTpsl,
            signature=signature,
            sourceFlag=sourceFlag,
        )
