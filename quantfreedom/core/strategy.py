from typing import NamedTuple, Optional, Callable
import numpy as np
from logging import getLogger
from quantfreedom.core.enums import (
    BacktestSettings,
    DynamicOrderSettings,
    ExchangeSettings,
    FootprintCandlesTuple,
    StaticOrderSettings,
)

logger = getLogger()


class IndicatorSettings(NamedTuple):
    pass


class Strategy:
    backtest_settings_tuple: BacktestSettings
    cur_dos_tuple: DynamicOrderSettings
    cur_ind_set_tuple: IndicatorSettings
    entries: np.ndarray
    exchange_settings_tuple: ExchangeSettings
    exit_prices: np.ndarray
    log_folder: str
    long_short: str
    og_dos_tuple: DynamicOrderSettings
    og_ind_set_tuple: IndicatorSettings
    static_os_tuple: StaticOrderSettings
    total_filtered_settings: int = 0
    total_indicator_settings: int = 0
    total_order_settings: int = 0

    def __init__(self) -> None:
        pass

    def get_ind_set_dos_cart_product(
        self,
        og_dos_tuple: DynamicOrderSettings,
        og_ind_set_tuple: IndicatorSettings,
    ) -> np.ndarray:
        total_indicator_settings = 1
        total_order_settings = 1

        for array in og_dos_tuple:
            total_order_settings *= array.size
        logger.debug(f"Total Order Settings: {total_order_settings}")
        self.total_order_settings = total_order_settings

        for array in og_ind_set_tuple:
            total_indicator_settings *= array.size
        logger.debug(f"Total Indicator Settings: {total_indicator_settings}")
        self.total_indicator_settings = total_indicator_settings

        the_tuple = og_dos_tuple + og_ind_set_tuple
        array_size = total_order_settings * total_indicator_settings
        logger.debug(f"Total Array Size: {array_size}")

        cart_prod_array = np.empty((array_size, len(the_tuple)))

        for i in range(len(the_tuple)):
            m = int(array_size / the_tuple[i].size)
            cart_prod_array[:array_size, i] = np.repeat(the_tuple[i], m)
            array_size //= the_tuple[i].size

        array_size = the_tuple[-1].size
        logger.debug("array_size")

        for k in range(len(the_tuple) - 2, -1, -1):
            array_size *= the_tuple[k].size
            m = int(array_size / the_tuple[k].size)
            for j in range(1, the_tuple[k].size):
                cart_prod_array[j * m : (j + 1) * m, k + 1 :] = cart_prod_array[0:m, k + 1 :]

        logger.debug("cart_prod_array")
        trail_sl_by_pct = 9
        trail_sl_when_pct = 10
        cart_prod_array = cart_prod_array.T

        filter_tf = cart_prod_array[trail_sl_when_pct] > cart_prod_array[trail_sl_by_pct]

        filtered_cart_prod = cart_prod_array[:, filter_tf]

        return filtered_cart_prod

    def get_og_dos_tuple(
        self,
        final_cart_prod_array: np.ndarray,
    ) -> DynamicOrderSettings:

        dos_tuple = DynamicOrderSettings(*tuple(final_cart_prod_array[:12]))
        logger.debug("dos_tuple")

        og_dos_tuple = DynamicOrderSettings(
            settings_index=dos_tuple.settings_index.astype(np.int_),
            account_pct_risk_per_trade=dos_tuple.account_pct_risk_per_trade / 100,
            max_trades=dos_tuple.max_trades.astype(np.int_),
            risk_reward=dos_tuple.risk_reward,
            sl_based_on_add_pct=dos_tuple.sl_based_on_add_pct / 100,
            sl_based_on_lookback=dos_tuple.sl_based_on_lookback.astype(np.int_),
            sl_bcb_type=dos_tuple.sl_bcb_type.astype(np.int_),
            sl_to_be_cb_type=dos_tuple.sl_to_be_cb_type.astype(np.int_),
            sl_to_be_when_pct=dos_tuple.sl_to_be_when_pct / 100,
            trail_sl_bcb_type=dos_tuple.trail_sl_bcb_type.astype(np.int_),
            trail_sl_by_pct=dos_tuple.trail_sl_by_pct / 100,
            trail_sl_when_pct=dos_tuple.trail_sl_when_pct / 100,
        )
        logger.debug("og_dos_tuple")

        return og_dos_tuple

    def get_settings_index(
        self,
        set_idx: int,
    ) -> int:
        indexes = self.og_dos_tuple.settings_index == set_idx
        new_set_idx = np.where(indexes)[0][0]
        return new_set_idx

    def set_cur_dos_tuple(
        self,
        set_idx: int,
    ):
        self.cur_dos_tuple = DynamicOrderSettings(
            settings_index=self.og_dos_tuple.settings_index[set_idx],
            account_pct_risk_per_trade=self.og_dos_tuple.account_pct_risk_per_trade[set_idx],
            max_trades=self.og_dos_tuple.max_trades[set_idx],
            risk_reward=self.og_dos_tuple.risk_reward[set_idx],
            sl_based_on_add_pct=self.og_dos_tuple.sl_based_on_add_pct[set_idx],
            sl_based_on_lookback=self.og_dos_tuple.sl_based_on_lookback[set_idx],
            sl_bcb_type=self.og_dos_tuple.sl_bcb_type[set_idx],
            sl_to_be_cb_type=self.og_dos_tuple.sl_to_be_cb_type[set_idx],
            sl_to_be_when_pct=self.og_dos_tuple.sl_to_be_when_pct[set_idx],
            trail_sl_bcb_type=self.og_dos_tuple.trail_sl_bcb_type[set_idx],
            trail_sl_by_pct=self.og_dos_tuple.trail_sl_by_pct[set_idx],
            trail_sl_when_pct=self.og_dos_tuple.trail_sl_when_pct[set_idx],
        )

        logger.info(
            f"""
Settings Index= {self.og_dos_tuple.settings_index[set_idx]}
account_pct_risk_per_trade={round(self.cur_dos_tuple.account_pct_risk_per_trade * 100, 2)}
max_trades={self.cur_dos_tuple.max_trades}
risk_reward={self.cur_dos_tuple.risk_reward}
sl_based_on_add_pct={round(self.cur_dos_tuple.sl_based_on_add_pct * 100, 2)}
sl_based_on_lookback={self.cur_dos_tuple.sl_based_on_lookback}
sl_bcb_type={self.cur_dos_tuple.sl_bcb_type}
sl_to_be_cb_type={self.cur_dos_tuple.sl_to_be_cb_type}
sl_to_be_when_pct={round(self.cur_dos_tuple.sl_to_be_when_pct * 100, 2)}
trail_sl_bcb_type={self.cur_dos_tuple.trail_sl_bcb_type}
trail_sl_by_pct={round(self.cur_dos_tuple.trail_sl_by_pct * 100, 2)}
trail_sl_when_pct={round(self.cur_dos_tuple.trail_sl_when_pct * 100, 2)}
"""
        )

    def candle_chunk(
        self,
        candles: FootprintCandlesTuple,
        beg: int,
        end: int,
    ) -> FootprintCandlesTuple:
        candle_chunk = FootprintCandlesTuple(
            candle_open_datetimes=candles.candle_open_datetimes[beg:end],
            candle_open_timestamps=candles.candle_open_timestamps[beg:end],
            candle_open_prices=candles.candle_open_prices[beg:end],
            candle_high_prices=candles.candle_high_prices[beg:end],
            candle_low_prices=candles.candle_low_prices[beg:end],
            candle_close_prices=candles.candle_close_prices[beg:end],
            candle_asset_volumes=candles.candle_asset_volumes[beg:end],
            candle_usdt_volumes=candles.candle_usdt_volumes[beg:end],
        )
        return candle_chunk

    #######################################################
    #######################################################
    #######################################################
    ##################      Reg      ######################
    ##################      Reg      ######################
    ##################      Reg      ######################
    #######################################################
    #######################################################
    #######################################################

    def set_og_ind_and_dos_tuples(
        self,
        og_ind_set_tuple: IndicatorSettings,
        shuffle_bool: bool,
    ) -> None:
        pass

    def get_filter_cart_prod_array(
        self,
        cart_prod_array: np.ndarray,
    ) -> np.ndarray:
        pass

    def get_og_ind_set_tuple(
        self,
        final_cart_prod_array: np.ndarray,
    ) -> IndicatorSettings:
        pass

    def set_cur_ind_tuple(
        self,
        set_idx: int,
    ):
        pass

    def set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def set_live_bt_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def entry_message(
        self,
        bar_index: int,
    ):
        pass

    def live_evaluate(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def live_bt(
        self,
        beg: int,
        candles: FootprintCandlesTuple,
        end: int,
    ):
        pass

    #######################################################
    #######################################################
    #######################################################
    ##################      Long     ######################
    ##################      Long     ######################
    ##################      Long     ######################
    #######################################################
    #######################################################
    #######################################################

    def long_set_cur_ind_tuple(
        self,
        set_idx: int,
    ):
        pass

    def long_set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def long_entry_message(
        self,
        bar_index: int,
    ):
        pass

    def long_live_evaluate(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def long_live_bt(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    #######################################################
    #######################################################
    #######################################################
    ##################      short    ######################
    ##################      short    ######################
    ##################      short    ######################
    #######################################################
    #######################################################
    #######################################################

    def short_set_cur_ind_tuple(
        self,
        set_idx: int,
    ):
        pass

    def short_set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
        set_idx: int,
    ):
        pass

    def short_entry_message(
        self,
        bar_index: int,
    ):
        pass

    def short_live_evaluate(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def short_live_bt(
        self,
        candles: FootprintCandlesTuple,
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

    def get_strategy_plot_filename(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass
