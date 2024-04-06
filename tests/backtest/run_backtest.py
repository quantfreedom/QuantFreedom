import sys, os
from time import perf_counter
from quantfreedom.backtest import run_df_backtest
from quantfreedom.helper_funcs import dl_ex_candles
from strat import long_strat, backtest_settings_tuple, exchange_settings_tuple, static_os_tuple
from datetime import datetime
from time import gmtime, strftime


if __name__ == "__main__":
    start = perf_counter()
    if os.path.exists("backtest_results.h5"):
        os.remove("backtest_results.h5")

    print("Downloading candles")
    candles = dl_ex_candles(
        exchange="binance_usdm",
        symbol="BTCUSDT",
        timeframe="5m",
        since_datetime=datetime(2024, 3, 1),
        until_datetime=datetime(2024, 4, 6),
    )
    backtest_results = run_df_backtest(
        backtest_settings_tuple=backtest_settings_tuple,
        candles=candles,
        exchange_settings_tuple=exchange_settings_tuple,
        static_os_tuple=static_os_tuple,
        strategy=long_strat,
        threads=int(sys.argv[1]),
        # threads=10,
    )
    backtest_results.to_hdf("backtest_results.h5", key="backtest_results", mode="w")

    end = perf_counter()
    print("It took %M mins and %S seconds to complete the backtest", gmtime(int(end - start)))
