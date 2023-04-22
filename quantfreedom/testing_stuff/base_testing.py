import numpy as np
import pandas as pd

from quantfreedom._typing import pdFrame
from quantfreedom.testing_stuff.enums_testing import *
from quantfreedom.testing_stuff.helper_funcs_testing import *


def backtest_df_only_testing(
    # entry info
    price_data: pdFrame,
    entries: pdFrame,
    entry_order_tuple: EntryOrder,
    static_variables_tuple: StaticVariables,
    stops_order_tuple: StopsOrder,
) -> tuple[pdFrame, pdFrame]:
    print("Checking static variables for errors or conflicts.")
    # Static checks
    static_variables_tuple = static_var_checker_nb_testing(
        static_variables_tuple=static_variables_tuple,
    )
    print("Turning all variables into arrays.")
    # Create 1d Arrays
    arrays_1d_tuple = create_1d_arrays_nb_testing(
        entry_order_tuple=entry_order_tuple,
        stops_order_tuple=stops_order_tuple,
    )
    print(
        "Checking arrays for errors or conflicts ... the backtest will begin shortly, please hold."
    )
    # Checking all new arrays
    check_1d_arrays_nb_testing(
        arrays_1d_tuple=arrays_1d_tuple,
        static_variables_tuple=static_variables_tuple,
    )

    print(
        "Creating cartesian product ... after this the backtest will start, I promise :).\n"
    )
    cart_array_tuple = create_cart_product_nb_testing(arrays_1d_tuple=arrays_1d_tuple)

    num_of_symbols = len(price_data.columns.levels[0])

    # Creating Settings Vars
    total_order_settings = cart_array_tuple.sl_init_pct.shape[0]

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

    strat_array, settings_array = backtest_df_only_nb_testing(
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

    strat_results_df = pd.DataFrame(strat_array).sort_values(
        by=["to_the_upside", "gains_pct"], ascending=False
    )

    symbols = list(price_data.columns.levels[0])

    for i in range(len(symbols)):
        strat_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    symbols = list(entries.columns.levels[0])
    setting_results_df = pd.DataFrame(settings_array).dropna(axis="columns", thresh=1)

    for i in range(len(CandleBody._fields)):
        setting_results_df.replace(
            {"tsl_based_on": {i: CandleBody._fields[i]}}, inplace=True
        )
        setting_results_df.replace(
            {"sl_to_be_based_on": {i: CandleBody._fields[i]}}, inplace=True
        )
    for i in range(len(symbols)):
        setting_results_df.replace({"symbol": {i: symbols[i]}}, inplace=True)

    setting_results_df = setting_results_df.T

    return strat_results_df, setting_results_df
