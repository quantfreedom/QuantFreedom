import time
from multiprocessing import Pool, cpu_count, Lock
import numpy as np


def backtesting(
    record_results: np.array,
    range_start: int,
    range_end: int,
) -> np.array:
    # print("inside backteesting")
    candles = 3000
    time.sleep(10)
    for i in range(range_end - range_start):  # looping settings
        backtest_result = False
        if np.random.randint(0, 50) < 25:
            backtest_result = True
        for candle in range(candles):
            # print(f"Setting: {i} Candle: {candle}")
            # backtest settings i
            if backtest_result:
                record_results[i, 0] = i + range_start
                record_results[i, 1:] = np.random.randint(5, size=4)
    return record_results, range_start, range_end


def proc_results(results):
    # print("Results: ", results)
    begin = results[1]
    length = results[2] - results[1]
    for i in range(length):
        whole_array[begin + i] = results[0][i - length]


# error callback function
def handler(error):
    print(f"Error: {error}", flush=True)


def main(
    record_results: np.array,
):
    print("start main")
    start = time.perf_counter()

    p = Pool()
    threads = cpu_count()
    total_settings = record_results.shape[0]
    range_multiplier = total_settings / threads
    results = []

    for x in range(threads):
        range_start = int(x * range_multiplier)
        range_end = int((x + 1) * range_multiplier)

        r = p.apply_async(
            func=backtesting,
            args=[record_results[range_start:range_end], range_start, range_end],
            callback=proc_results,
            error_callback=handler,
        )
        results.append(r)

    for r in results:
        r.wait()

    p.close()
    p.join()
    end = time.perf_counter()
    return results


if __name__ == "__main__":
    global whole_array

    start = time.perf_counter()

    total_settings = 20051
    record_results = np.zeros((total_settings, 5)).astype(np.int_)
    whole_array = record_results.copy()

    results = main(record_results=record_results)

    end = time.perf_counter()
    print(f"Entire Process took: ", end - start)
    # print(whole_array)