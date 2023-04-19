import numpy as np
import numpy as np
import pandas as pd

from quantfreedom.nb.simulate_test import sim_test_thing_nb

from quantfreedom._typing import (
    pdFrame,
    PossibleArray,
)
from quantfreedom.enums.enums import (
    OrderType,
    CandleBody,
    Arrays1dTuple,
    StaticVariables,
)


def sim_6_base(
    entries,
    price_data,
    static_variables_tuple: StaticVariables,
    broadcast_arrays: Arrays1dTuple,
) -> tuple[pdFrame, pdFrame]:
    
    order_records = sim_test_thing_nb(
        price_data=price_data,
        entries=entries,
        static_variables_tuple=static_variables_tuple,
        broadcast_arrays=broadcast_arrays,
    )

    return strat_results_df, setting_results_df
