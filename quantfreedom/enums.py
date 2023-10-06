from typing import NamedTuple
import numpy as np


class CandleProcessingTypeT(NamedTuple):
    RegularBacktest: int = 0
    BacktestCandleByCandle: int = 1
    LiveTrading: int = 2


CandleProcessingType = CandleProcessingTypeT()


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


class LeverageModeTypeT(NamedTuple):
    Cross: int = 0
    Isolated: int = 1


LeverageModeType = LeverageModeTypeT()


class LeverageStrategyTypeT(NamedTuple):
    Nothing: int = 0
    Static: int = 1
    Dynamic: int = 2


LeverageStrategyType = LeverageStrategyTypeT()


class OrderPlacementTypeT(NamedTuple):
    Limit: int = 0
    Market: int = 1


OrderPlacementType = OrderPlacementTypeT()


class OrderStatusT(NamedTuple):
    Nothing: int = 0
    EntryFilled: int = 1
    StopLossFilled: int = 2
    TakeProfitFilled: int = 3
    LiquidationFilled: int = 4
    MovedStopLossToBE: int = 5
    MovedTrailingStopLoss: int = 6
    MaxEquityRisk: int = 7
    RiskToBig: int = 8
    CashUsedExceed: int = 9
    EntrySizeTooSmall: int = 10
    EntrySizeTooBig: int = 11
    PossibleLossTooBig: int = 12


OrderStatus = OrderStatusT()


class LongOrShortTypeT(NamedTuple):
    Long: int = 0
    Short: int = 1


LongOrShortType = LongOrShortTypeT()


class PositionModeTypeT(NamedTuple):
    OneWayMode: int = 0
    HedgeMode: int = 1


PositionModeType = PositionModeTypeT()


class SLToBeZeroOrEntryTypeT(NamedTuple):
    Nothing: int = 0
    ZeroLoss: int = 1
    AverageEntry: int = 2


SLToBeZeroOrEntryType = SLToBeZeroOrEntryTypeT()


class StopLossStrategyTypeT(NamedTuple):
    Nothing: int = 0
    SLBasedOnCandleBody: int = 1
    SLPct: int = 2


StopLossStrategyType = StopLossStrategyTypeT()


class TakeProfitFeeTypeT(NamedTuple):
    Nothing: int = 0
    Limit: int = 1
    Market: int = 2


TakeProfitFeeType = TakeProfitFeeTypeT()


class TakeProfitStrategyTypeT(NamedTuple):
    Nothing: int = 0
    RiskReward: int = 1
    TPPct: int = 2
    Provided: int = 3
    ProvidedandPct: int = 4
    ProvidedandRR: int = 5


TakeProfitStrategyType = TakeProfitStrategyTypeT()


class TriggerDirectionTypeT(NamedTuple):
    Rise: int = 1
    Fall: int = 2


TriggerDirectionType = TriggerDirectionTypeT()


class AccountState(NamedTuple):
    available_balance: float = 1000.0
    cash_borrowed: float = 0.0
    cash_used: float = 0.0
    equity: float = 1000.0


class BacktestSettings(NamedTuple):
    divide_records_array_size_by: float = 1.0
    gains_pct_filter: float = -np.inf
    total_trade_filter: int = 0
    upside_filter: float = -np.inf


class ExchangeSettings(NamedTuple):
    limit_fee_pct: float = None
    max_leverage: float = None
    market_fee_pct: float = None
    mmr_pct: float = None
    min_leverage: float = None
    max_asset_size: float = None
    min_asset_size: float = None
    asset_tick_step: float = None
    position_mode: int = None
    leverage_mode: int = None
    price_tick_step: float = None
    leverage_tick_step: float = None


class OrderSettingsArrays(NamedTuple):
    increase_position_type: np.array
    leverage_type: np.array
    max_equity_risk_pct: np.array
    long_or_short: np.array
    risk_account_pct_size: np.array
    risk_reward: np.array
    sl_based_on_add_pct: np.array
    sl_based_on_lookback: np.array
    sl_candle_body_type: np.array
    sl_to_be_based_on_candle_body_type: np.array
    sl_to_be_when_pct_from_candle_body: np.array
    sl_to_be_zero_or_entry_type: np.array
    static_leverage: np.array
    stop_loss_type: np.array
    take_profit_type: np.array
    tp_fee_type: np.array
    trail_sl_based_on_candle_body_type: np.array
    trail_sl_by_pct: np.array
    trail_sl_when_pct_from_candle_body: np.array


class OrderSettings(NamedTuple):
    increase_position_type: int
    leverage_type: int
    max_equity_risk_pct: float
    long_or_short: int
    risk_account_pct_size: float
    risk_reward: float
    sl_based_on_add_pct: float
    sl_based_on_lookback: int
    sl_candle_body_type: int
    sl_to_be_based_on_candle_body_type: int
    sl_to_be_when_pct_from_candle_body: float
    sl_to_be_zero_or_entry_type: int
    static_leverage: float
    stop_loss_type: int
    take_profit_type: int
    tp_fee_type: int
    trail_sl_based_on_candle_body_type: int
    trail_sl_by_pct: float
    trail_sl_when_pct_from_candle_body: float


class OrderResult(NamedTuple):
    indicator_settings_index: int
    order_settings_index: int
    bar_index: int
    equity: float = np.nan
    available_balance: float = np.nan
    cash_borrowed: float = np.nan
    cash_used: float = np.nan
    average_entry: float = np.nan
    fees_paid: float = np.nan
    leverage: float = np.nan
    liq_price: float = np.nan
    order_status: int = np.nan
    possible_loss: float = np.nan
    entry_size_usd: float = np.nan
    entry_price: float = np.nan
    exit_price: float = np.nan
    position_size_usd: float = np.nan
    realized_pnl: float = np.nan
    sl_pct: float = np.nan
    sl_price: float = np.nan
    tp_pct: float = np.nan
    tp_price: float = np.nan


class RejectedOrder(Exception):
    def __init__(
        self,
        order_status: OrderStatus = None,
        msg: str = None,
    ):
        self.order_status = order_status
        self.msg = msg


class DecreasePosition(Exception):
    def __init__(
        self,
        order_status: OrderStatus = None,
        exit_price: float = None,
        exit_fee_pct: float = None,
        msg: str = None,
    ):
        self.order_status = order_status
        self.exit_price = exit_price
        self.exit_fee_pct = exit_fee_pct
        self.msg = msg


class MoveStopLoss(Exception):
    def __init__(
        self,
        order_status: OrderStatus = None,
        sl_price: float = None,
        can_move_sl_to_be: bool = None,
        msg: str = None,
    ):
        self.order_status = order_status
        self.sl_price = sl_price
        self.can_move_sl_to_be = can_move_sl_to_be
        self.msg = msg


order_settings_array_dt = np.dtype(
    [
        ("or_set_idx", np.int_),
        ("increase_position_type", np.int_),
        ("leverage_type", np.int_),
        ("max_equity_risk_pct", np.float_),
        ("long_or_short", np.int_),
        ("risk_account_pct_size", np.float_),
        ("risk_reward", np.float_),
        ("sl_based_on_add_pct", np.float_),
        ("sl_based_on_lookback", np.int_),
        ("sl_candle_body_type", np.int_),
        ("sl_to_be_based_on_candle_body_type", np.int_),
        ("sl_to_be_when_pct_from_candle_body", np.float_),
        ("sl_to_be_zero_or_entry_type", np.int_),
        ("static_leverage", np.float_),
        ("stop_loss_type", np.int_),
        ("take_profit_type", np.int_),
        ("tp_fee_type", np.int_),
        ("trail_sl_based_on_candle_body_type", np.int_),
        ("trail_sl_by_pct", np.float_),
        ("trail_sl_when_pct_from_candle_body", np.float_),
    ],
    align=True,
)


or_dt = np.dtype(
    [
        ("ind_set_idx", np.int_),
        ("or_set_idx", np.int_),
        ("bar_idx", np.int_),
        ("equity", np.float_),
        ("available_balance", np.float_),
        ("cash_borrowed", np.float_),
        ("cash_used", np.float_),
        ("average_entry", np.float_),
        ("fees_paid", np.float_),
        ("leverage", np.float_),
        ("liq_price", np.float_),
        ("order_status", np.int_),
        ("possible_loss", np.float_),
        ("entry_size_usd", np.float_),
        ("entry_price", np.float_),
        ("exit_price", np.float_),
        ("position_size_usd", np.float_),
        ("realized_pnl", np.float_),
        ("sl_pct", np.float_),
        ("sl_price", np.float_),
        ("tp_pct", np.float_),
        ("tp_price", np.float_),
    ],
    align=True,
)

strat_df_array_dt = np.dtype(
    [
        ("ind_set_idx", np.int_),
        ("or_set_idx", np.int_),
        ("total_trades", np.float_),
        ("gains_pct", np.float_),
        ("win_rate", np.float_),
        ("to_the_upside", np.float_),
        ("total_pnl", np.float_),
        ("ending_eq", np.float_),
    ],
    align=True,
)

strat_records_dt = np.dtype(
    [
        ("equity", np.float_),
        ("bar_idx", np.int_),
        ("or_set_idx", np.int_),
        ("ind_set_idx", np.int_),
        ("real_pnl", np.float_),
    ],
    align=True,
)
