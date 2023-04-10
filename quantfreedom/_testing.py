"""
    Function Name
    -------------
        backtest_df_only

    Quick Summary
    -------------
        The main way to backtest your strategy. 
        I highly highly highly suggest watching the explainer video
        I explain what everything does and means in great detail.

    Explainer Video
    ---------------
        <a>https://youtu.be/yDNPhgO-450</a>
        
    mmr_pct: float
        maintenance margin rate this is for bybit but i am not sure what other exchange also have this but please check your exchange and this
    lev_mode: int
    order_type: int
    size_type: int

    Optional Parameters
    -------------------
    Variable Name: Variable Type, Default Value

    leverage: PossibleArray, np.nan
    max_equity_risk_pct: PossibleArray, np.nan
    max_equity_risk_value: PossibleArray, np.nan
        What is the max usd amount of your equity do you want to possibly risk
    max_order_size_pct: float, 100.0
        max order size percent possible
    min_order_size_pct: float, 0.01
        min order size percent possible
    max_order_size_value: float, np.inf
        max order size usd value possible
    min_order_size_value: float, 1.0
        min order size usd value possible
    max_lev: float, 100.0
        setting your max leverage
    size_pct: PossibleArray, np.nan
        When you have selected a size type that is based on percent you put your size percent here.
    size_value: PossibleArray, np.nan
        when you selected a size type that is based on value you put your size value here.
    sl_pcts: PossibleArray, np.nan
        stop loss based on percent
    sl_to_be: bool, False
        if you want to move your stop loss to break even
    sl_to_be_based_on: PossibleArray, np.nan
        Selecting what part of the candle you want your stop loss to break even to based on. Please look in enums api to find out more info on SL_BE_or_Trail_BasedOn
    sl_to_be_when_pct_from_avg_entry: PossibleArray, np.nan
        how far in percent does the price have to be from your average entry to move your stop loss to break even
    sl_to_be_zero_or_entry: PossibleArray, np.nan
        do you want to have your break even be zero dollars lost or moving your stop loss to your average entry. Use 0 for zero and use 1 for average entry
    sl_to_be_trail_by_when_pct_from_avg_entry: PossibleArray, np.nan
        how much, in percent, do you want to trail the price by, set that here
    tsl_pcts_init: PossibleArray, np.nan
        your initial stop loss
    tsl_true_or_false: bool, False
        if you want to have a trailing stop loss this must be set to true
    tsl_based_on: PossibleArray, np.nan
        Selecting what part of the candle you want your trailing stop loss to be based on. Please look in enums api to find out more info on SL_BE_or_Trail_BasedOn
    tsl_trail_by_pct: PossibleArray, np.nan
        how much percent from the price do you want to trail your stop loss
    tsl_when_pct_from_avg_entry: PossibleArray, np.nan
        at what percent from the price should the trailing stop loss strat trailing
    risk_rewards: PossibleArray, np.nan
        risk to reward, don't set a tp percent if you are going to use risk to reward
    tp_pcts: PossibleArray, np.nan
        take profit percent, don't set this if you are going to use risk to reward
    gains_pct_filter: float, -np.inf
        don't return any strategies that have gains less than the percent set here
    total_trade_filter: int, 0
        don't return any strategies that have a total trade amount that is less than this filter
    divide_records_array_size_by: float, 1.0
        if you have a ton of combinations you are testing with very strict filters then put this number higher like 100 or more, if you have very low filters then set it to 10 or 5 or something and if you have absolutely no filters then leave this at 1. This basically saves you memory so if you have 5 mil combinations but strict filters then you could reduce the amount of rows by like 100 which would be 5000000 / 100 which would create 50,000 rows for the array instead of 5 million
    upside_filter: float, -1.0
        How you want to filter strategies that don't meet the to the upside numbers you want. Please watch the video to understand what to the upside is but it is basically the r2 value of the cumilative sum of the strategies pnl.

    Returns
    -------
    tuple[pdFrame, pdFrame]
        First return is a dataframe of strategy results
        Second return is a dataframe of the indicator and order settings
    """