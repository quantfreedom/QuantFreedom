"""
Enums
!!! warning
    ☠️:warning:THIS IS A MASSIVE MASSIVE WARNING.:warning:☠️

    Make sure you follow what the variable types are. If it says float you have to make sure you put a \
        decimal like 1. or 3., or if it says int that you make sure there are no decimals.
    
    If you do not follow exactly what the type says for you to do then numba will start crying and wont run your code.


    Then you will be sitting there for hours trying to debug what is wrong and then you will find out it is because you put
    a number as an int instead of a float

!!! danger
    All inputs requiring you to tell it what percent you want something to be should be put in like 1. for 1% or 50. for 50%.

    If you put .01 for 1% the math will calculate it as .0001. 

"""

import numpy as np

from quantfreedom import _typing as tp

__all__ = [
    'AccountState',
    'OrderStatusInfo',
    'OrderStatus',
    'OrderResult',
    'OrderType',
    'RejectedOrderError',
    'SL_BE_or_Trail_BasedOn',
    'LeverageMode',
    'SizeType',
    'EntryOrder',
    'StopsOrder',
    'StaticVariables',

    'or_dt',
    'df_array_dt',
    'strat_dt',
    'cart_array_dt',
]


class AccountState(tp.NamedTuple):
    available_balance: float = 0.
    cash_borrowed: float = 0.
    cash_used: float = 0.
    equity: float = 0.


class EntryOrder(tp.NamedTuple):
    leverage: float = 0.
    max_equity_risk_pct: float = np.nan
    max_equity_risk_value: float = np.nan
    order_type: int = 0
    risk_rewards: float = np.nan
    size_pct: float = np.nan
    size_value: float = np.nan
    sl_pcts: float = np.nan
    tp_pcts: float = np.nan
    tsl_pcts_init: float = np.nan


class OrderResult(tp.NamedTuple):
    average_entry: float = 0.
    fees_paid: float = 0.
    leverage: float = 0.
    liq_price: float = np.nan
    moved_sl_to_be: bool = False
    order_status: int = 0
    order_status_info: int = 0
    order_type: int = 0
    pct_chg_trade: float = 0.
    position: float = 0.
    price: float = 0.
    realized_pnl: float = 0.
    size_value: float = 0.
    sl_pcts: float = 0.
    sl_prices: float = 0.
    tp_pcts: float = 0.
    tp_prices: float = 0.
    tsl_pcts_init: float = 0.
    tsl_prices: float = 0.


class StaticVariables(tp.NamedTuple):
    lev_mode: int
    size_type: int
    fee_pct: float = .0006
    max_lev: float = 100.
    max_order_size_pct: float = 1.
    min_order_size_pct: float = .0001
    max_order_size_value: float = np.inf
    min_order_size_value: float = 1.
    mmr: float = .005


class StopsOrder(tp.NamedTuple):
    sl_to_be: bool = False
    sl_to_be_based_on: float = np.nan
    sl_to_be_then_trail: bool = False
    sl_to_be_trail_by_when_pct_from_avg_entry: float = np.nan
    sl_to_be_when_pct_from_avg_entry: float = np.nan
    sl_to_be_zero_or_entry: float = np.nan
    tsl_based_on: float = np.nan
    tsl_trail_by_pct: float = np.nan
    tsl_true_or_false: bool = False
    tsl_when_pct_from_avg_entry: float = np.nan


class LeverageModeT(tp.NamedTuple):
    Isolated: int = 0
    LeastFreeCashUsed: int = 1


LeverageMode = LeverageModeT()


class OrderStatusT(tp.NamedTuple):
    Filled: int = 0
    Ignored: int = 1
    Rejected: int = 2


OrderStatus = OrderStatusT()


class OrderStatusInfoT(tp.NamedTuple):
    HopefullyNoProblems: int = 0
    MaxEquityRisk: int = 1


OrderStatusInfo = OrderStatusInfoT()


class OrderTypeT(tp.NamedTuple):
    LongEntry: int = 0
    ShortEntry: int = 1
    Both: int = 2

    LongLiq: int = 3
    LongSL: int = 4
    LongTP: int = 5
    LongTSL: int = 6

    ShortLiq: int = 7
    ShortSL: int = 8
    ShortTP: int = 9
    ShortTSL: int = 10

    MovedSLtoBE: int = 11
    MovedTSL: int = 12


OrderType = OrderTypeT()


class SL_BE_or_Trail_BasedOnT(tp.NamedTuple):
    open_price: int = 0
    high_price: int = 1
    low_price: int = 2
    close_price: int = 3


SL_BE_or_Trail_BasedOn = SL_BE_or_Trail_BasedOnT()


class SizeTypeT(tp.NamedTuple):
    Amount: int = 0
    PercentOfAccount: int = 1
    RiskAmount: int = 2
    RiskPercentOfAccount: int = 3


SizeType = SizeTypeT()

# ############# Records ############# #

df_array_dt = np.dtype([
    ('or_set', np.int_),
    ('ind_set', np.int_),
    ('win_rate', np.float_),
    ('gains_pct', np.float_),
    ('to_the_upside', np.float_),
    ('total_trades', np.float_),
    ('total_BE', np.int_),
    ('total_fees', np.float_),
    ('total_pnl', np.float_),
    ('ending_eq', np.float_),
], align=True)

strat_array_dt = np.dtype([
    ('or_set', np.int_),
    ('ind_set', np.int_),
    ('total_trades', np.float_),
    ('gains_pct', np.float_),
    ('win_rate', np.float_),
    ('to_the_upside', np.float_),
    ('total_pnl', np.float_),
    ('ending_eq', np.float_),
], align=True)


cart_array_dt = np.dtype([
    ('order_settings_id', np.int_),
    ('leverage', np.float_),
    ('max_equity_risk_pct', np.float_),
    ('max_equity_risk_value', np.float_),
    ('risk_rewards', np.float_),
    ('size_pct', np.float_),
    ('size_value', np.float_),
    ('sl_pcts', np.float_),
    ('sl_to_be_based_on', np.float_),
    ('sl_to_be_trail_by_when_pct_from_avg_entry', np.float_),
    ('sl_to_be_when_pct_from_avg_entry', np.float_),
    ('sl_to_be_zero_or_entry', np.float_),
    ('tp_pcts', np.float_),
    ('tsl_based_on', np.float_),
    ('tsl_pcts_init', np.float_),
    ('tsl_trail_by_pct', np.float_),
    ('tsl_when_pct_from_avg_entry', np.float_),
], align=True)
"""
A numpy array with specific data types that allow you to store specific information about your order result
"""

strat_dt = np.dtype([
    ('or_set', np.int_),
    ('ind_set', np.int_),
    ('real_pnl', np.float_),
    ('equity', np.float_),
], align=True)

or_dt = np.dtype([
    ('order_id', np.int_),
    ('or_set', np.int_),
    ('ind_set', np.int_),
    ('bar', np.int_),
    ('size_value', np.float_),
    ('price', np.float_),
    ('avg_entry', np.float_),
    ('fees_paid', np.float_),
    ('order_type', np.float_),
    ('real_pnl', np.float_),
    ('equity', np.float_),
    ('sl_prices', np.float_),
    ('tsl_prices', np.float_),
    ('tp_prices', np.float_),
], align=True)


class RejectedOrderError(Exception):
    """Rejected order error."""
    pass