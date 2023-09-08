import numpy as np
from quantfreedom._typing import NamedTuple


class CandleBody(NamedTuple):
    Open = 1.0
    High = 2.0
    Low = 3.0
    Close = 4.0


class EntrySizeType(NamedTuple):
    AmountEntrySize = 1.0
    PctAccountEntrySize = 2.0
    RiskAmountEntrySize = 3.0
    RiskPctAccountEntrySize = 4.0


class LeverageType(NamedTuple):
    Static = 1.0
    Dynamic = 2.0


class OrderType(NamedTuple):
    Long = 1
    Short = 2


class StopLossType(NamedTuple):
    SLBasedOnCandleBody = 1.0
    SLPct = 2.0


class TakeProfitType(NamedTuple):
    RiskReward = 1.0
    TPPct = 2.0


class AccountState(NamedTuple):
    available_balance: float = 1000.0
    cash_borrowed: float = 0.0
    cash_used: float = 0.0
    equity: float = 1000.0


class BacktestSettings(NamedTuple):
    order_type: int
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
    risk_account_pct_size: np.array = np.array(np.nan)
    sl_based_on_add_pct: np.array = np.array(np.nan)
    sl_based_on_lookback: np.array = np.array(np.nan)
    risk_reward: np.array = np.array(np.nan)
    leverage_type: np.array = np.array(np.nan)
    candle_body: np.array = np.array(np.nan)
    entry_size_type: np.array = np.array(np.nan)
    stop_loss_type: np.array = np.array(np.nan)
    take_profit_type: np.array = np.array(np.nan)
    max_equity_risk_pct: np.array = np.array(np.nan)


class OrderSettings(NamedTuple):
    risk_account_pct_size: float
    sl_based_on_add_pct: float
    sl_based_on_lookback: float
    risk_reward: float
    leverage_type: float
    candle_body: float
    entry_size_type: float
    stop_loss_type: float
    take_profit_type: float
    max_equity_risk_pct: float


class OrderResult(NamedTuple):
    average_entry: float
    fees_paid: float
    leverage: float
    liq_price: float
    order_status: int
    order_status_info: int
    possible_loss: float
    pct_chg_trade: float
    entry_size: float
    entry_price: float
    position_size: float
    realized_pnl: float
    sl_pct: float
    sl_price: float
    tp_pct: float
    tp_price: float


class OrderStatusInfo(NamedTuple):
    Filled: int = 0
    Ignored: int = 1
    Rejected: int = 2
    HopefullyNoProblems: int = 3
    MaxEquityRisk: int = 4
    RiskToBig: int = 5
