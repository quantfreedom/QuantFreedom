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
    'SL_BE_andTrailBasedOn',
    'LeverageMode',
    'SizeType',
    'TestTuple',
    'Order',
    'LogAndOrderRecords',

    'log_records_dt',
    'order_records_dt',
    'ready_for_df',
    'cart_array_dt',
]

class RejectedOrderError(Exception):
    """Rejected order error."""
    pass

class SL_BE_andTrailBasedOnT(tp.NamedTuple):
    open_price: int = 0
    high_price: int = 1
    low_price: int = 2
    close_price: int = 3


SL_BE_andTrailBasedOn = SL_BE_andTrailBasedOnT()


class TestTuple(tp.NamedTuple):
    order_records: tp.ArrayLike = np.nan
    order_count_id: int = -1


class LogAndOrderRecords(tp.NamedTuple):
    bar: int = 0
    indicator_settings_counter: int = 0
    order_count_id: int = 0
    order_records_filled: int = 0
    order_records: tp.RecordArray = np.nan
    order_settings_counter: int = 0
    log_count_id: tp.Optional[int] = None
    log_records_filled: tp.Optional[int] = None
    log_records: tp.Optional[tp.RecordArray] = None


class AccountState(tp.NamedTuple):
    available_balance: float = 0.
    cash_borrowed: float = 0.
    cash_used: float = 0.
    equity: float = 0.
    fee_pct: float = 0.06
    mmr: float = .5


class OrderResult(tp.NamedTuple):
    average_entry_order_result: float = 0.
    fees_paid_order_result: float = 0.
    leverage_auto_order_result: float = 0.
    liq_price_order_result: float = 0.
    moved_sl_to_be_order_result: bool = False
    moved_tsl_order_result: bool = False
    order_status_info_order_result: int = 0
    order_status_order_result: int = 0
    order_type_order_result: float = 0.
    pct_chg_order_result: float = 0.
    position_order_result: float = 0.
    realized_pnl_order_result: float = 0.
    size_value_order_result: float = 0.
    sl_pcts_order_result: float = 0.
    sl_prices_order_result: float = 0.
    tp_pcts_order_result: float = 0.
    tp_prices_order_result: float = 0.
    tsl_pcts_order_result: float = 0.
    tsl_prices_order_result: float = 0.


class Order(tp.NamedTuple):
    lev_mode_order: int = 0
    leverage_iso_order: float = 0.
    max_equity_risk_pct_order: float = np.nan
    max_equity_risk_value_order: float = np.nan
    max_lev_order: float = 100.
    max_order_size_pct_order: float = 100.
    max_order_size_value_order: float = np.inf
    min_order_size_pct_order: float = .01
    min_order_size_value_order: float = 1.
    order_type_order: int = 0
    risk_rewards_order: float = np.nan
    size_pct_order: float = np.nan
    size_type_order: int = 0
    size_value_order: float = np.nan
    sl_be_then_trail_order: bool = False
    sl_pcts_order: float = np.nan
    sl_prices_order: float = np.nan
    sl_to_be_order: bool = False
    sl_to_be_based_on_order: float = np.nan
    sl_to_be_then_trail_order: bool = False
    sl_to_be_trail_when_pct_from_avg_entry_order: float = np.nan
    sl_to_be_when_pct_from_avg_entry_order: float = np.nan
    sl_to_be_zero_or_entry_order: float = np.nan
    slippage_pct_order: float = np.nan
    tp_pcts_order: float = np.nan
    tp_prices_order: float = np.nan
    tsl_based_on_order: float = np.nan
    tsl_pcts_order: float = np.nan
    tsl_prices_order: float = np.nan
    tsl_trail_by_order: float = np.nan
    tsl_true_or_false_order: bool = False
    tsl_when_pct_from_avg_entry_order: float = np.nan


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
"""
A numpy array with specific data types that allow you to store specific information about your order result.

This is different from order records as log records is ment to store a lot of information about every order, \
    where order records is just for the filled orders and the needed info for plotting and other stuff.
"""
