from typing import NamedTuple
import numpy as np
from logging import getLogger
from quantfreedom.core.enums import DynamicOrderSettings, FootprintCandlesTuple

logger = getLogger()


class IndicatorSettings(NamedTuple):
    pass


class Strategy:
    cur_dos_tuple: DynamicOrderSettings = None
    cur_ind_set_tuple: IndicatorSettings = None
    entries: np.ndarray = None
    entry_message = None
    exit_prices: np.ndarray = None
    live_evaluate = None
    log_folder: str = None
    long_short: str = None
    og_dos_tuple: DynamicOrderSettings = None
    og_ind_set_tuple: IndicatorSettings = None
    set_entries_exits_array: np.ndarray = None
    total_indicator_settings: int = 0
    total_order_settings: int = 0

    def __init__(self) -> None:
        pass

    def get_ind_set_dos_cart_product(
        self,
        og_dos_tuple: DynamicOrderSettings,
        og_ind_set_tuple: IndicatorSettings,
    ) -> None:
        total_indicator_settings = 1
        total_order_settings = 1

        for array in og_dos_tuple:
            total_order_settings *= array.size
        logger.debug(f"Total Order Settings: {total_order_settings}")

        for array in og_ind_set_tuple:
            total_indicator_settings *= array.size
        logger.debug(f"Total Indicator Settings: {total_indicator_settings}")

        the_tuple = og_dos_tuple + og_ind_set_tuple
        array_size = total_order_settings * total_indicator_settings
        logger.debug(f"Total Array Size: {array_size}")

        cart_arrays = np.empty((array_size, len(the_tuple)))

        for i in range(len(the_tuple)):
            m = int(array_size / the_tuple[i].size)
            cart_arrays[:array_size, i] = np.repeat(the_tuple[i], m)
            array_size //= the_tuple[i].size

        array_size = the_tuple[-1].size
        logger.debug("array_size")

        for k in range(len(the_tuple) - 2, -1, -1):
            array_size *= the_tuple[k].size
            m = int(array_size / the_tuple[k].size)
            for j in range(1, the_tuple[k].size):
                cart_arrays[j * m : (j + 1) * m, k + 1 :] = cart_arrays[0:m, k + 1 :]

        logger.debug("cart_arrays")
        return cart_arrays.T

    def get_og_dos_tuple(
        self,
        filtered_cart_arrays: np.ndarray,
    ) -> DynamicOrderSettings:

        dos_tuple = DynamicOrderSettings(*tuple(filtered_cart_arrays[:11]))
        logger.debug("dos_tuple")

        og_dos_tuple = DynamicOrderSettings(
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

    def set_cur_dos_tuple(
        self,
        dos_index: int,
    ):
        self.cur_dos_tuple = DynamicOrderSettings(
            account_pct_risk_per_trade=self.og_dos_tuple.account_pct_risk_per_trade[dos_index],
            max_trades=self.og_dos_tuple.max_trades[dos_index],
            risk_reward=self.og_dos_tuple.risk_reward[dos_index],
            sl_based_on_add_pct=self.og_dos_tuple.sl_based_on_add_pct[dos_index],
            sl_based_on_lookback=self.og_dos_tuple.sl_based_on_lookback[dos_index],
            sl_bcb_type=self.og_dos_tuple.sl_bcb_type[dos_index],
            sl_to_be_cb_type=self.og_dos_tuple.sl_to_be_cb_type[dos_index],
            sl_to_be_when_pct=self.og_dos_tuple.sl_to_be_when_pct[dos_index],
            trail_sl_bcb_type=self.og_dos_tuple.trail_sl_bcb_type[dos_index],
            trail_sl_by_pct=self.og_dos_tuple.trail_sl_by_pct[dos_index],
            trail_sl_when_pct=self.og_dos_tuple.trail_sl_when_pct[dos_index],
        )

        logger.info(
            f"""
Dynamic Order settings index= {dos_index}
account_pct_risk_per_trade={round(self.cur_dos_tuple.account_pct_risk_per_trade * 100, 3)}
max_trades={self.cur_dos_tuple.max_trades}
risk_reward={self.cur_dos_tuple.risk_reward}
sl_based_on_add_pct={round(self.cur_dos_tuple.sl_based_on_add_pct * 100, 3)}
sl_based_on_lookback={self.cur_dos_tuple.sl_based_on_lookback}
sl_bcb_type={self.cur_dos_tuple.sl_bcb_type}
sl_to_be_cb_type={self.cur_dos_tuple.sl_to_be_cb_type}
sl_to_be_when_pct={round(self.cur_dos_tuple.sl_to_be_when_pct * 100, 3)}
trail_sl_bcb_type={self.cur_dos_tuple.trail_sl_bcb_type}
trail_sl_by_pct={round(self.cur_dos_tuple.trail_sl_by_pct * 100, 3)}
trail_sl_when_pct={round(self.cur_dos_tuple.trail_sl_when_pct * 100, 3)
}"""
        )

    def set_og_ind_and_dos_tuples(
        self,
        og_ind_set_tuple: IndicatorSettings,
        shuffle_bool: bool,
    ) -> None:
        pass

    def get_filter_cart_arrays(
        self,
        cart_arrays: np.ndarray,
    ) -> np.ndarray:
        pass

    def get_og_ind_set_tuple(
        self,
        cart_arrays: np.ndarray,
        filtered_cart_arrays: np.ndarray,
    ) -> IndicatorSettings:
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

    def long_set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
        ind_set_index: int,
    ):
        pass

    def long_entry_message(
        self,
        bar_index: int,
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

    def short_set_entries_exits_array(
        self,
        candles: FootprintCandlesTuple,
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
    ##################      Live     ######################
    ##################      Live     ######################
    ##################      Live     ######################
    #######################################################
    #######################################################
    #######################################################

    def live_set_indicator(
        self,
        ind_set_index: int,
    ):
        pass

    def long_live_evaluate(
        self,
        candles: FootprintCandlesTuple,
    ):
        pass

    def short_live_evaluate(
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
