import numpy as np


def sma_tv_calc(
    source: np.array,
    length: int,
):
    """
    Simple moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma
    """
    arr = np.cumsum(source, dtype=np.float_)
    arr[length:] = arr[length:] - arr[:-length]

    sma = np.full_like(source, np.nan)
    sma[length - 1 :] = arr[length - 1 :] / length

    return sma


def ema_tv_calc(
    source: np.array,
    length: int,
):
    """
    Exponential moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema
    """
    alpha = 2 / (length + 1)

    ema = np.full_like(source, np.nan)
    ema[length] = source[length]

    for i in range(length + 1, ema.size):
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

    rma = np.full_like(source, np.nan)
    rma[length - 1] = source[:length].mean()

    for i in range(length, rma.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def rma_tv_calc_2(source_1: np.array, source_2: np.array, length: int):
    """
    Relative strength index moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    """
    alpha = 1 / length

    rma_1 = np.full_like(source_1, np.nan)
    rma_2 = np.full_like(source_2, np.nan)

    rma_1[length - 1] = source_1[:length].mean()
    rma_2[length - 1] = source_2[:length].mean()

    for i in range(length, rma_1.size):
        rma_1[i] = alpha * source_1[i] + (1 - alpha) * rma_1[i - 1]
        rma_2[i] = alpha * source_2[i] + (1 - alpha) * rma_2[i - 1]

    return rma_1, rma_2


def wma_tv_calc(
    source: np.array,
    length: int,
):
    weight = np.flip((length - np.arange(0, length)) * length)
    norm = weight.sum()
    wma = np.full_like(source, np.nan)

    looper = length - 1
    for i in range(looper, source.size):
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
    avg = sma_tv_calc(source=source, length=length)

    sum_square_dev = np.full_like(avg, np.nan)

    looper = length - 1

    for i in range(avg.size - 1, looper, -1):
        res = source[i - looper : i + 1] + -avg[i]
        res_2 = np.where(np.absolute(res) <= 1e-10, 0, res)
        sum = np.where((np.absolute(res_2) < 1e-4) & (np.absolute(res_2) > 1e-10), 1e-5, res_2)
        sum_square_dev[i] = (sum * sum).sum()

    final = np.sqrt(sum_square_dev / length)
    return final


def macd_tv_calc(
    source: np.array,
    fast_length: int,
    slow_length: int,
    signal_smoothing: int,
    oscillator_type=ema_tv_calc,
    signal_ma_type=ema_tv_calc,
):
    """
    Moving average convergence divergence https://www.tradingview.com/pine-script-reference/v5/#fun_ta.macd
    """
    fast_ma = oscillator_type(source=source, length=fast_length)
    slow_ma = oscillator_type(source=source, length=slow_length)
    macd = fast_ma - slow_ma
    signal = signal_ma_type(source=source, length=signal_smoothing)
    histogram = macd - signal
    return macd, signal, histogram


def bb_tv_calc(
    source: np.array,
    length: int,
    multi: float,
    basis_ma_type=sma_tv_calc,
):
    """
    returns upper - basis - lower
    Bollinger bands https://www.tradingview.com/pine-script-reference/v5/#fun_ta.bb
    """
    basis = basis_ma_type(source=source, length=length)
    dev = multi * stdev_tv_calc(source=source, length=length)
    upper = basis + dev
    lower = basis - dev
    bb = np.array([upper, basis, lower]).T
    return bb


def atr_tv_calc(
    candles: np.array,
    length: int,
    smoothing_type=rma_tv_calc,
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
