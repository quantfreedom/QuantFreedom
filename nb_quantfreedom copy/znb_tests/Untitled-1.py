# %%
# import sys
# import os
# sys.dont_write_bytecode = True
# os.environ["NUMBA_DISABLE_JIT"] = "1"

import os
os.environ["NUMBA_DEBUG_CACHE"] = "1"

# %%
import numpy as np
import pandas as pd
from my_stuff import MufexKeys
from nb_quantfreedom.exchanges.mufex_exchange.mufex import Mufex
from nb_quantfreedom.nb_enums import DynamicOrderSettingsArrays
from nb_quantfreedom.utils import pretty_qf
from requests import get
from numba import njit, types, typed
from numba.experimental import jitclass
import logging
from nb_quantfreedom.nb_enums import *
from nb_quantfreedom.nb_helper_funcs import dos_cart_product
from nb_quantfreedom.strategies.nb_strategy import (
    strat_bt_create_ind,
    strat_evaluate,
    strat_get_current_ind_settings,
    strat_get_ind_set_str,
    strat_get_total_ind_settings,
)
from nb_quantfreedom.nb_simulate import sim_df_backtest
from nb_quantfreedom.sim_order_records import sim_get_or


mufex_main = Mufex(
    api_key=MufexKeys.api_key,
    secret_key=MufexKeys.secret_key,
    use_test_net=False,
)

# %%
candles_np = mufex_main.get_candles_df(symbol="BTCUSDT", timeframe="5m", candles_to_dl=2000)

# %%
mufex_main.set_exchange_settings(
    symbol="BTCUSDT",
    position_mode=PositionModeType.HedgeMode,
    leverage_mode=LeverageModeType.Isolated,
)
backtest_settings = BacktestSettings(
    divide_records_array_size_by=10,
    gains_pct_filter=-95,
    total_trade_filter=80,
    upside_filter=-np.inf,
)
dos_arrays = DynamicOrderSettingsArrays(
    entry_size_asset=np.array([0]),
    max_equity_risk_pct=np.array([6, 9, 12]),
    max_trades=np.array([5]),
    num_candles=np.array([100]),
    risk_account_pct_size=np.array([3]),
    risk_reward=np.array([2, 3, 5]),
    sl_based_on_add_pct=np.array([0.01, 0.02, 0.03]),
    sl_based_on_lookback=np.array([10, 20, 30]),
    sl_bcb_type=np.array([CandleBodyType.Low]),
    sl_to_be_cb_type=np.array([CandleBodyType.Nothing]),
    sl_to_be_when_pct=np.array([0]),
    sl_to_be_ze_type=np.array([0]),
    static_leverage=np.array([0]),
    trail_sl_bcb_type=np.array([CandleBodyType.Low]),
    trail_sl_by_pct=np.array([0.5, 0.3, 0.1, 1.0]),
    trail_sl_when_pct=np.array([0.0009, 0.001, 0.002, 0.003]),
)
static_os = StaticOrderSettings(
    increase_position_type=IncreasePositionType.RiskPctAccountEntrySize,
    leverage_strategy_type=LeverageStrategyType.Dynamic,
    long_or_short=LongOrShortType.Long,
    logger_bool=True,
    pg_min_max_sl_bcb=PriceGetterType.Min,
    sl_to_be_bool=False,
    z_or_e_type=ZeroOrEntryType.Nothing,
    sl_strategy_type=StopLossStrategyType.SLBasedOnCandleBody,
    tp_strategy_type=TakeProfitStrategyType.RiskReward,
    tp_fee_type=TakeProfitFeeType.Limit,
    trail_sl_bool=True,
)
dos_cart_arrays = dos_cart_product(
    dos_arrays=dos_arrays,
)

# %%
database = sim_df_backtest(
    backtest_settings=backtest_settings,
    candles=candles_np,
    dos_cart_arrays=dos_cart_arrays,
    evaluate=strat_evaluate,
    exchange_settings=mufex_main.exchange_settings,
    get_current_ind_settings=strat_get_current_ind_settings,
    get_ind_set_str=strat_get_ind_set_str,
    get_total_ind_settings=strat_get_total_ind_settings,
    ind_creator=strat_bt_create_ind,
    logger_type=LoggerType.Pass,
    starting_equity=1000.0,
    static_os=static_os,
)


print(database)
print("")