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
    'LogAndOrderRecords',
    'StaticVariables',

    'log_records_dt',
    'order_records_dt',
    'ready_for_df',
    'cart_array_dt',
]


class AccountState(tp.NamedTuple):
    available_balance: float = 0.
    cash_borrowed: float = 0.
    cash_used: float = 0.
    equity: float = 0.


class EntryOrder(tp.NamedTuple):
    leverage_iso: float = 0.
    max_equity_risk_pct: float = np.nan
    max_equity_risk_value: float = np.nan
    order_type: int = 0
    risk_rewards: float = np.nan
    size_pct: float = np.nan
    size_value: float = np.nan
    sl_pcts: float = np.nan
    sl_prices: float = np.nan
    tp_pcts: float = np.nan
    tp_prices: float = np.nan
    tsl_pcts: float = np.nan
    tsl_prices: float = np.nan


class LogAndOrderRecords(tp.NamedTuple):
    bar: int = 0
    indicator_settings_counter: int = 0
    order_count_id: int = 0
    order_records_filled: int = 0
    order_settings_counter: int = 0
    log_count_id: tp.Optional[int] = None
    log_records_filled: tp.Optional[int] = None


class OrderResult(tp.NamedTuple):
    average_entry: float = 0.
    fees_paid: float = 0.
    leverage_auto: float = 0.
    liq_price: float = np.nan
    moved_sl_to_be: bool = False
    moved_tsl: bool = False
    order_status: int = 0
    order_status_info: int = 0
    order_type: float = 0.
    pct_chg: float = 0.
    position: float = 0.
    realized_pnl: float = 0.
    size_value: float = 0.
    sl_pcts: float = 0.
    sl_prices: float = 0.
    tp_pcts: float = 0.
    tp_prices: float = 0.
    tsl_pcts: float = 0.
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
    sl_to_be_trail_when_pct_from_avg_entry: float = np.nan
    sl_to_be_when_pct_from_avg_entry: float = np.nan
    sl_to_be_zero_or_entry: float = np.nan
    tsl_based_on: float = np.nan
    tsl_trail_by: float = np.nan
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

ready_for_df = np.dtype([
    ('or_set', np.int_),
    ('ind_set', np.int_),
    ('total_trades', np.float_),
    ('total_BE', np.int_),
    ('gains_pct', np.float_),
    ('win_rate', np.float_),
    ('to_the_upside', np.float_),
    ('total_fees', np.float_),
    ('total_pnl', np.float_),
    ('ending_eq', np.float_),
    ('sl_pct', np.float_),
    ('rr', np.float_),
    ('max_eq_risk_pct', np.float_),
], align=True)

cart_array_dt = np.dtype([
    ('leverage_array', np.float_),
    ('max_equity_risk_pct_array', np.float_),
    ('max_equity_risk_value_array', np.float_),
    ('risk_rewards_array', np.float_),
    ('size_pct_array', np.float_),
    ('size_value_array', np.float_),
    ('sl_pcts_array', np.float_),
    ('sl_prices_array', np.float_),
    ('sl_to_be_array', np.float_),
    ('sl_to_be_based_on_array', np.float_),
    ('sl_to_be_then_trail_array', np.float_),
    ('sl_to_be_trail_when_pct_from_avg_entry_array', np.float_),
    ('sl_to_be_when_pct_from_avg_entry_array', np.float_),
    ('sl_to_be_zero_or_entry_array', np.float_),
    ('tp_pcts_array', np.float_),
    ('tp_prices_array', np.float_),
    ('tsl_based_on_array', np.float_),
    ('tsl_pcts_array', np.float_),
    ('tsl_prices_array', np.float_),
    ('tsl_trail_by_array', np.float_),
    ('tsl_true_or_false_array', np.float_),
    ('tsl_when_pct_from_avg_entry_array', np.float_),
], align=True)
"""
A numpy array with specific data types that allow you to store specific information about your order result
"""

order_records_dt = np.dtype([
    ('id', np.int_),
    ('col', np.int_),
    ('equity', np.float_),
    ('fees', np.float_),
    ('idx', np.int_),
    ('ind_set', np.int_),
    ('max_eq_risk_pct', np.float_),
    ('or_set', np.int_),
    ('price', np.float_),
    ('real_pnl', np.float_),
    ('rr', np.float_),
    ('side', np.float_),
    ('size', np.float_),
    ('size_usd', np.float_),
    ('sl_pct', np.float_),
], align=True)

log_records_dt = np.dtype([
    ('bar', np.int_),
    ('col', np.int_),
    ('id_order', np.int_),
    ('id_log', np.int_),
    ('order_price', np.float_),
    ('order_type', np.float_),
    ('avg_entry', np.float_),
    ('sl_prices', np.float_),
    ('tsl_prices', np.float_),
    ('tp_prices', np.float_),
    ('real_pnl', np.float_),

], align=True)


class RejectedOrderError(Exception):
    """Rejected order error."""
    pass
