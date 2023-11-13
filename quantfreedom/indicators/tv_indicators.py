from typing import Callable
import numpy as np


def sma_tv_calc(
    source: np.array,
    length: int,
):
    """
    Simple moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma
    """
    new_source = source[~np.isnan(source)]

    sma = np.full_like(source, np.nan)

    len_adder = source.size - new_source.size
    len_minus_one = length - 1

    for i in range(len_minus_one, new_source.size):
        sma[i + len_adder] = new_source[i - len_minus_one : i + 1].mean()

    return sma


def wma_tv_calc(
    source: np.array,
    length: int,
):
    """
    https://www.tradingview.com/pine-script-reference/v5/#fun_ta.wma
    """
    new_source = source[~np.isnan(source)]

    weight = np.flip((length - np.arange(0, length)) * length)
    norm = weight.sum()

    wma = np.full_like(source, np.nan)

    len_adder = source.size - new_source.size
    len_minus_one = length - 1

    for i in range(len_minus_one, new_source.size):
        the_sum = (new_source[i - len_minus_one : i + 1] * weight).sum()
        wma[i + len_adder] = the_sum / norm
    return wma


def ema_tv_calc(
    source: np.array,
    length: int,
):
    """
    Exponential moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema
    """
    alpha = 2 / (length + 1)

    new_source = source[~np.isnan(source)]
    len_adder = source.size - new_source.size

    len_minus_one = length - 1
    ema = np.full_like(source, np.nan)
    ema[len_minus_one + len_adder] = source[len_minus_one + len_adder]

    for i in range(length, new_source.size):
        index = len_adder + i
        ema[index] = alpha * new_source[i] + (1 - alpha) * ema[index - 1]

    return ema


def rma_tv_calc(
    source: np.array,
    length: int,
):
    """
    Relative strength index Moving Average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    """
    alpha = 1 / length

    new_source = source[~np.isnan(source)]
    len_adder = source.size - new_source.size

    len_minus_one = length - 1
    rma = np.full_like(source, np.nan)
    rma[len_minus_one + len_adder] = new_source[:length].mean()

    for i in range(length, new_source.size):
        index = len_adder + i
        rma[index] = alpha * new_source[i] + (1 - alpha) * rma[index - 1]

    return rma


def rma_tv_calc_2(source_1: np.array, source_2: np.array, length: int):
    """
    Relative strength index moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    """
    alpha = 1 / length

    new_source_1 = source_1[~np.isnan(source_1)]
    new_source_2 = source_2[~np.isnan(source_2)]

    len_adder = source_1.size - new_source_1.size
    len_minus_one = length - 1

    rma_1 = np.full_like(source_1, np.nan)
    rma_2 = np.full_like(source_2, np.nan)

    rma_1[len_minus_one + len_adder] = new_source_1[:length].mean()
    rma_2[len_minus_one + len_adder] = new_source_2[:length].mean()

    for i in range(length, new_source_1.size):
        index = len_adder + i
        rma_1[index] = alpha * new_source_1[i] + (1 - alpha) * rma_1[index - 1]
        rma_2[index] = alpha * new_source_2[i] + (1 - alpha) * rma_2[index - 1]

    return rma_1, rma_2


def stdev_tv_calc(
    source: np.array,
    length: np.array,
):
    """
    Standard deviation https://www.tradingview.com/pine-script-reference/v5/#fun_ta.stdev
    """
    avg = sma_tv_calc(source=source, length=length)

    sum_square_dev = np.full_like(avg, np.nan)

    len_minus_one = length - 1

    for i in range(avg.size - 1, len_minus_one, -1):
        res = source[i - len_minus_one : i + 1] + -avg[i]
        res_2 = np.where(np.absolute(res) <= 1e-10, 0, res)
        sum = np.where((np.absolute(res_2) < 1e-4) & (np.absolute(res_2) > 1e-10), 1e-5, res_2)
        sum_square_dev[i] = (sum * sum).sum()

    final = np.sqrt(sum_square_dev / length)
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
    gains[0] = np.nan
    losses[0] = np.nan

    rma_gains, rma_losses = rma_tv_calc_2(
        source_1=gains,
        source_2=losses,
        length=length,
    )

    rs = rma_gains / rma_losses

    rsi = 100 - (100 / (1 + rs))
    return rsi
