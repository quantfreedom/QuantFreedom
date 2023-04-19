import numpy as np
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
    pdFrame,
    PossibleArray,
)
from quantfreedom.enums.enums import OrderType, CandleBody


def backtest_df_only(
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
    """
    Function Name
    -------------
    backtest_df_only

    Quick Summary
    -------------
    The main way to backtest your strategy. I highly highly highly suggest watching the explainer video. I explain what everything does and means in great detail.

    Explainer Video
    ---------------
    https://youtu.be/yDNPhgO-450

    Parameters
    ----------
    price_data : pdFrame
        Dataframe of price_data
    entries : pdFrame
        Dataframe of entries
    equity : float
        Starting equity. I suggest only doing 100 or 1000 dollars
    fee_pct : float
        Fees percent
    mmr_pct : float
        maintenance margin rate this is for bybit but i am not sure what other exchange also have this but please check your exchange and this
    lev_mode : int
        Selecting your leverage mode. Look in the enums api section for LeverageMode
    order_type : int
        Selecting your order type. Please only use long short or both. Look in the enums api section for OrderType
    size_type : int
        Selecting your size type. Look in the enums api section for SizeType
    leverage : PossibleArray, np.nan
        If your leverage mode is isolated this is where you put in how much leverage you want to use.
    max_equity_risk_pct : PossibleArray, np.nan
        What is the max equity percent you want to possibly risk
    max_equity_risk_value : PossibleArray, np.nan
        What is the max usd amount of your equity do you want to possibly risk
    max_order_size_pct : float, 100.0
        max order size percent possible
    min_order_size_pct : float, 0.01
        min order size percent possible
    max_order_size_value : float, np.inf
        max order size usd value possible
    min_order_size_value : float, 1.0
        min order size usd value possible
    max_lev : float, 100.0
        setting your max leverage
    size_pct : PossibleArray, np.nan
        When you have selected a size type that is based on percent you put your size percent here.
    size_value : PossibleArray, np.nan
        when you selected a size type that is based on value you put your size value here.
    sl_based_on : PossibleArray, np.nan
        stop loss based on open high low close of candle
    sl_based_on_add_pct : PossibleArray, np.nan
        add a specific percentage amount to the stop loss
    sl_pcts : PossibleArray, np.nan
        stop loss based on percent
    sl_to_be : bool, False
        if you want to move your stop loss to break even
    sl_to_be_based_on : PossibleArray, np.nan
        Selecting what part of the candle you want your stop loss to break even to based on. Please look in enums api to find out more info on CandleBody
    sl_to_be_when_pct_from_avg_entry : PossibleArray, np.nan
        how far in percent does the price have to be from your average entry to move your stop loss to break even
    sl_to_be_zero_or_entry : PossibleArray, np.nan
        do you want to have your break even be zero dollars lost or moving your stop loss to your average entry. Use 0 for zero and use 1 for average entry
    sl_to_be_trail_by_when_pct_from_avg_entry : PossibleArray, np.nan
        how much, in percent, do you want to trail the price by, set that here
    tsl_pcts_init : PossibleArray, np.nan
        your initial stop loss
    tsl_true_or_false : bool, False
        if you want to have a trailing stop loss this must be set to true
    tsl_based_on : PossibleArray, np.nan
        Selecting what part of the candle you want your trailing stop loss to be based on. Please look in enums api to find out more info on CandleBody
    tsl_trail_by_pct : PossibleArray, np.nan
        how much percent from the price do you want to trail your stop loss
    tsl_when_pct_from_avg_entry : PossibleArray, np.nan
        at what percent from the price should the trailing stop loss strat trailing
    risk_rewards : PossibleArray, np.nan
        risk to reward, don't set a tp percent if you are going to use risk to reward
    tp_pcts : PossibleArray, np.nan
        take profit percent, don't set this if you are going to use risk to reward
    gains_pct_filter : float, -np.inf
        don't return any strategies that have gains less than the percent set here
    total_trade_filter : int, 0
        don't return any strategies that have a total trade amount that is less than this filter
    divide_records_array_size_by : float, 1.0
        if you have a ton of combinations you are testing with very strict filters then put this number higher like 100 or more, if you have very low filters then set it to 10 or 5 or something and if you have absolutely no filters then leave this at 1. This basically saves you memory so if you have 5 mil combinations but strict filters then you could reduce the amount of rows by like 100 which would be 5000000 / 100 which would create 50,000 rows for the array instead of 5 million
    upside_filter : float, -1.0
        How you want to filter strategies that don't meet the to the upside numbers you want. Please watch the video to understand what to the upside is but it is basically the r2 value of the cumilative sum of the strategies pnl.

    Returns
    -------
    tuple[pdFrame, pdFrame]
        First return is a dataframe of strategy results.
        Second return is a dataframe of the indicator and order settings.
    """
    print("Checking static variables for errors or conflicts.")
    # Static checks
    static_variables_tuple = static_var_checker_nb(
        equity=equity,
        divide_records_array_size_by=divide_records_array_size_by,
        fee_pct=fee_pct,
        gains_pct_filter=gains_pct_filter,
        lev_mode=lev_mode,
        max_lev=max_lev,
        max_order_size_pct=max_order_size_pct,
        max_order_size_value=max_order_size_value,
        min_order_size_pct=min_order_size_pct,
        min_order_size_value=min_order_size_value,
        mmr_pct=mmr_pct,
        order_type=order_type,
        size_type=size_type,
        sl_to_be_then_trail=sl_to_be_then_trail,
        sl_to_be=sl_to_be,
        total_trade_filter=total_trade_filter,
        tsl_true_or_false=tsl_true_or_false,
        upside_filter=upside_filter,
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
    print(
        "Checking arrays for errors or conflicts ... the backtest will begin shortly, please hold."
    )
    # Checking all new arrays
    check_1d_arrays_nb(
        arrays_1d_tuple=arrays_1d_tuple,
        static_variables_tuple=static_variables_tuple,
    )

    print(
        "Creating cartesian product ... after this the backtest will start, I promise :).\n"
    )
    cart_array_tuple = create_cart_product_nb(arrays_1d_tuple=arrays_1d_tuple)

    num_of_symbols = len(price_data.columns.levels[0])

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
