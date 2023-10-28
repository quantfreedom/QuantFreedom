import numpy as np


def qf_calc_rsi(prices: np.array, period: int):
    prices_shift = np.roll(prices, 1)
    prices_shift[0] = np.nan
    pchg = (prices - prices_shift) / prices_shift

    alpha = 1 / period
    gain = np.where(pchg > 0, pchg, 0)
    avg_gain = np.full_like(gain, np.nan)

    loss = np.where(pchg < 0, abs(pchg), 0)
    avg_loss = np.full_like(loss, np.nan)

    avg_gain[period] = gain[1 : period + 1].mean()
    avg_loss[period] = loss[1 : period + 1].mean()

    for i in range(period + 1, gain.size):
        avg_gain[i] = alpha * gain[i] + (1 - alpha) * avg_gain[i - 1]
        avg_loss[i] = alpha * loss[i] + (1 - alpha) * avg_loss[i - 1]

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return rsi
