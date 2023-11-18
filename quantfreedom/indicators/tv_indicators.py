from typing import Callable
import numpy as np


def sma_tv(
    source: np.array,
    length: int,
):
    """
    Simple Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma
    """
    new_source = source[~np.isnan(source)]

    sma = np.full_like(source, np.nan)

    len_adder = source.size - new_source.size
    len_minus_one = length - 1

    for i in range(len_minus_one, new_source.size):
        sma[i + len_adder] = new_source[i - len_minus_one : i + 1].mean()

    return sma


def wma_tv(
    source: np.array,
    length: int,
):
    """
    Weighted Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.wma
    """
    weight = np.flip((length - np.arange(0, length)) * length)
    norm = weight.sum()

    wma = np.full_like(source, np.nan)
    len_minus_one = length - 1

    for index in range(len_minus_one, source.size):
        the_sum = (source[index - len_minus_one : index + 1] * weight).sum()
        wma[index] = the_sum / norm
    return wma


def ema_tv(
    source: np.array,
    length: int,
):
    """
    Exponential Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema
    """
    alpha = 2 / (length + 1)

    len_adder = source.size - source[~np.isnan(source)].size
    starting_index = len_adder + length

    ema = np.full_like(source, np.nan)
    ema[starting_index - 1] = source[starting_index - 1]

    for index in range(starting_index, source.size):
        ema[index] = alpha * source[index] + (1 - alpha) * ema[index - 1]

    return ema


def rma_tv(
    source: np.array,
    length: int,
):
    """
    Relative strength index Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
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


def rma_tv_2(
    source_1: np.array,
    source_2: np.array,
    length: int,
):
    """
    Relative strength index Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
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


def stdev_tv(
    source: np.array,
    length: int,
):
    """
    Standard deviation https://www.tradingview.com/pine-script-reference/v5/#fun_ta.stdev
    """
    avg = sma_tv(source=source, length=length)

    sum_square_dev = np.full_like(avg, np.nan)

    len_minus_one = length - 1

    for i in range(avg.size - 1, len_minus_one, -1):
        res = source[i - len_minus_one : i + 1] + -avg[i]
        res_2 = np.where(np.absolute(res) <= 1e-10, 0, res)
        sum = np.where((np.absolute(res_2) < 1e-4) & (np.absolute(res_2) > 1e-10), 1e-5, res_2)
        sum_square_dev[i] = (sum * sum).sum()

    final = np.sqrt(sum_square_dev / length)
    return final


def macd_tv(
    source: np.array,
    fast_length: int,
    slow_length: int,
    signal_smoothing: int,
    oscillator_type: Callable = ema_tv,
    signal_ma_type: Callable = ema_tv,
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


def bb_tv(
    source: np.array,
    length: int,
    multi: float,
    basis_ma_type: Callable = sma_tv,
):
    """
    returns basis, upper, lower
    Bollinger bands https://www.tradingview.com/pine-script-reference/v5/#fun_ta.bb
    """
    basis = basis_ma_type(source=source, length=length)
    dev = multi * stdev_tv(source=source, length=length)
    upper = basis + dev
    lower = basis - dev
    bb = np.array([basis, upper, lower]).T
    return bb


def atr_tv(
    candles: np.array,
    length: int,
    smoothing_type: Callable = rma_tv,
):
    """
    Average true range smoothing https://www.tradingview.com/pine-script-reference/v5/#fun_ta.atr
    """
    high = candles[:, 2]
    low = candles[:, 3]
    prev_close = np.roll(candles[:, 4], 1)
    prev_close[0] = np.nan
    tr = np.maximum(
        np.maximum(
            high - low,
            np.absolute(high - prev_close),
        ),
        np.absolute(low - prev_close),
    )
    atr = smoothing_type(source=tr, length=length)
    return atr


def rsi_tv(
    source: np.array,
    length: int,
):
    """
    Relative strength index https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rsi
    """
    prices_shift = np.roll(source, 1)
    prices_shift[0] = np.nan
    change = source - prices_shift

    gains = np.where(change > 0, change, 0)
    losses = np.where(change < 0, -(change), 0)
    gains[0] = np.nan
    losses[0] = np.nan

    rma_gains, rma_losses = rma_tv_2(
        source_1=gains,
        source_2=losses,
        length=length,
    )

    rs = rma_gains / rma_losses

    rsi = 100 - (100 / (1 + rs))
    return rsi


def supertrend_tv(
    candles: np.array,
    atr_length: int,
    factor: int,
):
    """
    return super trend, direction
    Super Trend https://www.tradingview.com/pine-script-reference/v5/#fun_ta.supertrend
    """
    atr = atr_tv(candles=candles, length=atr_length)
    source = (candles[:, 2] + candles[:, 3]) / 2
    close = candles[:, 4]
    super_trend = np.full_like(close, np.nan)
    direction = np.full_like(close, np.nan)

    upper_band = source[atr_length] + factor * atr[atr_length]
    lower_band = source[atr_length] - factor * atr[atr_length]
    super_trend[atr_length] = upper_band
    direction[atr_length] = 1

    for i in range(atr_length + 1, candles.shape[0]):
        current_source = source[i]
        current_atr = atr[i]
        current_close = close[i]

        prev_close = close[i - 1]

        # Lower band
        prev_lower_band = lower_band
        lower_band = current_source - factor * current_atr

        if lower_band <= prev_lower_band and prev_close >= prev_lower_band:
            lower_band = prev_lower_band

        # Upper Band
        prev_upper_band = upper_band
        upper_band = current_source + factor * current_atr

        if upper_band >= prev_upper_band and prev_close <= prev_upper_band:
            upper_band = prev_upper_band

        direction[i] = -1
        super_trend[i] = lower_band

        if super_trend[i - 1] == prev_upper_band:
            if current_close <= upper_band:
                direction[i] = 1
                super_trend[i] = upper_band
        else:
            if current_close < lower_band:
                direction[i] = 1
                super_trend[i] = upper_band
    final = np.array([super_trend, direction]).T
    return final
