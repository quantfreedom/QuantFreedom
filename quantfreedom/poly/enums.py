import numpy as np
from quantfreedom._typing import NamedTuple


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


class CandleBody(NamedTuple):
    Open = 1
    High = 2
    Low = 3
    Close = 4


class EntrySizeType(NamedTuple):
    AmountEntrySize = 1
    PctAccountEntrySize = 2
    RiskAmountEntrySize = 3
    RiskPctAccountEntrySize = 4


class ExchangeSettings(NamedTuple):
    market_fee_pct: float = 0.06 / 100
    limit_fee_pct: float = 0.02 / 100
    mmr_pct: float = 0.5 / 100
    max_lev: float = 100.0
    max_order_size_pct: float = 100.0
    max_order_size_value: float = np.inf
    min_order_size_pct: float = 0.01
    min_order_size_value: float = 1.0


class LeverageType(NamedTuple):
    Static = 1
    Dynamic = 2


class OrderSettingsArrays(NamedTuple):
    risk_account_pct_size: np.array = np.nan
    sl_based_on_add_pct: np.array = np.nan


class OrderSettings(NamedTuple):
    risk_account_pct_size: float = 1.0 / 100
    sl_based_on_add_pct: float = 0.01 / 100


class OrderType(NamedTuple):
    Long = 1
    Short = 2


class StopLossType(NamedTuple):
    SLBasedOnCandleBody = 1
    SLPct = 2


class TakeProfitType(NamedTuple):
    RiskReward = 1
    TPPct = 2
