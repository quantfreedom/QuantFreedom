from typing import NamedTuple
import numpy as np

from quantfreedom.enums import DynamicOrderSettings


class IndicatorSettings(NamedTuple):
    pass


class Strategy:
    current_ind_settings_tuple = None
    dos_tuple = None
    entries = None
    entry_message = None
    exit_prices = None
    indicator_settings_tuple = None
    live_evaluate = None
    log_folder = None
    log_indicator_settings = None
    long_short = None
    set_entries_exits_array = None
    total_indicator_settings = 1
    total_order_settings = 1

    def __init__(self) -> None:
        pass

    def change_dtypes_of_ind_settings_tuple(self) -> None:
        pass

    def get_ind_set_dos_cart_product(
        self,
        dos_tuple: DynamicOrderSettings,
        indicator_settings_tuple: IndicatorSettings,
    ) -> None:

        for array in dos_tuple:
            self.total_order_settings *= array.size

        for array in indicator_settings_tuple:
            self.total_indicator_settings *= array.size

        the_tuple = dos_tuple + indicator_settings_tuple
        array_size = self.total_order_settings * self.total_indicator_settings

        cart_arrays = np.empty((array_size, len(the_tuple)))

        for i in range(len(the_tuple)):
            m = int(array_size / the_tuple[i].size)
            cart_arrays[:array_size, i] = np.repeat(the_tuple[i], m)
            array_size //= the_tuple[i].size

        array_size = the_tuple[-1].size
        for k in range(len(the_tuple) - 2, -1, -1):
            array_size *= the_tuple[k].size
            m = int(array_size / the_tuple[k].size)
            for j in range(1, the_tuple[k].size):
                cart_arrays[j * m : (j + 1) * m, k + 1 :] = cart_arrays[0:m, k + 1 :]

        cart_arrays = cart_arrays.T

        dos_tuple = DynamicOrderSettings(*tuple(cart_arrays[:11, :]))
        self.dos_tuple = DynamicOrderSettings(
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

        return tuple(cart_arrays[11:, :])

    #######################################################
    #######################################################
    #######################################################
    ##################      Long     ######################
    ##################      Long     ######################
    ##################      Long     ######################
    #######################################################
    #######################################################
    #######################################################

    def long_set_entries_exits_array(self, candles: np.array, ind_set_index: int):
        pass

    def long_log_indicator_settings(self, ind_set_index: int):
        pass

    def long_entry_message(self, bar_index: int):
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

    def short_set_entries_exits_array(self, candles: np.array, ind_set_index: int):
        pass

    def short_log_indicator_settings(self, ind_set_index: int):
        pass

    def short_entry_message(self, bar_index: int):
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

    def live_set_indicator(self, ind_set_index: int):
        pass

    def long_live_evaluate(self, candles: np.array):
        pass

    def short_live_evaluate(self, candles: np.array):
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

    def plot_signals(self, candles: np.array):
        pass

    def get_strategy_plot_filename(self, candles: np.array):
        pass
