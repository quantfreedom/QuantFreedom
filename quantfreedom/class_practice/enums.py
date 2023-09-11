import numpy as np
from quantfreedom._typing import NamedTuple


class CandleBodyTypeT(NamedTuple):
    Nothing: int = 0
    Open: int = 1
    High: int = 2
    Low: int = 3
    Close: int = 4


CandleBodyType = CandleBodyTypeT()


class IncreasePositionTypeT(NamedTuple):
    Nothing: int = 0
    AmountEntrySize: int = 1
    PctAccountEntrySize: int = 2
    RiskAmountEntrySize: int = 3
    RiskPctAccountEntrySize: int = 4


IncreasePositionType = IncreasePositionTypeT()

class LeverageTypeT(NamedTuple):
    Nothing: int = 0
    Static: int = 1
    Dynamic: int = 2


LeverageType = LeverageTypeT()


class SLToBeZeroOrEntryTypeT(NamedTuple):
    Nothing = 0
    ZeroLoss = 1
    AverageEntry = 2


SLToBeZeroOrEntryType = SLToBeZeroOrEntryTypeT()


class OrderStatusT(NamedTuple):
    Nothing: int = 0
    EntryFilled: int = 1
    StopLossFilled: int = 2
    TakeProfitFilled: int = 3
    MovedStopLossToBE: int = 4
    MovedTrailingStopLoss: int = 5
    MaxEquityRisk: int = 6
    RiskToBig: int = 7
    CashUsedExceed: int = 8


OrderStatus = OrderStatusT()


class OrderTypeT(NamedTuple):
    Nothing: int = 0
    Long: int = 1
    Short: int = 2
    Both: int = 3


OrderType = OrderTypeT()


class StopLossTypeT(NamedTuple):
    Nothing: int = 0
    SLBasedOnCandleBody: int = 1
    SLPct: int = 2


StopLossType = StopLossTypeT()


class TakeProfitTypeT(NamedTuple):
    Nothing: int = 0
    RiskReward: int = 1
    TPPct: int = 2
    Provided: int = 3


TakeProfitType = TakeProfitTypeT()


class AccountState(NamedTuple):
    available_balance: float = 1000.0
    cash_borrowed: float = 0.0
    cash_used: float = 0.0
    equity: float = 1000.0


class BacktestSettings(NamedTuple):
    divide_records_array_size_by: float = 1.0
    gains_pct_filter: float = -np.inf
    total_trade_filter: int = 0
    upside_filter: float = -1.0


class ExchangeSettings(NamedTuple):
    market_fee_pct: float = 0.06 / 100
    limit_fee_pct: float = 0.02 / 100
    mmr_pct: float = 0.5 / 100
    max_lev: float = 100.0
    max_order_size_pct: float = 100.0
    max_order_size_value: float = np.inf
    min_order_size_pct: float = 0.01
    min_order_size_value: float = 1.0


class OrderSettingsArrays(NamedTuple):
    risk_account_pct_size: np.array
    sl_based_on_add_pct: np.array
    sl_based_on_lookback: np.array
    risk_reward: np.array
    leverage_type: np.array
    sl_candle_body_type: np.array
    increase_position_type: np.array
    stop_loss_type: np.array
    take_profit_type: np.array
    max_equity_risk_pct: np.array
    order_type: np.array
    sl_to_be_based_on_candle_body_type: np.array
    sl_to_be_when_pct_from_candle_body: np.array
    sl_to_be_zero_or_entry: np.array
    trail_sl_based_on_candle_body_type: np.array
    trail_sl_by_pct: np.array
    trail_sl_when_pct_from_candle_body: np.array


class OrderSettings(NamedTuple):
    risk_account_pct_size: float
    sl_based_on_add_pct: float
    sl_based_on_lookback: int
    risk_reward: float
    leverage_type: int
    sl_candle_body_type: int
    increase_position_type: int
    stop_loss_type: int
    take_profit_type: int
    max_equity_risk_pct: float
    order_type: int
    sl_to_be_based_on_candle_body_type: int
    sl_to_be_when_pct_from_candle_body: float
    sl_to_be_zero_or_entry: int
    trail_sl_based_on_candle_body_type: int
    trail_sl_by_pct: float
    trail_sl_when_pct_from_candle_body: float



class OrderResult(NamedTuple):
    average_entry: float = 0.0
    fees_paid: float = 0.0
    leverage: float = 1.0
    liq_price: float = 0.0
    order_status: int = 0
    possible_loss: float = 0.0
    entry_size: float = 0.0
    entry_price: float = 0.0
    position_size: float = 0.0
    realized_pnl: float = 0.0
    sl_pct: float = 0.0
    sl_price: float = 0.0
    tp_pct: float = 0.0
    tp_price: float = 0.0


class RejectedOrderError(Exception):
    """Rejected order error."""

    order_status = None

    def __init__(self, order_status: OrderStatus):
        self.order_status = order_status
