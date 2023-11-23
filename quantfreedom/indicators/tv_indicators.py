from typing import Callable
import numpy as np


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


def sma_tv(
    source: np.array,
    length: int,
):
    """
    Simple Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma
    """
    sma = np.full_like(source, np.nan)
    len_minus_one = source[np.isnan(source)].size + length - 1

    for i in range(len_minus_one, source.size):
        sma[i] = source[i - len_minus_one : i + 1].mean()

    return sma


def ema_tv(
    source: np.array,
    length: int,
):
    """
    Exponential Moving average https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema
    """
    alpha = 2 / (length + 1)

    starting_index = source[np.isnan(source)].size + length

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

    new_length = source.size - source[~np.isnan(source)].size + length

    rma = np.full_like(source, np.nan)
    rma[new_length - 1] = source[new_length - length : new_length].mean()

    for i in range(new_length, source.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

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

    new_length = source_1.size - source_1[~np.isnan(source_1)].size + length

    rma_1 = np.full_like(source_1, np.nan)
    rma_2 = np.full_like(rma_1, np.nan)

    rma_1[new_length - 1] = source_1[new_length - length : new_length].mean()
    rma_2[new_length - 1] = source_2[new_length - length : new_length].mean()

    for i in range(new_length, source_1.size):
        rma_1[i] = alpha * source_1[i] + (1 - alpha) * rma_1[i - 1]
        rma_2[i] = alpha * source_2[i] + (1 - alpha) * rma_2[i - 1]

    return rma_1, rma_2


def stdev_tv(
    source: np.array,
    length: int,
):
    """
    Standard deviation https://www.tradingview.com/pine-script-reference/v5/#fun_ta.stdev
    """
    avg = -sma_tv(source=source, length=length)

    sum_square_dev = np.full_like(avg, np.nan)

    len_minus_one = length - 1

    for i in range(avg.size - 1, len_minus_one, -1):
        res = np.absolute(source[i - len_minus_one : i + 1] + avg[i])
        res_2 = np.where(
            res <= 1e-10,
            0,
            np.where(
                (res <= 1e-4) & (res > 1e-10),
                1e-5,
                res,
            ),
        )
        sum_square_dev[i] = (res_2 * res_2).sum()

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
    return basis, upper, lower


def true_range_tv(candles: np.array):
    """
    https://www.tradingview.com/pine-script-reference/v5/#fun_ta.tr
    """
    high = candles[:, 2]
    low = candles[:, 3]
    prev_close = np.roll(candles[:, 4], 1)
    prev_close[0] = np.nan
    true_range = np.maximum(
        np.maximum(
            high - low,
            np.absolute(high - prev_close),
        ),
        np.absolute(low - prev_close),
    )
    return true_range


def atr_tv(
    candles: np.array,
    length: int,
    smoothing_type: Callable = rma_tv,
):
    """
    Average true range smoothing https://www.tradingview.com/pine-script-reference/v5/#fun_ta.atr
    """
    true_range = true_range_tv(candles=candles)
    atr = smoothing_type(source=true_range, length=length)
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
    return super_trend, direction


def vwap_tv(
    candles: np.array,
):
    """
    https://blog.quantinsti.com/vwap-strategy/
    """
    timestamps = candles[:, 0]
    high = candles[:, 2]
    low = candles[:, 3]
    close = candles[:, 4]
    volume = candles[:, 5]

    typical_price = (high + low + close) / 3
    tp_x_vol = typical_price * volume

    day_in_ms = 86400000
    nan_array = np.where(timestamps % day_in_ms == 0, np.nan, 0)

    nan_indexes = np.isnan(nan_array).nonzero()[0]  # returns tuple for some reason
    cum_vol = np.full_like(close, np.nan)
    cum_tp = np.full_like(close, np.nan)

    try:
        cum_vol[: nan_indexes[0]] = volume[: nan_indexes[0]].cumsum()
        cum_tp[: nan_indexes[0]] = tp_x_vol[: nan_indexes[0]].cumsum()

        for i in range(nan_indexes.size - 1):
            cum_vol[nan_indexes[i] : nan_indexes[i + 1]] = volume[nan_indexes[i] : nan_indexes[i + 1]].cumsum()
            cum_tp[nan_indexes[i] : nan_indexes[i + 1]] = tp_x_vol[nan_indexes[i] : nan_indexes[i + 1]].cumsum()

        cum_vol[nan_indexes[-1] :] = volume[nan_indexes[-1] :].cumsum()
        cum_tp[nan_indexes[-1] :] = tp_x_vol[nan_indexes[-1] :].cumsum()
    except Exception:
        raise Exception("You need to have enough data to where you have at least one start of the day")

    vwap = cum_tp / cum_vol
    return vwap


def squeeze_momentum_lazybear_tv(
    candles: np.array,
    length_bb: int,
    length_kc: int,
    multi_bb: int,
    multi_kc: int,
):
    """
    Returns = sqz_hist, sqz_on, no_sqz

    https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/
    """
    high = candles[:, 2]
    low = candles[:, 3]
    close = candles[:, 4]

    s_min_ma_hl = np.full_like(close, np.nan)
    sqz_hist = np.full_like(close, np.nan)

    x = np.arange(0, length_kc)
    A = np.vstack([x, np.ones(len(x))]).T

    _, upper_bb, lower_bb = bb_tv(
        source=close,
        length=length_bb,
        multi=multi_bb,
    )

    true_range_ma = sma_tv(
        true_range_tv(candles=candles),
        length=length_kc,
    )

    ma = sma_tv(close, length=length_kc)

    upper_kc = ma + true_range_ma * multi_kc
    lower_kc = ma - true_range_ma * multi_kc
    sqz_on = np.where((lower_bb > lower_kc) & (upper_bb < upper_kc), True, False)
    no_sqz = np.where((lower_bb == lower_kc) & (upper_bb == upper_kc), True, False)

    length_kc_m_1 = length_kc - 1
    for i in range(length_kc_m_1, close.size):
        highest = high[i - length_kc_m_1 : i + 1].max()
        lowest = low[i - length_kc_m_1 : i + 1].min()
        hl_avg = (highest + lowest) / 2
        ma_hl_avg = (hl_avg + ma[i]) / 2
        s_min_ma_hl[i] = close[i] - ma_hl_avg
        m, b = np.linalg.lstsq(A, s_min_ma_hl[i - length_kc_m_1 : i + 1], rcond=None)[0]
        sqz_hist[i] = b + m * (length_kc_m_1)
    return sqz_hist, sqz_on, no_sqz
