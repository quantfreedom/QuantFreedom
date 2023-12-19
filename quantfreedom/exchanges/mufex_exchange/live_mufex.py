from quantfreedom.enums import LeverageModeType, PositionModeType, TriggerDirectionType
from quantfreedom.exchanges.exchange import UNIVERSAL_TIMEFRAMES
from quantfreedom.exchanges.live_exchange import LiveExchange
from quantfreedom.exchanges.mufex_exchange.mufex import MUFEX_TIMEFRAMES, Mufex


class LiveMufex(LiveExchange, Mufex):
    def __init__(
        self,
        api_key: str,
        candles_to_dl: int,
        secret_key: str,
        symbol: str,
        timeframe: str,
        trading_with: str,
        use_test_net: bool,
    ):
        self.timeframe = MUFEX_TIMEFRAMES[UNIVERSAL_TIMEFRAMES.index(timeframe)]
    