from typing import NamedTuple
import numpy as np
import os
from numba.experimental import jitclass


class CandleProcessingTypeT(NamedTuple):
    Backtest: int = 0
    LiveTrading: int = 1


CandleProcessingType = CandleProcessingTypeT()


class CandleBodyTypeT(NamedTuple):
    Timestamp: int = 0
    Open: int = 1
    High: int = 2
    Low: int = 3
    Close: int = 4
    Volume: int = 5
    Nothing: int = 6


CandleBodyType = CandleBodyTypeT()


class IncreasePositionTypeT(NamedTuple):
    Nothing: int = 0
    AmountEntrySize: int = 1
    PctAccountEntrySize: int = 2
    RiskAmountEntrySize: int = 3
    RiskPctAccountEntrySize: int = 4
    SmalletEntrySizeAsset: int = 5


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
    HitMaxTrades: int = 0
    EntryFilled: int = 1
    StopLossFilled: int = 2
    TakeProfitFilled: int = 3
    LiquidationFilled: int = 4
    MovedSLToBE: int = 5
    MovedTSL: int = 6
    MaxEquityRisk: int = 7
    RiskToBig: int = 8
    CashUsedExceed: int = 9
    EntrySizeTooSmall: int = 10
    EntrySizeTooBig: int = 11
    PossibleLossTooBig: int = 12
    Nothing: int = 13


OrderStatus = OrderStatusT()


class LoggerTypeT(NamedTuple):
    Disable: int = 0
    Print: int = 1
    File: int = 2


LoggerType = LoggerTypeT()

class LongOrShortTypeT(NamedTuple):
    Long: int = 0
    Short: int = 1


LongOrShortType = LongOrShortTypeT()


class PositionModeTypeT(NamedTuple):
    OneWayMode: int = 0
    HedgeMode: int = 1


PositionModeType = PositionModeTypeT()


class PriceGetterTypeT(NamedTuple):
    Min: int = 0
    Max: int = 1
    Nothing: int = 2


PriceGetterType = PriceGetterTypeT()


class StopLossStrategyTypeT(NamedTuple):
    SLBasedOnCandleBody: int = 0
    Nothing: int = 1


StopLossStrategyType = StopLossStrategyTypeT()


class TakeProfitFeeTypeT(NamedTuple):
    Nothing: int = 0
    Limit: int = 1
    Market: int = 2


TakeProfitFeeType = TakeProfitFeeTypeT()


class TakeProfitStrategyTypeT(NamedTuple):
    ProvidedandRR: int = 0
    RiskReward: int = 1
    TPPct: int = 2
    Provided: int = 3
    ProvidedandPct: int = 4
    Nothing: int = 5


TakeProfitStrategyType = TakeProfitStrategyTypeT()


class TriggerDirectionTypeT(NamedTuple):
    Rise: int = 1
    Fall: int = 2


TriggerDirectionType = TriggerDirectionTypeT()


class ZeroOrEntryTypeT(NamedTuple):
    ZeroLoss: int = 0
    AverageEntry: int = 1
    Nothing: int = 2


ZeroOrEntryType = ZeroOrEntryTypeT()


############################################################
############################################################
############################################################
############################################################
############################################################
############################################################
############################################################
############################################################
############################################################
############################################################


class BacktestSettings(NamedTuple):
    divide_records_array_size_by: float = 1.0
    gains_pct_filter: float = -np.inf
    total_trade_filter: int = -1
    upside_filter: float = -np.inf


class ExchangeSettings(NamedTuple):
    limit_fee_pct: float = None
    max_leverage: float = None
    market_fee_pct: float = None
    mmr_pct: float = None
    min_leverage: float = None
    max_asset_size: float = None
    min_asset_size: float = None
    asset_tick_step: int = None
    position_mode: int = None
    leverage_mode: int = None
    price_tick_step: int = None
    leverage_tick_step: int = None


class DynamicOrderSettingsArrays(NamedTuple):
    entry_size_asset: np.array
    max_equity_risk_pct: np.array
    max_trades: np.array
    num_candles: np.array
    risk_account_pct_size: np.array
    risk_reward: np.array
    sl_based_on_add_pct: np.array
    sl_based_on_lookback: np.array
    sl_bcb_type: np.array
    sl_to_be_cb_type: np.array
    sl_to_be_when_pct: np.array
    sl_to_be_ze_type: np.array
    static_leverage: np.array
    trail_sl_bcb_type: np.array
    trail_sl_by_pct: np.array
    trail_sl_when_pct: np.array


class DynamicOrderSettings(NamedTuple):
    entry_size_asset: float
    max_equity_risk_pct: float
    max_trades: int
    num_candles: int
    risk_account_pct_size: float
    risk_reward: float
    sl_based_on_add_pct: float
    sl_based_on_lookback: int
    sl_bcb_type: int
    sl_to_be_cb_type: int
    sl_to_be_when_pct: float
    sl_to_be_ze_type: int
    static_leverage: float
    trail_sl_bcb_type: int
    trail_sl_by_pct: float
    trail_sl_when_pct: float


class AccountState(NamedTuple):
    # where we are at
    ind_set_index: int
    dos_index: int
    bar_index: int
    timestamp: int
    # account info
    available_balance: float = np.nan
    cash_borrowed: float = np.nan
    cash_used: float = np.nan
    equity: float = np.nan
    fees_paid: float = np.nan
    possible_loss: float = np.nan
    realized_pnl: float = np.nan
    total_trades: int = 0


class OrderResult(NamedTuple):
    average_entry: np.float_ = np.nan
    can_move_sl_to_be: np.bool_ = False
    entry_price: np.float_ = np.nan
    entry_size_asset: np.float_ = np.nan
    entry_size_usd: np.float_ = np.nan
    exit_price: np.float_ = np.nan
    leverage: np.float_ = np.nan
    liq_price: np.float_ = np.nan
    order_status: np.int_ = np.nan
    position_size_asset: np.float_ = np.nan
    position_size_usd: np.float_ = np.nan
    sl_pct: np.float_ = np.nan
    sl_price: np.float_ = np.nan
    tp_pct: np.float_ = np.nan
    tp_price: np.float_ = np.nan


class StaticOrderSettings(NamedTuple):
    increase_position_type: int
    leverage_strategy_type: int
    long_or_short: int
    logger_bool: bool
    pg_min_max_sl_bcb: int
    sl_strategy_type: int
    sl_to_be_bool: bool
    z_or_e_type: int
    tp_strategy_type: int
    tp_fee_type: int
    trail_sl_bool: bool


class RejectedOrder(Exception):
    def message(self, message: str = "Hey there inside rejected order"):
        return message


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
        msg: str = None,
    ):
        self.order_status = order_status
        self.sl_price = sl_price
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
        ("sl_bcb_type", np.int_),
        ("sl_to_be_cb_type", np.int_),
        ("sl_to_be_when_pct", np.float_),
        ("sl_to_be_ze_type", np.int_),
        ("static_leverage", np.float_),
        ("stop_loss_type", np.int_),
        ("take_profit_type", np.int_),
        ("tp_fee_type", np.int_),
        ("trail_sl_bcb_type", np.int_),
        ("trail_sl_by_pct", np.float_),
        ("trail_sl_when_pct", np.float_),
        ("num_candles", np.int_),
        ("entry_size_asset", np.float_),
        ("max_trades", np.int_),
    ],
    align=True,
)


or_dt = np.dtype(
    [
        ("ind_set_idx", np.int_),
        ("or_set_idx", np.int_),
        ("bar_idx", np.int_),
        ("timestamp", np.int64),
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
        ("total_trades", np.int_),
        ("entry_size_asset", np.float_),
        ("entry_size_usd", np.float_),
        ("entry_price", np.float_),
        ("exit_price", np.float_),
        ("position_size_asset", np.float_),
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
        ("dos_index", np.int_),
        ("total_trades", np.float_),
        ("gains_pct", np.float_),
        ("win_rate", np.float_),
        ("to_the_upside", np.float_),
        ("fees_paid", np.float_),
        ("total_pnl", np.float_),
        ("ending_eq", np.float_),
    ],
    align=True,
)

