import numpy as np


def qf_calc_rsi(
    prices: np.array,
    period: int,
):
    prices_length = prices.size
    up = np.zeros(prices_length)
    down = np.zeros(prices_length)
    mean_up = np.zeros(prices_length)
    mean_down = np.zeros(prices_length)
    rsi = np.full(prices_length, np.nan)
    alpha = 1/period
    for idx in range(1, period):
        rma = alpha * prices[idx] + (1 - alpha) * prices[idx - 1]
        pchg = (rma - prices[idx - 1]) / prices[idx - 1]
        if pchg > 0:
            up[idx] = pchg
        else:
            down[idx] = abs(pchg)
    
    
    for idx in range(period, prices_length):
        rma = (1 / period) * prices[idx] + (1 - (1 / period)) * prices[idx - 1]
        pchg = (rma - prices[idx - 1]) / prices[idx - 1]
        if pchg > 0:
            up[idx] = pchg
        else:
            down[idx] = abs(pchg)
        mean_up[idx] = np.mean(up[idx - period+1 : idx + 1])
        mean_down[idx] = np.mean(down[idx - period+1 : idx + 1])
        rsi[idx] = 100 - 100 / (1 + mean_up[idx] / mean_down[idx])

    return rsi
