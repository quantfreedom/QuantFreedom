from my_keys import MufexKeys
import os
import numpy as np
import plotly.graph_objects as go
from logging import getLogger
from typing import NamedTuple
from quantfreedom.exchanges.mufex_exchange.mufex import Mufex
from quantfreedom.indicators.tv_indicators import rsi_tv
from quantfreedom.strategies.strategy import Strategy
from quantfreedom.enums import (
    ExchangeSettings,
    LeverageModeType,
    PositionModeType,
    IncreasePositionType,
    LeverageStrategyType,
    StaticOrderSettings,
    BacktestSettings,
    CandleBodyType,
    DynamicOrderSettings,
    StopLossStrategyType,
    TakeProfitStrategyType,
)

logger = getLogger("info")


# mufex_main = Mufex(
#     api_key=MufexKeys.mainnet_neo_api_key,
#     secret_key=MufexKeys.mainnet_neo_secret_key,
#     use_test_net=False,
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
backtest_settings_tuple = BacktestSettings(qf_filter=0.06)

dos_tuple = DynamicOrderSettings(
    account_pct_risk_per_trade=np.array([3]),
    max_trades=np.array([4]),
    risk_reward=np.array([2, 5]),
    sl_based_on_add_pct=np.array([0.1, 0.2, 0.3, 0.5]),
    sl_based_on_lookback=np.array([20, 50]),
    sl_bcb_type=np.array([CandleBodyType.Low]),
    sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
    sl_to_be_when_pct=np.array([0]),
    trail_sl_bcb_type=np.array([CandleBodyType.Low]),
    trail_sl_by_pct=np.array([0.5, 1.0, 2.0, 3, 4]),
    trail_sl_when_pct=np.array([1, 2, 3, 4]),
)

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


class IndicatorSettings(NamedTuple):
    rsi_is_above: np.array
    rsi_is_below: np.array
    rsi_length: np.array


class RSIRisingFalling(Strategy):
    def __init__(
        self,
        long_short: str,
        rsi_length: int,
        rsi_is_above: np.array = np.array([0]),
        rsi_is_below: np.array = np.array([0]),
    ) -> None:

        self.long_short = long_short
        self.log_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        indicator_settings_tuple = IndicatorSettings(
            rsi_is_above=rsi_is_above,
            rsi_is_below=rsi_is_below,
            rsi_length=rsi_length,
        )

        indicator_settings_tuple = IndicatorSettings(
            *self.get_ind_set_dos_cart_product(
                dos_tuple=dos_tuple,
                indicator_settings_tuple=indicator_settings_tuple,
            )
        )
        self.set_ind_settings_tuple(
            indicator_settings_tuple=indicator_settings_tuple,
        )

        if long_short == "long":
            self.set_entries_exits_array = self.long_set_entries_exits_array
            self.log_indicator_settings = self.long_log_indicator_settings
            self.entry_message = self.long_entry_message
            self.live_evaluate = self.long_live_evaluate
            self.chart_title = "Long Signal"
        else:
            self.set_entries_exits_array = self.short_set_entries_exits_array
            self.log_indicator_settings = self.short_log_indicator_settings
            self.entry_message = self.short_entry_message
            self.live_evaluate = self.short_live_evaluate
            self.chart_title = "short Signal"

    #######################################################
    #######################################################
    #######################################################
    ##################      Utils     #####################
    ##################      Utils     #####################
    ##################      Utils     #####################
    #######################################################
    #######################################################
    #######################################################

    def set_ind_settings_tuple(
        self,
        indicator_settings_tuple: IndicatorSettings,
    ) -> None:
        self.indicator_settings_tuple = IndicatorSettings(
            rsi_is_above=indicator_settings_tuple.rsi_is_above.astype(np.int_),
            rsi_is_below=indicator_settings_tuple.rsi_is_below.astype(np.int_),
            rsi_length=indicator_settings_tuple.rsi_length.astype(np.int_),
        )

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
        candles: np.array,
        ind_set_index: int,
    ):
        try:
            self.rsi_is_below = self.indicator_settings_tuple.rsi_is_below[ind_set_index]
            self.rsi_length = self.indicator_settings_tuple.rsi_length[ind_set_index]
            self.h_line = self.rsi_is_below
            self.current_ind_settings_tuple = IndicatorSettings(
                rsi_is_above=0,
                rsi_is_below=self.rsi_is_below,
                rsi_length=self.rsi_length,
            )

            rsi = rsi_tv(
                source=candles[:, CandleBodyType.Close],
                length=self.rsi_length,
            )

            self.rsi = np.around(rsi, 1)
            logger.info(f"Created RSI rsi_length= {self.rsi_length}")

            prev_rsi = np.roll(self.rsi, 1)
            prev_rsi[0] = np.nan

            prev_prev_rsi = np.roll(prev_rsi, 1)
            prev_prev_rsi[0] = np.nan

            falling = prev_prev_rsi > prev_rsi
            rising = self.rsi > prev_rsi
            is_below = self.rsi < self.rsi_is_below

            self.entries = np.where(is_below & falling & rising, True, False)
            self.entry_signals = np.where(self.entries, self.rsi, np.nan)

            self.exit_prices = np.full_like(self.rsi, np.nan)
        except Exception as e:
            logger.error(f"Exception long_set_entries_exits_array -> {e}")
            raise Exception(f"Exception long_set_entries_exits_array -> {e}")

    def long_log_indicator_settings(
        self,
        ind_set_index: int,
    ):
        logger.info(
            f"""
Indicator Settings
Indicator Settings Index= {ind_set_index}
rsi_length= {self.rsi_length}
rsi_is_below= {self.rsi_is_below}"""
        )

    def long_entry_message(
        self,
        bar_index: int,
    ):
        logger.info("\n\n")
        logger.info(
            f"Entry time!!! {self.rsi[bar_index-2]} > {self.rsi[bar_index-1]} < {self.rsi[bar_index]} and {self.rsi[bar_index]} < {self.rsi_is_below}"
        )

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
        candles: np.array,
        ind_set_index: int,
    ):
        try:
            self.rsi_is_above = self.indicator_settings_tuple.rsi_is_above[ind_set_index]
            self.h_line = self.rsi_is_above
            self.rsi_length = self.indicator_settings_tuple.rsi_length[ind_set_index]
            self.current_ind_settings_tuple = IndicatorSettings(
                rsi_is_above=self.rsi_is_above,
                rsi_is_below=0,
                rsi_length=self.rsi_length,
            )
            rsi = rsi_tv(
                source=candles[:, CandleBodyType.Close],
                length=self.rsi_length,
            )

            self.rsi = np.around(rsi, 1)
            logger.info(f"Created RSI rsi_length= {self.rsi_length}")

            prev_rsi = np.roll(self.rsi, 1)
            prev_rsi[0] = np.nan

            prev_prev_rsi = np.roll(prev_rsi, 1)
            prev_prev_rsi[0] = np.nan

            rising = prev_prev_rsi < prev_rsi
            falling = self.rsi < prev_rsi
            is_above = self.rsi > self.rsi_is_above

            self.entries = np.where(is_above & falling & rising, True, False)
            self.entry_signals = np.where(self.entries, self.rsi, np.nan)

            self.exit_prices = np.full_like(self.rsi, np.nan)
        except Exception as e:
            logger.error(f"Exception short_set_entries_exits_array -> {e}")
            raise Exception(f"Exception short_set_entries_exits_array -> {e}")

    def short_log_indicator_settings(
        self,
        ind_set_index: int,
    ):
        logger.info(
            f"""
Indicator Settings
Indicator Settings Index= {ind_set_index}
rsi_length= {self.rsi_length}
rsi_is_above= {self.rsi_is_above}"""
        )

    def short_entry_message(
        self,
        bar_index: int,
    ):
        logger.info("\n\n")
        logger.info(
            f"Entry time!!! {self.rsi[bar_index-2]} < {self.rsi[bar_index-1]} > {self.rsi[bar_index]} and {self.rsi[bar_index]} > {self.rsi_is_above}"
        )

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
        candles: np.array,
    ):
        datetimes = candles[:, CandleBodyType.Timestamp].astype("datetime64[ms]")

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
    rsi_length=np.array([14]),
    rsi_is_below=np.array([80]),
)
