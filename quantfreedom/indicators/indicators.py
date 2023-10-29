import numpy as np


def atr_calc(candles: np.array, length: int):
    """
    ATR with rma smoothing
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
    atr = rma_calc(source=tr, length=length)
    return atr


def rsi_calc(source: np.array, length: int):
    prices_shift = np.roll(source, 1)
    prices_shift[0] = np.nan
    pchgs = (source - prices_shift) / prices_shift

    gains = np.where(pchgs > 0, pchgs, 0)
    losses = np.where(pchgs < 0, -(pchgs), 0)

    rma_gains, rma_losses = rma_calc_2(length=length, source_1=gains, source_2=losses)

    rs = rma_gains / rma_losses

    rsi = 100 - (100 / (1 + rs))
    return rsi


def ema_calc(source: np.array, length: int):
    alpha = 2 / (length + 1)

    ema = np.full_like(source, np.nan)
    ema[length] = source[length]

    for i in range(length + 1, ema.size):
        ema[i] = alpha * source[i] + (1 - alpha) * ema[i - 1]

    return ema


def sma_calc(source: np.array, length: int):
    arr = np.cumsum(source, dtype=np.float_)
    arr[length:] = arr[length:] - arr[:-length]

    sma = np.full_like(source, np.nan)
    sma[length - 1 :] = arr[length - 1 :] / length

    return sma


def rma_calc(source: np.array, length: int):
    alpha = 1 / length

    rma = np.full_like(source, np.nan)
    rma[length - 1] = source[:length].mean()

    for i in range(length, rma.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def rma_calc_2(source_1: np.array, source_2: np.array, length: int):
    alpha = 1 / length

    rma_1 = np.full_like(source_1, np.nan)
    rma_2 = np.full_like(source_2, np.nan)

    rma_1[length - 1] = source_1[:length].mean()
    rma_2[length - 1] = source_2[:length].mean()

    for i in range(length, rma_1.size):
        rma_1[i] = alpha * source_1[i] + (1 - alpha) * rma_1[i - 1]
        rma_2[i] = alpha * source_2[i] + (1 - alpha) * rma_2[i - 1]

    return rma_1, rma_2
