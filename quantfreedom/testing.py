import numpy as np
import pandas as pd

from numba import njit
from quantfreedom._typing import PossibleArray, pdFrame
from quantfreedom.nb.simulate import backtest_df_array_only_nb
from quantfreedom.nb.execute_funcs import process_order_nb, check_sl_tp_nb
from quantfreedom.nb.helper_funcs import (
    static_var_checker_nb,
    create_1d_arrays_nb,
    check_1d_arrays_nb,
)
from quantfreedom.enums.enums import (
    final_array_dt,
    or_dt,
    AccountState,
    EntryOrder,
    OrderResult,
    StopsOrder,
    SL_BE_or_Trail_BasedOn,
)
