import pickle
from os import remove
from os.path import exists
from time import perf_counter
from time import gmtime, strftime
from quantfreedom.backtesters.bt_regular import run_df_backtest
from strat import long_strat


if __name__ == "__main__":
    start = perf_counter()
    if exists("backtest_results.h5"):
        remove("backtest_results.h5")

    print("loading candles")
    with open("candles.pkl", "rb") as f:
        candles = pickle.load(f)

    backtest_results = run_df_backtest(
        candles=candles,
        step_by=2,
        strategy=long_strat,
        threads=32,
        num_chunk_bts=2000000,
    )
    print("\n" + "Backtest results done now saving to hdf5")
    backtest_results.to_hdf(
        "backtest_results.h5",
        key="backtest_results",
        mode="w",
    )

    end = perf_counter()
    print(strftime("\n" + "It took %M mins and %S seconds to complete the backtest", gmtime(int(end - start))))
