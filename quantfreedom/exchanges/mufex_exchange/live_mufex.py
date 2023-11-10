from time import sleep
from uuid import uuid4
import numpy as np
from quantfreedom.enums import LeverageModeType, LongOrShortType, PositionModeType, TriggerDirectionType
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES
from quantfreedom.exchanges.live_exchange import LiveExchange
from quantfreedom.exchanges.mufex_exchange.mufex import MUFEX_TIMEFRAMES, Mufex


class LiveMufex(LiveExchange, Mufex):
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        symbol: str,
        timeframe: str,
        trading_with: str,
        use_test_net: bool,
        candles_to_dl: int = None,
        position_mode: PositionModeType = PositionModeType.HedgeMode,
        leverage_mode: LeverageModeType = LeverageModeType.Isolated,
    ):
        self.timeframe = MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]

        if position_mode == PositionModeType.HedgeMode:
            self.set_position_mode_as_hedge_mode(symbol=self.symbol)
        else:
            self.set_position_mode_as_one_way_mode(symbol=self.symbol)

        if leverage_mode == LeverageModeType.Isolated:
            self.set_leverage_mode_isolated(symbol=self.symbol)
        elif leverage_mode == LeverageModeType.Cross:
            self.set_leverage_mode_cross(symbol=self.symbol)

        self.candles_to_dl_ms = candles_to_dl * self.timeframe_in_ms

        self.set_exchange_settings(
            symbol=symbol,
            position_mode=position_mode,
            leverage_mode=leverage_mode,
        )

    def check_long_hedge_mode_if_in_position(
        self,
    ):
        if float(self.get_position_info(symbol=self.symbol)[0]["entryPrice"]) > 0:
            return True
        else:
            return False

    def create_long_hedge_mode_entry_market_order(
        self,
        asset_size: float,
    ):
        return self.create_order(
            symbol=self.symbol,
            position_mode=1,
            buy_sell="Buy",
            order_type="Market",
            asset_size=asset_size,
            time_in_force="GoodTillCancel",
        )

    def create_long_hedge_mode_tp_limit_order(
        self,
        asset_size: float,
        tp_price: float,
    ):
        return self.create_order(
            symbol=self.symbol,
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
        trigger_price: float,
    ):
        return self.create_order(
            symbol=self.symbol,
            position_mode=1,
            buy_sell="Sell",
            order_type="Market",
            asset_size=asset_size,
            triggerPrice=trigger_price,
            reduce_only=True,
            triggerDirection=TriggerDirectionType.Fall,
            time_in_force="GoodTillCancel",
        )

    def get_long_hedge_mode_position_info(self):
        return self.get_position_info(symbol=self.symbol)[0]
