import numpy as np
import numpy as np
import pandas as pd

from quantfreedom.nb.simulate import backtest_df_only_nb
from quantfreedom.nb.helper_funcs import (
    static_var_checker_nb,
    create_1d_arrays_nb,
    check_1d_arrays_nb,
    create_cart_product_nb,
    boradcast_to_1d_arrays,
)
from quantfreedom._typing import (
    pdFrame,
    PossibleArray,
)
from quantfreedom.enums.enums import OrderType, CandleBody


def sim_6_base(
    # entry info
    price_data: pdFrame,
    entries: pdFrame,
    # required account info
    equity: float,
    fee_pct: float,
    mmr_pct: float,
    # required order
    lev_mode: int,
    order_type: int,
    size_type: int,
    # Order Params
    leverage: PossibleArray = np.nan,
    max_equity_risk_pct: PossibleArray = np.nan,
    max_equity_risk_value: PossibleArray = np.nan,
    max_order_size_pct: float = 100.0,
    min_order_size_pct: float = 0.01,
    max_order_size_value: float = np.inf,
    min_order_size_value: float = 1.0,
    max_lev: float = 100.0,
    size_pct: PossibleArray = np.nan,
    size_value: PossibleArray = np.nan,
    # Stop Losses
    sl_pcts: PossibleArray = np.nan,
    sl_to_be: bool = False,
    sl_based_on: PossibleArray = np.nan,
    sl_based_on_add_pct: PossibleArray = np.nan,
    sl_to_be_based_on: PossibleArray = np.nan,
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan,
    sl_to_be_zero_or_entry: PossibleArray = np.nan,  # 0 for zero or 1 for entry
    sl_to_be_then_trail: bool = False,
    sl_to_be_trail_by_when_pct_from_avg_entry: PossibleArray = np.nan,
    # Trailing Stop Loss Params
    tsl_pcts_init: PossibleArray = np.nan,
    tsl_true_or_false: bool = False,
    tsl_based_on: PossibleArray = np.nan,
    tsl_trail_by_pct: PossibleArray = np.nan,
    tsl_when_pct_from_avg_entry: PossibleArray = np.nan,
    # Take Profit Params
    risk_rewards: PossibleArray = np.nan,
    tp_pcts: PossibleArray = np.nan,
    # Results Filters
    gains_pct_filter: float = -np.inf,
    total_trade_filter: int = 0,
    divide_records_array_size_by: float = 1.0,  # between 1 and 1000
    upside_filter: float = -1.0,  # between -1 and 1
) -> tuple[pdFrame, pdFrame]:
    
    print("Turning all variables into arrays.")
    # Create 1d Arrays
    arrays_1d_tuple = create_1d_arrays_nb(
        leverage=leverage,
        max_equity_risk_pct=max_equity_risk_pct,
        max_equity_risk_value=max_equity_risk_value,
        risk_rewards=risk_rewards,
        size_pct=size_pct,
        size_value=size_value,
        sl_based_on_add_pct=sl_based_on_add_pct,
        sl_based_on=sl_based_on,
        sl_pcts=sl_pcts,
        sl_to_be_based_on=sl_to_be_based_on,
        sl_to_be_trail_by_when_pct_from_avg_entry=sl_to_be_trail_by_when_pct_from_avg_entry,
        sl_to_be_when_pct_from_avg_entry=sl_to_be_when_pct_from_avg_entry,
        sl_to_be_zero_or_entry=sl_to_be_zero_or_entry,
        tp_pcts=tp_pcts,
        tsl_based_on=tsl_based_on,
        tsl_pcts_init=tsl_pcts_init,
        tsl_trail_by_pct=tsl_trail_by_pct,
        tsl_when_pct_from_avg_entry=tsl_when_pct_from_avg_entry,
    )
    
    entries, broadcast_arrays = boradcast_to_1d_arrays(
        arrays_1d_tuple=arrays_1d_tuple,
        entries=entries,
    )
    
    num_of_symbols = len(price_data.columns.levels[0])

    # Creating Settings Vars
    total_order_settings = broadcasted_arrays.sl_pcts.shape[0]

    total_indicator_settings = entries.shape[1]

    total_bars = entries.shape[0]

    strat_array, settings_array = backtest_df_only_nb(
        cart_array_tuple=cart_array_tuple,
        entries=entries.values,
        gains_pct_filter=gains_pct_filter,
        num_of_symbols=num_of_symbols,
        og_equity=equity,
        price_data=price_data.values,
        static_variables_tuple=static_variables_tuple,
        total_bars=total_bars,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
        total_trade_filter=total_trade_filter,
    )


    return strat_results_df, setting_results_df
