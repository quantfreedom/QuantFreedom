import numpy as np

from quantfreedom._typing import NamedTuple, Array1d, PossibleArray

__all__ = [
    "AccountState",
    "OrderStatusInfo",
    "OrderStatus",
    "OrderResult",
    "OrderType",
    "RejectedOrderError",
    "CandleBody",
    "LeverageMode",
    "SizeType",
    "EntryOrder",
    "StopsOrder",
    "StaticVariables",
    "OrderSettingsArrays",
    "OrderSettings",
    "PriceTuple",
    "or_dt",
    "strat_df_array_dt",
    "order_settings_array_dt",
    "final_array_dt",
    "strat_records_dt",
]


class AccountState(NamedTuple):
    available_balance: float = 0.0
    cash_borrowed: float = 0.0
    cash_used: float = 0.0
    equity: float = 0.0


class StaticVariables(NamedTuple):
    equity: float
    lev_mode: int
    order_type: int
    size_type: int
    divide_records_array_size_by: float = 1.0
    fee_pct: float = 0.06
    gains_pct_filter: float = -np.inf
    max_lev: float = 100.0
    max_order_size_pct: float = 100.0
    max_order_size_value: float = np.inf
    min_order_size_pct: float = 0.01
    min_order_size_value: float = 1.0
    mmr_pct: float = 0.5
    total_trade_filter: int = 0
    upside_filter: float = -1.0


class OrderResult(NamedTuple):
    average_entry: float = 0.0
    fees_paid: float = 0.0
    leverage: float = 0.0
    liq_price: float = np.nan
    moved_sl_to_be: bool = False
    order_status: int = 0
    order_status_info: int = 0
    order_type: int = 0
    pct_chg_trade: float = 0.0
    position: float = 0.0
    price: float = 0.0
    realized_pnl: float = 0.0
    size_value: float = 0.0
    sl_pct: float = 0.0
    sl_price: float = 0.0
    tp_pct: float = 0.0
    tp_price: float = 0.0


class PriceTuple(NamedTuple):
    open: float = np.nan
    high: float = np.nan
    low: float = np.nan
    close: float = np.nan


class OrderSettingsArrays(NamedTuple):
    leverage: PossibleArray = np.nan
    max_equity_risk_pct: PossibleArray = np.nan
    max_equity_risk_value: PossibleArray = np.nan
    risk_reward: PossibleArray = np.nan
    size_pct: PossibleArray = np.nan
    size_value: PossibleArray = np.nan
    sl_based_on: PossibleArray = np.nan
    sl_based_on_add_pct: PossibleArray = np.nan
    sl_based_on_lookback: PossibleArray = np.nan
    sl_pct: PossibleArray = np.nan
    sl_to_be_based_on: PossibleArray = np.nan
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan
    sl_to_be_zero_or_entry: PossibleArray = np.nan
    tp_pct: PossibleArray = np.nan
    trail_sl_based_on: PossibleArray = np.nan
    trail_sl_by_pct: PossibleArray = np.nan
    trail_sl_when_pct_from_avg_entry: PossibleArray = np.nan


class OrderSettings(NamedTuple):
    leverage: float = np.nan
    max_equity_risk_pct: float = np.nan
    max_equity_risk_value: float = np.nan
    risk_reward: float = np.nan
    size_pct: float = np.nan
    size_value: float = np.nan
    sl_based_on: float = np.nan
    sl_based_on_add_pct: float = np.nan
    sl_based_on_lookback: float = np.nan
    sl_pct: float = np.nan
    sl_to_be_based_on: float = np.nan
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan
    sl_to_be_zero_or_entry: float = np.nan
    tp_pct: float = np.nan
    trail_sl_based_on: float = np.nan
    trail_sl_by_pct: float = np.nan
    trail_sl_when_pct_from_avg_entry: float = np.nan


class LeverageModeT(NamedTuple):
    Isolated: int = 0
    LeastFreeCashUsed: int = 1


LeverageMode = LeverageModeT()


class OrderStatusT(NamedTuple):
    Filled: int = 0
    Ignored: int = 1
    Rejected: int = 2


OrderStatus = OrderStatusT()


class OrderStatusInfoT(NamedTuple):
    HopefullyNoProblems: int = 0
    MaxEquityRisk: int = 1


OrderStatusInfo = OrderStatusInfoT()


class OrderTypeT(NamedTuple):
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


class CandleBodyT(NamedTuple):
    open: int = 0
    high: int = 1
    low: int = 2
    close: int = 3


CandleBody = CandleBodyT()


class SizeTypeT(NamedTuple):
    Amount: int = 0
    PercentOfAccount: int = 1
    RiskAmount: int = 2
    RiskPercentOfAccount: int = 3


SizeType = SizeTypeT()

# ############# Records ############# #

strat_df_array_dt = np.dtype(
    [
        ("symbol", np.int_),
        ("entries_col", np.int_),
        ("or_set", np.int_),
        ("total_trades", np.float_),
        ("gains_pct", np.float_),
        ("win_rate", np.float_),
        ("to_the_upside", np.float_),
        ("total_pnl", np.float_),
        ("ending_eq", np.float_),
    ],
    align=True,
)

order_settings_array_dt = np.dtype(
    [
        ("symbol", np.int_),
        ("entries_col", np.int_),
        ("leverage", np.float_),
        ("max_equity_risk_pct", np.float_),
        ("max_equity_risk_value", np.float_),
        ("risk_reward", np.float_),
        ("size_pct", np.float_),
        ("size_value", np.float_),
        ("sl_based_on", np.float_),
        ("sl_based_on_add_pct", np.float_),
        ("sl_based_on_lookback", np.float_),
        ("sl_pct", np.float_),
        ("sl_to_be_based_on", np.float_),
        ("sl_to_be_when_pct_from_avg_entry", np.float_),
        ("sl_to_be_zero_or_entry", np.float_),
        ("tp_pct", np.float_),
        ("trail_sl_based_on", np.float_),
        ("trail_sl_by_pct", np.float_),
        ("trail_sl_when_pct_from_avg_entry", np.float_),
    ],
    align=True,
)

strat_records_dt = np.dtype(
    [
        ("symbol", np.int_),
        ("entries_col", np.int_),
        ("or_set", np.int_),
        ("real_pnl", np.float_),
        ("equity", np.float_),
    ],
    align=True,
)


or_dt = np.dtype(
    [
        ("order_id", np.int_),
        ("order_set_id", np.int_),
        ("bar", np.int_),
        ("size_value", np.float_),
        ("price", np.float_),
        ("avg_entry", np.float_),
        ("fees_paid", np.float_),
        ("order_type", np.float_),
        ("real_pnl", np.float_),
        ("equity", np.float_),
        ("sl_price", np.float_),
        ("tp_price", np.float_),
    ],
    align=True,
)


class RejectedOrderError(Exception):
    """Rejected order error."""

    pass
