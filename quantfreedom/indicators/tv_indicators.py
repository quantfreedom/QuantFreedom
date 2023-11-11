from typing import Callable
import numpy as np


def sma_tv_calc(
    source: np.array,
    length: int,
):
    """
    Simple moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma
    """
    len_adder = source.size - new_source.size
    new_source = source[~np.isnan(source)]

    arr = np.cumsum(new_source, dtype=np.float_)
    arr[length:] = (arr[length:] - arr[:-length]) / length

    sma = np.full_like(source, np.nan)
    sma[len_adder + length :] = arr[length:]

    return sma


def ema_tv_calc(
    source: np.array,
    length: int,
):
    """
    Exponential moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema
    """
    alpha = 2 / (length + 1)

    arr = source[~np.isnan(source)]
    len_adder = max(source.size - arr.size, length)

    ema = np.full_like(source, np.nan)
    ema[len_adder] = source[len_adder]

    for i in range(len_adder + 1, ema.size):
        ema[i] = alpha * source[i] + (1 - alpha) * ema[i - 1]

    return ema


def rma_tv_calc(
    source: np.array,
    length: int,
):
    """
    Relative strength index Moving Average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    """
    alpha = 1 / length

    arr = source[~np.isnan(source)]
    len_adder = max(source.size - arr.size, length)

    rma = np.full_like(source, np.nan)
    rma[len_adder] = sma_tv_calc(source=source, length=len_adder)[len_adder]

    for i in range(len_adder + 1, rma.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def rma_tv_calc_2(source_1: np.array, source_2: np.array, length: int):
    """
    Relative strength index moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    """
    alpha = 1 / length

    arr = source_1[~np.isnan(source_1)]
    len_adder = max(source_1.size - arr.size, length)

    rma_1 = np.full_like(source_1, np.nan)
    rma_2 = np.full_like(source_2, np.nan)

    rma_1[len_adder] = sma_tv_calc(source=source_1, length=len_adder)[len_adder]
    rma_2[len_adder] = sma_tv_calc(source=source_2, length=len_adder)[len_adder]

    for i in range(len_adder + 1, rma_1.size):
        rma_1[i] = alpha * source_1[i] + (1 - alpha) * rma_1[i - 1]
        rma_2[i] = alpha * source_2[i] + (1 - alpha) * rma_2[i - 1]

    return rma_1, rma_2


def wma_tv_calc(
    source: np.array,
    length: int,
):
    arr = source[~np.isnan(source)]
    len_adder = max(source.size - arr.size, length)

    weight = np.flip((length - np.arange(0, length)) * length)
    norm = weight.sum()
    wma = np.full_like(source, np.nan)

    looper = len_adder - 1
    for i in range(len_adder - 1, source.size):
        the_sum = (source[i - looper : i + 1] * weight).sum()
        wma[i] = the_sum / norm
    return wma


def stdev_tv_calc(
    source: np.array,
    length: np.array,
):
    """
    Standard deviation https://www.tradingview.com/pine-script-reference/v5/#fun_ta.stdev
    """
    arr = source[~np.isnan(source)]
    len_adder = max(source.size - arr.size, length)

    avg = sma_tv_calc(source=source, length=len_adder)

    sum_square_dev = np.full_like(avg, np.nan)
    looper = len_adder - 1
    for i in range(avg.size - 1, looper, -1):
        res = source[i - looper : i + 1] + -avg[i]
        res_2 = np.where(np.absolute(res) <= 1e-10, 0, res)
        sum = np.where((np.absolute(res_2) < 1e-4) & (np.absolute(res_2) > 1e-10), 1e-5, res_2)
        sum_square_dev[i] = (sum * sum).sum()

    final = np.sqrt(sum_square_dev / len_adder)
    return final


def macd_tv_calc(
    source: np.array,
    fast_length: int = 12,
    slow_length: int = 26,
    signal_smoothing: int = 9,
    oscillator_type: Callable = ema_tv_calc,
    signal_ma_type: Callable = ema_tv_calc,
):
    """
    return order = histogram, macd, signal
    Moving average convergence divergence https://www.tradingview.com/pine-script-reference/v5/#fun_ta.macd
    """
    fast_ma = oscillator_type(source=source, length=fast_length)
    slow_ma = oscillator_type(source=source, length=slow_length)
    macd = fast_ma - slow_ma
    signal = signal_ma_type(source=macd, length=signal_smoothing)
    histogram = macd - signal
    final_macd = np.array([histogram, macd, signal]).T
    return final_macd


def bb_tv_calc(
    source: np.array,
    length: int,
    multi: float,
    basis_ma_type: Callable = sma_tv_calc,
):
    """
    returns basis, upper, lower
    Bollinger bands https://www.tradingview.com/pine-script-reference/v5/#fun_ta.bb
    """
    basis = basis_ma_type(source=source, length=length)
    dev = multi * stdev_tv_calc(source=source, length=length)
    upper = basis + dev
    lower = basis - dev
    bb = np.array([basis, upper, lower]).T
    return bb


def atr_tv_calc(
    candles: np.array,
    length: int,
    smoothing_type: Callable = rma_tv_calc,
):
    """
    Average true range smoothing https://www.tradingview.com/pine-script-reference/v5/#fun_ta.atr
    """
    high = candles[:, 2]
    low = candles[:, 3]
    close_shift = np.roll(candles[:, 4], 1)
    tr = np.maximum(
        np.maximum(
            high - low,
            np.absolute(high - close_shift),
        ),
        np.absolute(low - close_shift),
    )
    atr = smoothing_type(source=tr, length=length)
    return atr


def rsi_tv_calc(
    source: np.array,
    length: int,
):
    """
    Relative strength index https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rsi
    """
    prices_shift = np.roll(source, 1)
    prices_shift[0] = np.nan
    pchgs = (source - prices_shift) / prices_shift

    gains = np.where(pchgs > 0, pchgs, 0)
    losses = np.where(pchgs < 0, -(pchgs), 0)

    rma_gains, rma_losses = rma_tv_calc_2(length=length, source_1=gains, source_2=losses)

    rs = rma_gains / rma_losses

    rsi = 100 - (100 / (1 + rs))
    return rsi
