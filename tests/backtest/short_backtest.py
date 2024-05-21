import pickle
from os import remove
from os.path import exists
from time import perf_counter
from time import gmtime, strftime
from quantfreedom.backtesters import run_df_backtest
from rsi_rising_falling import rsi_rising_falling_short_strat


if __name__ == "__main__":
    start = perf_counter()
    h5_path = "dbs/btr_short.h5"
    if exists(h5_path):
        remove(h5_path)

    print("loading candles")
    candle_path = "dbs/apr22_june22_bybit_candles.pkl"
    with open(candle_path, "rb") as f:
        apr22_june22_bybit_candles = pickle.load(f)

    backtest_results = run_df_backtest(
        candles=apr22_june22_bybit_candles,
        strategy=rsi_rising_falling_short_strat,
        threads=32,
        step_by=6,
    )
    print("\n" + "Backtest results done now saving to hdf5")
    backtest_results.to_hdf(
        h5_path,
        key="backtest_results",
        mode="w",
    )

    end = perf_counter()
    print(strftime("\n" + "It took %M mins and %S seconds to complete the backtest", gmtime(int(end - start))))
