import pickle
from time import perf_counter
from quantfreedom.core.backtest import run_df_backtest
from quantfreedom.helpers.helper_funcs import dl_ex_candles
from vol_strat import long_strat, backtest_settings_tuple, exchange_settings_tuple, static_os_tuple
from datetime import datetime
from time import gmtime, strftime
from os.path import exists
from os import remove

if __name__ == "__main__":
    start = perf_counter()
    if exists("backtest_results.h5"):
        remove("backtest_results.h5")

    print("Downloading candles")
    with open('thing.pkl', 'rb') as f:
        candles = pickle.load(f) 
    backtest_results = run_df_backtest(
        backtest_settings_tuple=backtest_settings_tuple,
        candles=candles,
        exchange_settings_tuple=exchange_settings_tuple,
        static_os_tuple=static_os_tuple,
        strategy=long_strat,
        threads=32,
    )
    print("\n\nBacktest results done now saving to hdf5")
    backtest_results.to_hdf("backtest_results.h5", key="backtest_results", mode="w")

    end = perf_counter()
    print(strftime("\n\nIt took %M mins and %S seconds to complete the backtest", gmtime(int(end - start))))
