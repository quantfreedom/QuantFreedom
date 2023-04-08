import numpy as np
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from quantfreedom.nb.simulate import backtest_df_only_nb
from quantfreedom.nb.helper_funcs import (
    static_var_checker_nb,
    create_1d_arrays_nb,
    check_1d_arrays_nb,
    create_cart_product_nb,
)
from quantfreedom._typing import (
    plSeries,
    pdFrame,
    RecordArray,
    PossibleArray,
)
from quantfreedom.enums.enums import OrderType, SL_BE_or_Trail_BasedOn


def backtest_df_only(
    # entry info
    entries: pdFrame,
    prices: pdFrame,
    # required account info
    equity: float,
    fee_pct: float,
    mmr: float,
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
    sl_to_be_based_on: PossibleArray = np.nan,
    sl_to_be_when_pct_from_avg_entry: PossibleArray = np.nan,
    sl_to_be_zero_or_entry: PossibleArray = np.nan,
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
) -> tuple[pdFrame, pdFrame]:

    print("Checking static variables for errors or conflicts.")
    # Static checks
    static_variables_tuple = static_var_checker_nb(
        equity=equity,
        fee_pct=fee_pct,
        mmr=mmr,
        lev_mode=lev_mode,
        order_type=order_type,
        size_type=size_type,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        min_order_size_pct=min_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_value=min_order_size_value,
        sl_to_be=sl_to_be,
        sl_to_be_then_trail=sl_to_be_then_trail,
        tsl_true_or_false=tsl_true_or_false,
        gains_pct_filter=gains_pct_filter,
        total_trade_filter=total_trade_filter,
    )
    print("Turning all variables into arrays.")
    # Create 1d Arrays
    arrays_1d_tuple = create_1d_arrays_nb(
        leverage=leverage,
        max_equity_risk_pct=max_equity_risk_pct,
        max_equity_risk_value=max_equity_risk_value,
        risk_rewards=risk_rewards,
        size_pct=size_pct,
        size_value=size_value,
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
    print(
        "Checking arrays for errors or conflicts ... the backtest will begin shortly, please hold."
    )
    # Checking all new arrays
    check_1d_arrays_nb(
        static_variables_tuple=static_variables_tuple,
        arrays_1d_tuple=arrays_1d_tuple,
    )

    print(
        "Creating cartesian product ... after this the backtest will start, I promise :).\n"
    )
    cart_array_tuple = create_cart_product_nb(arrays_1d_tuple=arrays_1d_tuple)

    num_of_symbols = len(prices.columns.levels[0])

    # Creating Settings Vars
    total_order_settings = cart_array_tuple.sl_pcts.shape[0]

    total_indicator_settings = entries.shape[1]

    total_bars = entries.shape[0]

    # Printing out total numbers of things
    print(
        "Starting the backtest now ... and also here are some stats for your backtest.\n"
    )
    print(f"Total symbols: {num_of_symbols:,}")
    print(
        f"Total indicator settings per symbol: {int(total_indicator_settings / num_of_symbols):,}"
    )
    print(f"Total indicator settings to test: {total_indicator_settings:,}")
    print(f"Total order settings per symbol: {total_order_settings:,}")
    print(f"Total order settings to test: {total_order_settings * num_of_symbols:,}")
    print(f"Total candles per symbol: {total_bars:,}")
    print(
        f"Total candles to test: {total_indicator_settings * total_order_settings * total_bars:,}"
    )
    print(
        f"\nTotal combinations to test: {total_indicator_settings * total_order_settings:,}"
    )

    strat_array, settings_array = backtest_df_only_nb(
        num_of_symbols=num_of_symbols,
        total_indicator_settings=total_indicator_settings,
        total_order_settings=total_order_settings,
        total_bars=total_bars,
        og_equity=equity,
        entries=entries.values,
        prices=prices.values,
        gains_pct_filter=gains_pct_filter,
        total_trade_filter=total_trade_filter,
        static_variables_tuple=static_variables_tuple,
        cart_array_tuple=cart_array_tuple,
    )

    strat_results_df = pd.DataFrame(strat_array).sort_values(
        by=["to_the_upside", "gains_pct"], ascending=False
    )

    symbols = list(prices.columns.levels[0])

    for i in range(len(symbols)):
        strat_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    symbols = list(entries.columns.levels[0])
    setting_results_df = pd.DataFrame(settings_array).dropna(axis="columns", thresh=1)

    for i in range(len(SL_BE_or_Trail_BasedOn._fields)):
        setting_results_df.replace(
            {"tsl_based_on": {i: SL_BE_or_Trail_BasedOn._fields[i]}}, inplace=True
        )
        setting_results_df.replace(
            {"sl_to_be_based_on": {i: SL_BE_or_Trail_BasedOn._fields[i]}}, inplace=True
        )
    for i in range(len(symbols)):
        setting_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    setting_results_df = setting_results_df.T

    return strat_results_df, setting_results_df


