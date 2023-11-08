import numpy as np


def bb_sma_tv_calc(source: np.array, length: int, multi: float):
    """
    Bollinger Bands sma smoothing https://www.tradingview.com/pine-script-reference/v5/#fun_ta.bb
    """
    basis = sma_tv_calc(source=source, length=length)
    dev = multi * stdev_tv_calc(source=source, length=length)
    upper = basis + dev
    lower = basis - dev
    bb = np.array([upper, basis, lower]).T
    return bb


def atr_rma_tv_calc(candles: np.array, length: int):
    """
    ATR with rma smoothing https://www.tradingview.com/pine-script-reference/v5/#fun_ta.atr
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
    atr = rma_tv_calc(source=tr, length=length)
    return atr


def rsi_rma_tv_calc(source: np.array, length: int):
    """
    RSI with rma smoothing https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rsi
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


def ema_tv_calc(source: np.array, length: int):
    """
    EMA https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema
    """
    alpha = 2 / (length + 1)

    ema = np.full_like(source, np.nan)
    ema[length] = source[length]

    for i in range(length + 1, ema.size):
        ema[i] = alpha * source[i] + (1 - alpha) * ema[i - 1]

    return ema


def sma_tv_calc(source: np.array, length: int):
    """
    SMA https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma
    """
    arr = np.cumsum(source, dtype=np.float_)
    arr[length:] = arr[length:] - arr[:-length]

    sma = np.full_like(source, np.nan)
    sma[length - 1 :] = arr[length - 1 :] / length

    return sma


def rma_tv_calc(source: np.array, length: int):
    """
    RMA https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    """
    alpha = 1 / length

    rma = np.full_like(source, np.nan)
    rma[length - 1] = source[:length].mean()

    for i in range(length, rma.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def rma_tv_calc_2(source_1: np.array, source_2: np.array, length: int):
    """
    RMA https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
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


def stdev_tv_calc(source, length):
    """
    standard dev https://www.tradingview.com/pine-script-reference/v5/#fun_ta.stdev
    """
    avg = sma_tv_calc(source=source, length=length)

    sum_square_dev = np.full_like(avg, np.nan)

    looper = length - 1

    for i in range(looper, avg.size):
        res = source[i - looper : i + 1] + -avg[i]
        res_2 = np.where(np.absolute(res) <= 1e-10, 0, res)
        sum = np.where((np.absolute(res_2) < 1e-4) & (np.absolute(res_2) > 1e-10), 1e-5, res_2)
        sum_square_dev[i] = (sum * sum).sum()

    final = np.sqrt(sum_square_dev / length)
    return final
