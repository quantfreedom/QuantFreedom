import numpy as np
from quantfreedom._typing import NamedTuple


class CandleBodyType(NamedTuple):
    Nothing: int = 0
    Open: int = 1
    High: int = 2
    Low: int = 3
    Close: int = 4


class EntrySizeType(NamedTuple):
    Nothing: int = 0
    AmountEntrySize: int = 1
    PctAccountEntrySize: int = 2
    RiskAmountEntrySize: int = 3
    RiskPctAccountEntrySize: int = 4


class LeverageType(NamedTuple):
    Nothing: int = 0
    Static: int = 1.0
    Dynamic: int = 2.0


class OrderStatus(NamedTuple):
    Nothing: int = 0
    EntryFilled: int = 1
    StopLossFilled: int = 2
    TakeProfitFilled: int = 3
    MovedStopLossToBE: int = 4
    MovedTrailingStopLoss: int = 5
    MaxEquityRisk: int = 6
    RiskToBig: int = 7
    CashUsedExceed: int = 8


class OrderType(NamedTuple):
    Nothing: int = 0
    Long: int = 1
    Short: int = 2
    Both: int = 3


class StopLossType(NamedTuple):
    Nothing: int = 0
    SLBasedOnCandleBody: int = 1
    SLPct: int = 2


class TakeProfitType(NamedTuple):
    Nothing: int = 0
    RiskReward: int = 1
    TPPct: int = 2


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
    candle_body_type: np.array
    entry_size_type: np.array
    stop_loss_type: np.array
    take_profit_type: np.array
    max_equity_risk_pct: np.array
    order_type: np.array


class OrderSettings(NamedTuple):
    risk_account_pct_size: float
    sl_based_on_add_pct: float
    sl_based_on_lookback: float
    risk_reward: float
    leverage_type: int
    candle_body_type: int
    entry_size_type: int
    stop_loss_type: int
    take_profit_type: int
    max_equity_risk_pct: float
    order_type: int


class OrderResult(NamedTuple):
    average_entry: float
    fees_paid: float
    leverage: float
    liq_price: float
    order_status: int
    possible_loss: float
    entry_size: float
    entry_price: float
    exit_price: float
    position_size: float
    realized_pnl: float
    sl_pct: float
    sl_price: float
    tp_pct: float
    tp_price: float


class RejectedOrderError(Exception):
    """Rejected order error."""

    order_status = None

    def __init__(self, order_status: OrderStatus):
        self.order_status = order_status
