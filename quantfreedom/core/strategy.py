from typing import NamedTuple
import numpy as np
from logging import getLogger
from quantfreedom.core.enums import DynamicOrderSettings, FootprintCandlesTuple

logger = getLogger()


class IndicatorSettings(NamedTuple):
    pass


class Strategy:
    current_ind_settings_tuple: NamedTuple = None
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
    current_dos_tuple: NamedTuple = None

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

    def set_current_dos_tuple(
        self,
        dos_index: int,
    ):
        self.current_dos_tuple = DynamicOrderSettings(
            account_pct_risk_per_trade=self.dos_tuple.account_pct_risk_per_trade[dos_index],
            max_trades=self.dos_tuple.max_trades[dos_index],
            risk_reward=self.dos_tuple.risk_reward[dos_index],
            sl_based_on_add_pct=self.dos_tuple.sl_based_on_add_pct[dos_index],
            sl_based_on_lookback=self.dos_tuple.sl_based_on_lookback[dos_index],
            sl_bcb_type=self.dos_tuple.sl_bcb_type[dos_index],
            sl_to_be_cb_type=self.dos_tuple.sl_to_be_cb_type[dos_index],
            sl_to_be_when_pct=self.dos_tuple.sl_to_be_when_pct[dos_index],
            trail_sl_bcb_type=self.dos_tuple.trail_sl_bcb_type[dos_index],
            trail_sl_by_pct=self.dos_tuple.trail_sl_by_pct[dos_index],
            trail_sl_when_pct=self.dos_tuple.trail_sl_when_pct[dos_index],
        )

        logger.info(
            f"""
Dynamic Order settings index= {dos_index}
max_trades={self.current_dos_tuple.max_trades}
account_pct_risk_per_trade={round(self.current_dos_tuple.account_pct_risk_per_trade * 100, 3)}
risk_reward={self.current_dos_tuple.risk_reward}
sl_based_on_add_pct={round(self.current_dos_tuple.sl_based_on_add_pct * 100, 3)}
sl_based_on_lookback={self.current_dos_tuple.sl_based_on_lookback}
sl_bcb_type={self.current_dos_tuple.sl_bcb_type}
sl_to_be_cb_type={self.current_dos_tuple.sl_to_be_cb_type}
sl_to_be_when_pct={round(self.current_dos_tuple.sl_to_be_when_pct * 100, 3)}
trail_sl_bcb_type={self.current_dos_tuple.trail_sl_bcb_type}
trail_sl_by_pct={round(self.current_dos_tuple.trail_sl_by_pct * 100, 3)}
trail_sl_when_pct={round(self.current_dos_tuple.trail_sl_when_pct * 100, 3)
}"""
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

    def long_set_entries_exits_array(self, candles: FootprintCandlesTuple, ind_set_index: int):
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

    def short_set_entries_exits_array(self, candles: FootprintCandlesTuple, ind_set_index: int):
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

    def long_live_evaluate(self, candles: FootprintCandlesTuple):
        pass

    def short_live_evaluate(self, candles: FootprintCandlesTuple):
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

    def plot_signals(self, candles: FootprintCandlesTuple):
        pass

    def get_strategy_plot_filename(self, candles: FootprintCandlesTuple):
        pass
