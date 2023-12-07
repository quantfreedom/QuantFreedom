from typing import Callable, NamedTuple
import numpy as np


class IndicatorSettingsArrays(NamedTuple):
    """
    Summary
    -------
    _summary_

    Explainer Video
    ---------------
    Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

    Parameters
    ----------
    NamedTuple : _type_
        _description_

    """

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
        """
        Summary
        -------
        _summary_

        Explainer Video
        ---------------
        Coming Soon but if you want/need it now please let me know in discord or telegram and i will make it for you

        Parameters
        ----------
        long_short : str
            _description_

        """
        self.long_short = long_short

    def testing(self):
        pass
