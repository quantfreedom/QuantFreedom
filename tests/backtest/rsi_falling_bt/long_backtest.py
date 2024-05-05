from time import perf_counter
from quantfreedom.core.backtest import run_df_backtest
from quantfreedom.helpers.helper_funcs import dl_ex_candles
from strat import long_strat, backtest_settings_tuple, exchange_settings_tuple, static_os_tuple
from datetime import datetime
from time import gmtime, strftime
from os.path import exists
from os import remove

if __name__ == "__main__":
    start = perf_counter()
    if exists("backtest_results.h5"):
        remove("backtest_results.h5")

    print("Downloading candles")
    candles = dl_ex_candles(
        exchange="mufex",
        symbol="BTCUSDT",
        timeframe="5m",
        since_datetime=datetime(2023, 10, 1),
        until_datetime=datetime(2023, 11, 1),
    )
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
