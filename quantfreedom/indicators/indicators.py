import numpy as np


def rsi_calc(source: np.array, length: int):
    prices_shift = np.roll(source, 1)
    prices_shift[0] = np.nan
    pchgs = (source - prices_shift) / prices_shift

    gains = np.where(pchgs > 0, pchgs, 0)
    rma_gains = np.full_like(gains, np.nan)

    losses = np.where(pchgs < 0, abs(pchgs), 0)
    rma_losses = np.full_like(losses, np.nan)

    rma_gains[length] = gains[1 : length + 1].mean()
    rma_losses[length] = losses[1 : length + 1].mean()

    rma_gains, rma_losses = rma_calc_2(
        length=length,
        s_1=gains,
        rma_1=rma_gains,
        s_2=losses,
        rma_2=rma_losses,
    )

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

    final = arr[length - 1 :] / length

    return final


def rma_calc_1(
    length: int,
    source: np.array,
    rma: np.array,
):
    alpha = 1 / length
    for i in range(length + 1, rma.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def rma_calc_2(
    length: int,
    s_1: np.array,
    s_2: np.array,
    rma_1: np.array,
    rma_2: np.array,
):
    alpha = 1 / length
    for i in range(length + 1, rma_1.size):
        rma_1[i] = alpha * s_1[i] + (1 - alpha) * rma_1[i - 1]
        rma_2[i] = alpha * s_2[i] + (1 - alpha) * rma_2[i - 1]

    return rma_1, rma_2
