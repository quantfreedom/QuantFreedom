import numpy as np


def qf_calc_rsi(prices: np.array, period: int):
    prices_shift = np.roll(prices, 1)
    prices_shift[0] = np.nan
    pchgs = (prices - prices_shift) / prices_shift

    alpha = 1 / period
    gains = np.where(pchgs > 0, pchgs, 0)
    rma_gains = np.full_like(gains, np.nan)

    losses = np.where(pchgs < 0, abs(pchgs), 0)
    rma_losses = np.full_like(losses, np.nan)

    rma_gains[period] = gains[1 : period + 1].mean()
    rma_losses[period] = losses[1 : period + 1].mean()

    for i in range(period + 1, gains.size):
        rma_gains[i] = alpha * gains[i] + (1 - alpha) * rma_gains[i - 1]
        rma_losses[i] = alpha * losses[i] + (1 - alpha) * rma_losses[i - 1]

    rs = rma_gains / rma_losses

    rsi = 100 - (100 / (1 + rs))
    return rsi
