import numpy as np
from typing import NamedTuple, Optional


class CurrentFootprintCandleTuple(NamedTuple):
    open_dateime: Optional[np.datetime64] = None
    open_timestamp: Optional[int] = None
    close_dateime: Optional[np.datetime64] = None
    close_timestamp: Optional[int] = None
    durations_seconds: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    usdt_volume: Optional[float] = None
    asset_volume: Optional[float] = None


class FootprintCandlesTuple(NamedTuple):
    candle_open_datetimes: Optional[np.ndarray] = None
    candle_open_timestamps: Optional[np.ndarray] = None
    candle_close_datetimes: Optional[np.ndarray] = None
    candle_close_timestamps: Optional[np.ndarray] = None
    candle_durations_seconds: Optional[np.ndarray] = None
    candle_open_prices: Optional[np.ndarray] = None
    candle_high_prices: Optional[np.ndarray] = None
    candle_low_prices: Optional[np.ndarray] = None
    candle_close_prices: Optional[np.ndarray] = None
    candle_usdt_volumes: Optional[np.ndarray] = None
    candle_asset_volumes: Optional[np.ndarray] = None
    candle_trade_counts: Optional[np.ndarray] = None
    candle_deltas: Optional[np.ndarray] = None
    candle_delta_percents: Optional[np.ndarray] = None
    candle_buy_volumes: Optional[np.ndarray] = None
    candle_buy_counts: Optional[np.ndarray] = None
    candle_sell_volumes: Optional[np.ndarray] = None
    candle_sell_counts: Optional[np.ndarray] = None
    candle_cvds: Optional[np.ndarray] = None
    candle_pocs: Optional[np.ndarray] = None
    candle_high_lows: Optional[np.ndarray] = None
    prices_tuple: Optional[tuple] = None
    prices_buy_vol_tuple: Optional[tuple] = None
    prices_buy_count_tuple: Optional[tuple] = None
    prices_sell_vol_tuple: Optional[tuple] = None
    prices_sell_count_tuple: Optional[tuple] = None
    prices_delta_tuple: Optional[tuple] = None
    prices_delta_percent_tuple: Optional[tuple] = None
    prices_volume_tuple: Optional[tuple] = None
    prices_trade_count_tuple: Optional[tuple] = None


class CandleBodyTypeT(NamedTuple):
    OpenDatetime: int = 0
    OpenTimestamp: int = 1
    CloseDatetime: int = 2
    CloseTimestamp: int = 3
    DurationSeconds: int = 4
    Open: int = 5
    High: int = 6
    Low: int = 7
    Close: int = 8
    UsdtVolume: int = 9
    AssetVolume: int = 10
    Nothing: int = 11


CandleBodyType = CandleBodyTypeT()


class IncreasePositionTypeT(NamedTuple):
    """
    The different ways you can increase your position

    Parameters
    ----------
    AmountEntrySize : int= 0
        How much you want your position size to be per trade in USDT
    PctAccountEntrySize : int = 1
        If you have an equity of 1000 and you want your pct account entry size to be 1% then that means each trade will be a position size of 10 usdt
    RiskAmountEntrySize : int = 2
        How much you will risk per trade. You must have a stop loss in order to use this mode.
    RiskPctAccountEntrySize : int = 3
        How much of your account you want to risk per trade. If you have an equtiy of 1000 and you want to risk 1% then each trade would be risking $10. You must have a stop loss in order to use this mode
    SmalletEntrySizeAsset : int = 4
        What ever the exchange smallest asset size is that is what your position size will be for each trade. Let's say the smallest is .001 for btcusdt, then each trade will be worth .001 btc

    """

    AmountEntrySize: int = 0
    PctAccountEntrySize: int = 1
    RiskAmountEntrySize: int = 2
    RiskPctAccountEntrySize: int = 3
    SmalletEntrySizeAsset: int = 4


IncreasePositionType = IncreasePositionTypeT()


class LeverageModeTypeT(NamedTuple):
    Cross: int = 0
    Isolated: int = 1


LeverageModeType = LeverageModeTypeT()


class LeverageStrategyTypeT(NamedTuple):
    """
    Choosing which leverage strategy you would like to use.

    Parameters
    ----------
    Dynamic : int = 0
        This will automatically adjust your leverage to be .001 percent further than your stop loss. The reason behind this is to that it will keep your used cash amount down as much as possible so you can place more trades on the same or other assets.
    Static : int = 1
        Static leverage

    """

    Dynamic: int = 0
    Static: int = 1


LeverageStrategyType = LeverageStrategyTypeT()


class LoggerFuncTypeT(NamedTuple):
    Debug: int = 0
    Info: int = 1
    Warning: int = 2
    Error: int = 3


LoggerFuncType = LoggerFuncTypeT()


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


class PositionModeTypeT(NamedTuple):
    OneWayMode: int = 0
    BuySide: int = 1
    SellSide: int = 2
    HedgeMode: int = 3


PositionModeType = PositionModeTypeT()


class StringerFuncTypeT(NamedTuple):
    float_to_str: int = 0
    log_datetime: int = 1
    candle_body_str: int = 2
    os_to_str: int = 3


StringerFuncType = StringerFuncTypeT()


class StopLossStrategyTypeT(NamedTuple):
    Nothing: int = 0
    SLBasedOnCandleBody: int = 1


StopLossStrategyType = StopLossStrategyTypeT()


class TrailingSLStrategyTypeT(NamedTuple):
    Nothing: int = 0
    CBAboveBelow: int = 1
    PctAboveBelow: int = 2


TrailingSLStrategyType = TrailingSLStrategyTypeT()


class TakeProfitStrategyTypeT(NamedTuple):
    """
    How you want to process the take profit

    Parameters
    ----------
    RiskReward : int = 0
        Risk to reward
    Provided : int = 1
        Your strategy will provide the exit prices
    Nothing : int = 2
        No take profits.

    """

    RiskReward: int = 0
    Provided: int = 1
    Nothing: int = 2


TakeProfitStrategyType = TakeProfitStrategyTypeT()


class TriggerDirectionTypeT(NamedTuple):
    Rise: int = 1
    Fall: int = 2


TriggerDirectionType = TriggerDirectionTypeT()


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


class AccountState(NamedTuple):
    # where we are at
    set_idx: int
    bar_index: int
    timestamp: int
    # account info
    available_balance: float
    cash_borrowed: float
    cash_used: float
    equity: float
    fees_paid: float
    total_possible_loss: int
    realized_pnl: float
    total_trades: int


class BacktestSettings(NamedTuple):
    """
    Settings for filtering the results of your backtest. The main purpose of this is to save on memory and also there is sometimes no point in wanting to see strategies that are negative gains or below a specific qf score because they are useless.

    Parameters
    ----------
    gains_pct_filter : float = -np.inf
        Will not record any strategies whos gains % result is below gains_pct_filter
    qf_filter : float = -np.inf
        Will not record any strategies whos qf score result is below the qf filter. qf_score is between -1 to 1,
    total_trade_filter : int = -1
        Will not record any strategies whos total trades result is below total trades filter.

    """

    gains_pct_filter: float = -np.inf
    qf_filter: float = -np.inf
    total_trade_filter: int = -1


class DynamicOrderSettings(NamedTuple):
    account_pct_risk_per_trade: np.ndarray
    max_trades: np.ndarray
    risk_reward: np.ndarray
    sl_based_on_add_pct: np.ndarray
    sl_based_on_lookback: np.ndarray
    sl_bcb_type: np.ndarray
    sl_to_be_cb_type: np.ndarray
    sl_to_be_when_pct: np.ndarray
    trail_sl_bcb_type: np.ndarray
    trail_sl_by_pct: np.ndarray
    trail_sl_when_pct: np.ndarray
    settings_index: np.ndarray = np.array([0])


class ExchangeSettings(NamedTuple):
    asset_tick_step: int
    leverage_mode: int
    leverage_tick_step: int
    limit_fee_pct: float
    market_fee_pct: float
    max_asset_size: float
    max_leverage: float
    min_asset_size: float
    min_leverage: float
    mmr_pct: float
    position_mode: int
    price_tick_step: int


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
    pg_min_max_sl_bcb: str
    sl_strategy_type: int
    sl_to_be_bool: bool
    starting_bar: int
    starting_equity: float
    static_leverage: float
    tp_fee_type: str
    tp_strategy_type: int
    trailing_sl_strategy_type: int
    z_or_e_type: str


class RejectedOrder(Exception):
    def __init__(
        self,
        msg: str = None,
    ):
        self.msg = msg


class DecreasePosition(Exception):
    def __init__(
        self,
        exit_fee_pct: Optional[float] = np.nan,
        exit_price: Optional[float] = np.nan,
        liq_price: Optional[float] = np.nan,
        msg: Optional[str] = None,
        order_status: Optional[OrderStatus] = None,  # type: ignore
        sl_price: Optional[float] = np.nan,
    ):
        self.exit_fee_pct = exit_fee_pct
        self.exit_price = exit_price
        self.liq_price = liq_price
        self.msg = msg
        self.order_status = order_status
        self.sl_price = sl_price


order_settings_array_dt = np.dtype(
    [
        ("set_idx", np.int_),
        ("increase_position_type", np.int_),
        ("leverage_type", np.int_),
        ("max_equity_risk_pct", np.float_),
        ("long_or_short", np.int_),
        ("account_pct_risk_per_trade", np.float_),
        ("risk_reward", np.float_),
        ("sl_based_on_add_pct", np.float_),
        ("sl_based_on_lookback", np.int_),
        ("sl_bcb_type", np.int_),
        ("sl_to_be_cb_type", np.int_),
        ("sl_to_be_when_pct", np.float_),
        ("static_leverage", np.float_),
        ("stop_loss_type", np.int_),
        ("take_profit_type", np.int_),
        ("tp_fee_type", np.int_),
        ("trail_sl_bcb_type", np.int_),
        ("trail_sl_by_pct", np.float_),
        ("trail_sl_when_pct", np.float_),
        ("candle_group_size", np.int_),
        ("entry_size_asset", np.float_),
        ("max_trades", np.int_),
    ],
    align=True,
)


or_dt = np.dtype(
    [
        ("set_idx", np.int_),
        ("bar_idx", np.int_),
        ("timestamp", np.int64),
        ("order_status", np.int_),
        ("equity", np.float_),
        ("available_balance", np.float_),
        ("cash_borrowed", np.float_),
        ("cash_used", np.float_),
        ("average_entry", np.float_),
        ("fees_paid", np.float_),
        ("leverage", np.float_),
        ("liq_price", np.float_),
        ("total_possible_loss", np.float_),
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
        ("set_idx", np.int_),
        ("total_trades", np.float_),
        ("wins", np.int_),
        ("losses", np.int_),
        ("gains_pct", np.float_),
        ("win_rate", np.float_),
        ("qf_score", np.float_),
        ("fees_paid", np.float_),
        ("total_pnl", np.float_),
        ("ending_eq", np.float_),
    ],
    align=True,
)
