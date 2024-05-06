from time import gmtime, strftime, perf_counter
import numpy as np
from quantfreedom import pretty_qf_string
from os.path import dirname, join, abspath
from logging import getLogger
from typing import NamedTuple
from quantfreedom.indicators.tv_indicators import ema_tv, rsi_tv
from quantfreedom.core.strategy import Strategy
from quantfreedom.core.enums import (
    ExchangeSettings,
    FootprintCandlesTuple,
    IncreasePositionType,
    LeverageStrategyType,
    StaticOrderSettings,
    BacktestSettings,
    CandleBodyType,
    DynamicOrderSettings,
    StopLossStrategyType,
    TakeProfitStrategyType,
)

logger = getLogger()


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

dos_tuple = DynamicOrderSettings(
    account_pct_risk_per_trade=np.array([3]),
    max_trades=np.array([4]),
    risk_reward=np.array([5, 10]),
    sl_based_on_add_pct=np.array([0.2]),
    sl_based_on_lookback=np.array([30]),
    sl_bcb_type=np.array([CandleBodyType.Low]),
    sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
    sl_to_be_when_pct=np.array([0]),
    trail_sl_bcb_type=np.array([CandleBodyType.Low]),
    trail_sl_by_pct=np.array([1, 2]),
    trail_sl_when_pct=np.array([1]),
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
    cur_candle_rsi_below: np.ndarray
    cur_dur_less_than: np.ndarray
    dur_x_times_faster: np.ndarray
    ema_length: np.ndarray
    max_av_duration: np.ndarray
    min_delta_dif: np.ndarray
    rsi_dur_lb: np.ndarray
    rsi_is_below: np.ndarray
    rsi_length: np.ndarray


class VolStrategy(Strategy):
    def __init__(
        self,
        long_short: str,
        cur_candle_rsi_below: np.ndarray,
        cur_dur_less_than: np.ndarray,
        dur_x_times_faster: np.ndarray,
        ema_length: np.ndarray,
        max_av_duration: np.ndarray,
        min_delta_dif: np.ndarray,
        rsi_dur_lb: np.ndarray,
        rsi_is_below: np.ndarray,
        rsi_length: np.ndarray,
    ) -> None:

        self.long_short = long_short
        self.log_folder = abspath(join(dirname(__file__)))

        indicator_settings_tuple = IndicatorSettings(
            cur_candle_rsi_below=cur_candle_rsi_below,
            cur_dur_less_than=cur_dur_less_than,
            dur_x_times_faster=dur_x_times_faster,
            ema_length=ema_length,
            max_av_duration=max_av_duration,
            min_delta_dif=min_delta_dif,
            rsi_dur_lb=rsi_dur_lb,
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
            cur_candle_rsi_below=indicator_settings_tuple.cur_candle_rsi_below.astype(np.int_),
            cur_dur_less_than=indicator_settings_tuple.cur_dur_less_than.astype(np.int_),
            dur_x_times_faster=indicator_settings_tuple.dur_x_times_faster.astype(np.int_),
            ema_length=indicator_settings_tuple.ema_length.astype(np.int_),
            max_av_duration=indicator_settings_tuple.max_av_duration.astype(np.int_),
            min_delta_dif=indicator_settings_tuple.min_delta_dif.astype(np.int_),
            rsi_dur_lb=indicator_settings_tuple.rsi_dur_lb.astype(np.int_),
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
        candles: FootprintCandlesTuple,
        ind_set_index: int,
    ):
        start_func = perf_counter()
        try:
            self.current_ind_settings_tuple = IndicatorSettings(
                cur_candle_rsi_below=self.indicator_settings_tuple.cur_candle_rsi_below[ind_set_index],
                cur_dur_less_than=self.indicator_settings_tuple.cur_dur_less_than[ind_set_index],
                dur_x_times_faster=self.indicator_settings_tuple.dur_x_times_faster[ind_set_index],
                ema_length=self.indicator_settings_tuple.ema_length[ind_set_index],
                max_av_duration=self.indicator_settings_tuple.max_av_duration[ind_set_index],
                min_delta_dif=self.indicator_settings_tuple.min_delta_dif[ind_set_index],
                rsi_dur_lb=self.indicator_settings_tuple.rsi_dur_lb[ind_set_index],
                rsi_is_below=self.indicator_settings_tuple.rsi_is_below[ind_set_index],
                rsi_length=self.indicator_settings_tuple.rsi_length[ind_set_index],
            )
            logger.info(f"current_ind_settings_tuple: {pretty_qf_string(self.current_ind_settings_tuple)}")

            cur_candle_rsi_below = self.indicator_settings_tuple.cur_candle_rsi_below[ind_set_index]
            cur_dur_less_than = self.indicator_settings_tuple.cur_dur_less_than[ind_set_index]
            dur_x_times_faster = self.indicator_settings_tuple.dur_x_times_faster[ind_set_index]
            ema_length = self.indicator_settings_tuple.ema_length[ind_set_index]
            max_av_duration = self.indicator_settings_tuple.max_av_duration[ind_set_index]
            min_delta_dif = self.indicator_settings_tuple.min_delta_dif[ind_set_index]
            rsi_dur_lb = self.indicator_settings_tuple.rsi_dur_lb[ind_set_index]
            rsi_is_below = self.indicator_settings_tuple.rsi_is_below[ind_set_index]
            rsi_length = self.indicator_settings_tuple.rsi_length[ind_set_index]

            close_prices = candles.candle_close_prices
            duration_s = candles.candle_durations_seconds
            delta = candles.candle_deltas

            rsi = rsi_tv(
                length=rsi_length,
                source=close_prices,
            )

            self.rsi = np.around(rsi, 1)

            logger.info(f"Created RSI rsi_length= {rsi_length}")

            ema = ema_tv(
                length=ema_length,
                source=close_prices,
            )

            self.ema = np.around(ema, 1)

            logger.info(f"Created EMA ema_length= {ema_length}")

            num_rows = len(close_prices)
            logger.info(f"looping num_rows= {num_rows}")
            self.entries = np.full(num_rows, False, dtype=bool)
            self.exit_prices = np.full(num_rows, False, dtype=bool)
            start = perf_counter()
            for idx in range(rsi_dur_lb, num_rows):

                is_rsi_below = (self.rsi[idx - rsi_dur_lb : idx] < rsi_is_below).any()

                all_close_below_ema = (close_prices[idx - rsi_dur_lb : idx] < self.ema[idx - rsi_dur_lb : idx]).all()

                av_duration = duration_s[idx - rsi_dur_lb : idx].sum() / rsi_dur_lb

                is_av_durration_smaller_than_max = av_duration < max_av_duration
                is_delta_distance = abs(delta[idx] - delta[idx - 1]) > min_delta_dif
                is_cur_candle_rsi_below = self.rsi[idx] < cur_candle_rsi_below
                is_cur_candle_duration_less = duration_s[idx] < cur_dur_less_than
                is_cur_delta_positive = delta[idx] > 0

                is_long_signal = (
                    all_close_below_ema
                    and is_rsi_below
                    and is_av_durration_smaller_than_max
                    and is_delta_distance
                    and is_cur_candle_rsi_below
                    and is_cur_candle_duration_less
                    and is_cur_delta_positive
                )
                self.entries[idx] = is_long_signal
            end = perf_counter()

            logger.info(strftime("%M:%S looping entries", gmtime(int(end - start))))
            end_func = perf_counter()
            logger.info(strftime("%M:%S func", gmtime(int(end_func - start_func))))

        except Exception as e:
            logger.error(f"Exception long_set_entries_exits_array -> {e}")
            raise Exception(f"Exception long_set_entries_exits_array -> {e}")

    def long_log_indicator_settings(
        self,
        ind_set_index: int,
    ):
        pass

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
        ind_set_index: int,
    ):
        pass

    def short_log_indicator_settings(
        self,
        ind_set_index: int,
    ):
        pass

    def short_entry_message(
        self,
        bar_index: int,
    ):
        pass

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
        pass


rsi_length = 14
ema_length = 25
rsi_dur_lb = 4
max_av_duration = 1.5
min_delta_dif = 2000000
rsi_is_below = 30
cur_candle_rsi_below = 40
cur_dur_less_than = 5
dur_x_times_faster = 5

long_strat = VolStrategy(
    long_short="long",
    cur_candle_rsi_below=np.array([40]),
    cur_dur_less_than=np.array([cur_dur_less_than]),
    dur_x_times_faster=np.array([dur_x_times_faster]),
    ema_length=np.array([ema_length]),
    max_av_duration=np.array([max_av_duration]),
    min_delta_dif=np.array([min_delta_dif]),
    rsi_dur_lb=np.array([2, 4]),
    rsi_is_below=np.array([rsi_is_below]),
    rsi_length=np.array([rsi_length]),
)
