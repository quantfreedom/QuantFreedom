import numpy as np


class Strategy:
    current_ind_settings = None
    empty_ind_tup = None
    entries = None
    entry_message = None
    exit_prices = None
    indicator_settings_arrays = None
    live_evaluate = None
    log_folder = None
    log_indicator_settings = None
    long_short = None
    set_entries_exits_array = None

    def __init__(self) -> None:
        pass

    def change_ind_settings_to_ints(self) -> None:
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
