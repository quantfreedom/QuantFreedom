from typing import Callable, NamedTuple
import numpy as np


class IndicatorSettingsArrays(NamedTuple):
    pass


class Strategy:
    set_entries_exits_array: Callable
    log_indicator_settings: Callable
    entry_message: Callable
    entries_strat: np.array
    indicator_settings_arrays: IndicatorSettingsArrays

    def __init__(
        self,
        long_short: str,
    ) -> None:
        self.long_short = long_short
