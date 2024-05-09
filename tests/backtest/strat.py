import numpy as np
import plotly.graph_objects as go
from logging import getLogger
from typing import NamedTuple
from os.path import dirname, join, abspath
from quantfreedom.indicators.tv_indicators import rsi_tv
from quantfreedom.core.strategy import Strategy
from quantfreedom.core.enums import (
    BacktestSettings,
    CandleBodyType,
    DynamicOrderSettings,
    ExchangeSettings,
    FootprintCandlesTuple,
    IncreasePositionType,
    LeverageStrategyType,
    StaticOrderSettings,
    StopLossStrategyType,
    TakeProfitStrategyType,
)

logger = getLogger()


# mufex_main = Mufex(
#     api_key=MufexKeys.mainnet_neo_api_key,
#     secret_key=MufexKeys.mainnet_neo_secret_key,
#     use_testnet=False,
# )


# exchange_settings_tuple = mufex_main.set_and_get_exchange_settings_tuple(
#     leverage_mode=LeverageModeType.Isolated,
#     position_mode=PositionModeType.HedgeMode,
#     symbol="BTCUSDT",
# )

exchange_settings_tuple = ExchangeSettings(
    asset_tick_step=3,
    leverage_mode=1,
    leverage_tick_step=2,
    limit_fee_pct=0.0003,
    market_fee_pct=0.0006,
    max_asset_size=100.0,
    max_leverage=150.0,
    min_asset_size=0.001,
    min_leverage=1.0,
    mmr_pct=0.004,
    position_mode=3,
    price_tick_step=1,
)
backtest_settings_tuple = BacktestSettings()

static_os_tuple = StaticOrderSettings(
    increase_position_type=IncreasePositionType.RiskPctAccountEntrySize,
    leverage_strategy_type=LeverageStrategyType.Dynamic,
    pg_min_max_sl_bcb="min",
    sl_strategy_type=StopLossStrategyType.SLBasedOnCandleBody,
    sl_to_be_bool=False,
    starting_bar=50,
    starting_equity=1000.0,
    static_leverage=None,
    tp_fee_type="limit",
    tp_strategy_type=TakeProfitStrategyType.RiskReward,
    trail_sl_bool=True,
    z_or_e_type=None,
)

og_dos_tuple = DynamicOrderSettings(
    settings_index=np.array([0]),
    account_pct_risk_per_trade=np.array([5]),
    max_trades=np.array([2, 4, 6]),
    risk_reward=np.array([3, 5]),
    sl_based_on_add_pct=np.array([0.1, 0.2, 0.3, 0.5]),
    sl_based_on_lookback=np.array([20, 50]),
    sl_bcb_type=np.array([CandleBodyType.Low]),
    sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
    sl_to_be_when_pct=np.array([0]),
    trail_sl_bcb_type=np.array([CandleBodyType.Low]),
    trail_sl_by_pct=np.array([0.5, 1.0, 2.0, 3, 4]),
    trail_sl_when_pct=np.array([1, 2, 3, 4]),
)


class IndicatorSettings(NamedTuple):
    rsi_length: np.ndarray
    above_rsi_cur: np.ndarray
    above_rsi_p: np.ndarray
    above_rsi_pp: np.ndarray
    below_rsi_cur: np.ndarray
    below_rsi_p: np.ndarray
    below_rsi_pp: np.ndarray


class RSIRisingFalling(Strategy):
    og_ind_set_tuple: IndicatorSettings

    def __init__(
        self,
        long_short: str,
        shuffle_bool: bool,
        rsi_length: np.ndarray,
        above_rsi_cur: np.ndarray = np.array([0]),
        above_rsi_p: np.ndarray = np.array([0]),
        above_rsi_pp: np.ndarray = np.array([0]),
        below_rsi_cur: np.ndarray = np.array([0]),
        below_rsi_p: np.ndarray = np.array([0]),
        below_rsi_pp: np.ndarray = np.array([0]),
    ) -> None:

        self.long_short = long_short
        self.log_folder = abspath(join(dirname(__file__)))

        og_ind_set_tuple = IndicatorSettings(
            rsi_length=rsi_length,
            above_rsi_cur=above_rsi_cur,
            above_rsi_p=above_rsi_p,
            above_rsi_pp=above_rsi_pp,
            below_rsi_cur=below_rsi_cur,
            below_rsi_p=below_rsi_p,
            below_rsi_pp=below_rsi_pp,
        )

        self.set_og_ind_and_dos_tuples(
            og_ind_set_tuple=og_ind_set_tuple,
            shuffle_bool=shuffle_bool,
        )

        if long_short == "long":
            self.chart_title = "Long Signal"
            self.entry_message = self.long_entry_message
            self.live_evaluate = self.long_live_evaluate
            self.set_entries_exits_array = self.long_set_entries_exits_array
        else:
            self.chart_title = "short Signal"
            self.entry_message = self.short_entry_message
            self.live_evaluate = self.short_live_evaluate
            self.set_entries_exits_array = self.short_set_entries_exits_array

    #######################################################
    #######################################################
    #######################################################
    ##################      Utils     #####################
    ##################      Utils     #####################
    ##################      Utils     #####################
    #######################################################
    #######################################################
    #######################################################

    def set_og_ind_and_dos_tuples(
        self,
        og_ind_set_tuple: IndicatorSettings,
        shuffle_bool: bool,
    ) -> None:

        cart_prod_array = self.get_ind_set_dos_cart_product(
            og_dos_tuple=og_dos_tuple,
            og_ind_set_tuple=og_ind_set_tuple,
        )

        filtered_cart_prod_array = self.get_filter_cart_prod_array(
            cart_prod_array=cart_prod_array,
        )

        if shuffle_bool:
            shuffled_cart_prod_array = np.random.default_rng().permuted(filtered_cart_prod_array, axis=1)
        else:
            shuffled_cart_prod_array = filtered_cart_prod_array.copy()

        self.og_dos_tuple = self.get_og_dos_tuple(
            shuffled_cart_prod_array=shuffled_cart_prod_array,
        )

        self.og_ind_set_tuple = self.get_og_ind_set_tuple(
            shuffled_cart_prod_array=shuffled_cart_prod_array,
        )
        self.total_filtered_settings = self.og_ind_set_tuple.rsi_length.size

        logger.debug("set_og_ind_and_dos_tuples")

    def get_og_ind_set_tuple(
        self,
        shuffled_cart_prod_array: np.ndarray,
    ) -> IndicatorSettings:

        ind_set_tuple = IndicatorSettings(*tuple(shuffled_cart_prod_array[12:]))
        logger.debug("ind_set_tuple")

        og_ind_set_tuple = IndicatorSettings(
            rsi_length=ind_set_tuple.rsi_length.astype(np.int_),
            above_rsi_cur=ind_set_tuple.above_rsi_cur.astype(np.int_),
            above_rsi_p=ind_set_tuple.above_rsi_p.astype(np.int_),
            above_rsi_pp=ind_set_tuple.above_rsi_pp.astype(np.int_),
            below_rsi_cur=ind_set_tuple.below_rsi_cur.astype(np.int_),
            below_rsi_p=ind_set_tuple.below_rsi_p.astype(np.int_),
            below_rsi_pp=ind_set_tuple.below_rsi_pp.astype(np.int_),
        )
        logger.debug("og_ind_set_tuple")

        return og_ind_set_tuple

    def get_filter_cart_prod_array(
        self,
        cart_prod_array: np.ndarray,
    ) -> np.ndarray:
        # cart array indexes
        above_rsi_cur = 13
        above_rsi_p = 14
        above_rsi_pp = 15
        below_rsi_cur = 16
        below_rsi_p = 17
        below_rsi_pp = 18

        above_cur_le_p = cart_prod_array[above_rsi_cur] <= cart_prod_array[above_rsi_p]
        above_pp_le_p = cart_prod_array[above_rsi_pp] <= cart_prod_array[above_rsi_p]

        below_cur_ge_p = cart_prod_array[below_rsi_cur] >= cart_prod_array[below_rsi_p]
        below_pp_ge_p = cart_prod_array[below_rsi_pp] >= cart_prod_array[below_rsi_p]

        filtered_indexes = below_cur_ge_p & below_pp_ge_p & above_cur_le_p & above_pp_le_p

        filtered_cart_prod_array = cart_prod_array[:, filtered_indexes]
        logger.debug(f"cart prod size {cart_prod_array.shape[1]:,}")
        logger.debug(f"filtered cart prod size {filtered_cart_prod_array.shape[1]:,}")
        logger.debug(f"Removed {cart_prod_array.shape[1] -filtered_cart_prod_array.shape[1] }")

        filtered_cart_prod_array[0] = np.arange(filtered_cart_prod_array.shape[1])

        return filtered_cart_prod_array

    #######################################################
    #######################################################
    #######################################################
    ##################      Long     ######################
    ##################      Long     ######################
    ##################      Long     ######################
    #######################################################
    #######################################################
    #######################################################

    def long_set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
        set_idx: int,
    ):
        try:
            rsi_length = self.og_ind_set_tuple.rsi_length[set_idx]
            below_rsi_cur = self.og_ind_set_tuple.below_rsi_cur[set_idx]
            below_rsi_p = self.og_ind_set_tuple.below_rsi_p[set_idx]
            below_rsi_pp = self.og_ind_set_tuple.below_rsi_pp[set_idx]

            self.h_line = below_rsi_cur

            self.cur_ind_set_tuple = IndicatorSettings(
                rsi_length=rsi_length,
                above_rsi_cur=0,
                above_rsi_p=0,
                above_rsi_pp=0,
                below_rsi_cur=below_rsi_cur,
                below_rsi_p=below_rsi_p,
                below_rsi_pp=below_rsi_pp,
            )
            logger.info(
                f"""
Indicator Settings
Indicator Settings Index= {set_idx}
rsi_length= {rsi_length}
below_rsi_cur= {below_rsi_cur}
below_rsi_p= {below_rsi_p}
below_rsi_pp= {below_rsi_pp}
"""
            )

            rsi = rsi_tv(
                source=candles.candle_close_prices,
                length=rsi_length,
            )

            self.rsi = np.around(rsi, 1)
            logger.debug("Created RSI")

            prev_rsi = np.roll(self.rsi, 1)
            prev_rsi[0] = np.nan

            prev_prev_rsi = np.roll(prev_rsi, 1)
            prev_prev_rsi[0] = np.nan

            falling = prev_prev_rsi > prev_rsi
            rising = self.rsi > prev_rsi
            is_below_cur = self.rsi < below_rsi_cur
            is_below_p = prev_rsi < below_rsi_p
            is_below_pp = prev_prev_rsi < below_rsi_pp

            self.entries = is_below_cur & is_below_p & is_below_pp & falling & rising
            self.entry_signals = np.where(self.entries, self.rsi, np.nan)

            self.exit_prices = np.full_like(self.rsi, np.nan)
            logger.debug("Created entries exits")
        except Exception as e:
            logger.error(f"Exception long_set_entries_exits_array -> {e}")
            raise Exception(f"Exception long_set_entries_exits_array -> {e}")

    def long_entry_message(
        self,
        bar_index: int,
    ):
        logger.info("\n\n")
        logger.info(f"Entry time!!!")

    #######################################################
    #######################################################
    #######################################################
    ##################      short    ######################
    ##################      short    ######################
    ##################      short    ######################
    #######################################################
    #######################################################
    #######################################################

    def short_set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
        set_idx: int,
    ):
        try:
            self.above_rsi_cur = self.og_ind_set_tuple.above_rsi_cur[set_idx]
            self.h_line = self.above_rsi_cur
            rsi_length = self.og_ind_set_tuple.rsi_length[set_idx]

            logger.info(
                f"""
Indicator Settings
Indicator Settings Index= {set_idx}
rsi_length= {rsi_length}
above_rsi_cur= {self.above_rsi_cur}"""
            )

            self.cur_ind_set_tuple = IndicatorSettings(
                above_rsi_cur=self.above_rsi_cur,
                below_rsi_cur=0,
                rsi_length=rsi_length,
            )
            rsi = rsi_tv(
                source=candles.candle_close_prices,
                length=rsi_length,
            )

            self.rsi = np.around(rsi, 1)
            logger.info(f"Created RSI rsi_length= {rsi_length}")

            prev_rsi = np.roll(self.rsi, 1)
            prev_rsi[0] = np.nan

            prev_prev_rsi = np.roll(prev_rsi, 1)
            prev_prev_rsi[0] = np.nan

            rising = prev_prev_rsi < prev_rsi
            falling = self.rsi < prev_rsi
            is_above = self.rsi > self.above_rsi_cur

            self.entries = np.where(is_above & falling & rising, True, False)
            self.entry_signals = np.where(self.entries, self.rsi, np.nan)

            self.exit_prices = np.full_like(self.rsi, np.nan)
        except Exception as e:
            logger.error(f"Exception short_set_entries_exits_array -> {e}")
            raise Exception(f"Exception short_set_entries_exits_array -> {e}")

    def short_entry_message(
        self,
        bar_index: int,
    ):
        logger.info("\n\n")
        logger.info(f"Entry time!!!")

    #######################################################
    #######################################################
    #######################################################
    ##################      Plot     ######################
    ##################      Plot     ######################
    ##################      Plot     ######################
    #######################################################
    #######################################################
    #######################################################

    def plot_signals(
        self,
        candles: FootprintCandlesTuple,
    ):
        datetimes = candles.candle_open_datetimes

        fig = go.Figure()
        fig.add_scatter(
            x=datetimes,
            y=self.rsi,
            name="RSI",
            line_color="yellow",
        )
        fig.add_scatter(
            x=datetimes,
            y=self.entry_signals,
            mode="markers",
            name="entries",
            marker=dict(
                size=12,
                symbol="circle",
                color="#00F6FF",
                line=dict(
                    width=1,
                    color="DarkSlateGrey",
                ),
            ),
        )
        fig.add_hline(
            y=self.h_line,
            opacity=0.3,
            line_color="red",
        )
        fig.update_layout(
            height=500,
            xaxis_rangeslider_visible=False,
            title=dict(
                x=0.5,
                text=self.chart_title,
                xanchor="center",
                font=dict(
                    size=50,
                ),
            ),
        )
        fig.show()


long_strat = RSIRisingFalling(
    long_short="long",
    shuffle_bool=True,
    rsi_length=np.array([15, 25]),
    below_rsi_cur=np.array([30, 40, 60]),
    below_rsi_p=np.array([25, 30, 40]),
    below_rsi_pp=np.array([30, 40]),
)
