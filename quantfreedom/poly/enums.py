from quantfreedom._typing import NamedTuple


class OrderSettings(NamedTuple):
    risk_account_pct_size: float = 1.0 / 100
    sl_based_on_add_pct: float = .01 / 100


class AccountState(NamedTuple):
    available_balance: float = 1000.0
    cash_borrowed: float = 0.0
    cash_used: float = 0.0
    equity: float = 1000.0

class ExchangeSettings(NamedTuple):
    market_fee_pct: float = .06 / 100
    limit_fee_pct: float = .02 / 100
