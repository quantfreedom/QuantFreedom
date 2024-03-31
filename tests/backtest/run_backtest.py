import sys
from time import perf_counter
from quantfreedom.backtest import run_df_backtest
from quantfreedom.helper_funcs import dl_ex_candles
from strat import long_strat, backtest_settings_tuple, exchange_settings_tuple, static_os_tuple


if __name__ == "__main__":
    start = perf_counter()

    candles = dl_ex_candles(
        exchange="mufex",
        symbol="BTCUSDT",
        timeframe="5m",
        candles_to_dl=3000,
    )
    backtest_results = run_df_backtest(
        backtest_settings_tuple=backtest_settings_tuple,
        candles=candles,
        exchange_settings_tuple=exchange_settings_tuple,
        static_os_tuple=static_os_tuple,
        strategy=long_strat,
        threads=int(sys.argv[1]),
    )

    backtest_results.to_hdf("backtest_results.h5", key="backtest_results", mode="w")
    
    end = perf_counter()
    print(f"Main took: ", end - start)
