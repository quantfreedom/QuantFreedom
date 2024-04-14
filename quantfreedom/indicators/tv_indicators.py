from typing import Callable
import numpy as np

from quantfreedom.core.enums import CandleBodyType


def wma_tv(
    source: np.array,
    length: int,
) -> np.array:
    """
    [Weighted Moving Average From Tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.wma)

    [Explainer Video](https://youtu.be/eHlHoWC4W8k)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        wma
    """
    weight = np.flip((length - np.arange(0, length)) * length)
    norm = weight.sum()

    wma = np.full_like(source, np.nan)
    len_minus_one = length - 1
    starting_index = source[np.isnan(source)].size + len_minus_one

    for index in range(starting_index, source.size):
        the_sum = (source[index - len_minus_one : index + 1] * weight).sum()
        wma[index] = the_sum / norm
    return wma


def sma_tv(
    source: np.array,
    length: int,
) -> np.array:
    """
    [Simple Moving average from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        sma
    """
    sma = np.full_like(source, np.nan)
    len_minus_one = length - 1

    starting_index = source[np.isnan(source)].size + len_minus_one

    for i in range(starting_index, source.size):
        sma[i] = source[i - len_minus_one : i + 1].mean()

    return sma


def ema_tv(
    source: np.array,
    length: int,
) -> np.array:
    """
    [Exponential Moving average from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.ema)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        ema
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
) -> np.array:
    """
    [Relative strength index Moving average from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        rma
    """
    alpha = 1 / length

    starting_index = source[np.isnan(source)].size + length

    rma = np.full_like(source, np.nan)
    rma[starting_index - 1] = source[starting_index - length : starting_index].mean()

    for i in range(starting_index, source.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def rma_tv_2(
    source_1: np.array,
    source_2: np.array,
    length: int,
):
    """
    [Relative strength index Moving average from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma)

    Parameters
    ----------
    source_1 : np.array
        Values to process
    source_2 : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        rma_1, rma_2
    """
    alpha = 1 / length

    starting_index = source_1[np.isnan(source_1)].size + length

    rma_1 = np.full_like(source_1, np.nan)
    rma_2 = np.full_like(rma_1, np.nan)

    rma_1[starting_index - 1] = source_1[starting_index - length : starting_index].mean()
    rma_2[starting_index - 1] = source_2[starting_index - length : starting_index].mean()

    for i in range(starting_index, source_1.size):
        rma_1[i] = alpha * source_1[i] + (1 - alpha) * rma_1[i - 1]
        rma_2[i] = alpha * source_2[i] + (1 - alpha) * rma_2[i - 1]

    return rma_1, rma_2


def stdev_tv(
    source: np.array,
    length: int,
) -> np.array:
    """
    [Standard deviation from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.stdev)

    [Explainer Video](https://youtu.be/Hejf_bzLfL4)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        stdev
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

    stdev = np.sqrt(sum_square_dev / length)
    return stdev


def macd_tv(
    source: np.array,
    fast_length: int,
    slow_length: int,
    signal_smoothing: int,
    oscillator_type: Callable = ema_tv,
    signal_ma_type: Callable = ema_tv,
) -> tuple[np.array, np.array, np.array]:
    """
    [Moving average convergence divergence from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.macd)

    Parameters
    ----------
    source : np.array
        Values to process
    fast_length : int
        Number of bars
    slow_length : int
        Number of bars
    signal_smoothing : int
        Number of bars
    oscillator_type : Callable
        Function to process fast and slow ma
    signal_ma_type : Callable
        Function to process signal ma

    Returns
    -------
    np.array, np.array, np.array
        histogram, macd, signal
    """
    fast_ma = oscillator_type(source=source, length=fast_length)
    slow_ma = oscillator_type(source=source, length=slow_length)
    macd = fast_ma - slow_ma
    signal = signal_ma_type(source=macd, length=signal_smoothing)
    histogram = macd - signal
    return histogram, macd, signal


def bb_tv(
    length: int,
    multi: float,
    source: np.array,
    basis_ma_type: Callable = sma_tv,
) -> tuple[np.array, np.array, np.array]:
    """
    [Bollinger bands from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.bb)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars
    multi : float
        Standard deviation factor
    basis_ma_type : Callable
        Function to process basic ma

    Returns
    -------
    tuple[np.array, np.array, np.array]
        basis, upper, lower
    """
    basis = basis_ma_type(source=source, length=length)
    dev = multi * stdev_tv(source=source, length=length)
    upper = basis + dev
    lower = basis - dev
    return basis, upper, lower


def true_range_tv(
    candles: np.array,
) -> np.array:
    """
    [True Range from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.tr)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]

    Returns
    -------
    np.array
        true_range
    """
    high = candles[:, CandleBodyType.High]
    low = candles[:, CandleBodyType.Low]
    prev_close = np.roll(candles[:, CandleBodyType.Close], 1)
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
) -> np.array:
    """
    [Average true range smoothing from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.atr)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    length : int
        Number of bars
    smoothing_type : Callable
        function to process the smoothing of the atr

    Returns
    -------
    np.array
        atr
    """
    true_range = true_range_tv(candles=candles)
    atr = smoothing_type(source=true_range, length=length)
    return atr


def rsi_tv(
    length: int,
    source: np.array,
) -> np.array:
    """
    [Relative strength index](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rsi)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        rsi
    """
    prev_source = np.roll(source, 1)
    prev_source[0] = np.nan
    change = source - prev_source

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
) -> tuple[np.array, np.array]:
    """
    [Super Trend](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.supertrend)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    atr_length : int
        Number of bars
    factor : int
        The multiplier by which the ATR will get multiplied

    Returns
    -------
    tuple[np.array, np.array]
        super_trend, direction
    """
    atr = atr_tv(candles=candles, length=atr_length)
    source = (candles[:, CandleBodyType.High] + candles[:, CandleBodyType.Low]) / 2
    close = candles[:, CandleBodyType.Close]
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
) -> np.array:
    """
    [Volume Weighted Average Price](https://blog.quantinsti.com/vwap-strategy/)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]

    Returns
    -------
    np.array
        vwap
    """
    timestamps = candles[:, CandleBodyType.Timestamp]
    high = candles[:, CandleBodyType.High]
    low = candles[:, CandleBodyType.Low]
    close = candles[:, CandleBodyType.Close]
    volume = candles[:, CandleBodyType.Volume]

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


def donchain_channels_tv(
    candles: np.array,
    length: int,
):
    """
    Donchain channels

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    length : int
        Number of bars of donchain lookback

    Returns
    -------
    tuple[np.array, np.array, np.array]
        upper, basis, lower
    """
    high_prices = candles[:, CandleBodyType.High]
    low_prices = candles[:, CandleBodyType.Low]

    length_m_1 = length - 1
    lower = np.full_like(low_prices, np.nan)
    upper = np.full_like(low_prices, np.nan)

    for i in range(length_m_1, low_prices.size):
        lower[i] = np.min(low_prices[i - length_m_1 : i + 1])
        upper[i] = np.max(high_prices[i - length_m_1 : i + 1])

    basis = np.mean(np.array([upper, lower]), axis=0)

    return upper, basis, lower


def squeeze_momentum_lazybear_tv(
    candles: np.array,
    length_bb: int,
    length_kc: int,
    multi_bb: int,
    multi_kc: int,
) -> tuple[np.array, np.array, np.array]:
    """
    [LazyBear Pinescript](https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    length_bb : int
        Number of bars of Bollinger Bands
    length_kc : int
        Number of bars of KC
    multi_bb : int
        The multiplier by which the Bollinger Bands will get multiplied
    multi_kc : int
        The multiplier by which the KC will get multiplied

    Returns
    -------
    tuple[np.array, np.array, np.array]
        squeeze historgram, squeeze on, no squeeze
    """
    high = candles[:, CandleBodyType.High]
    low = candles[:, CandleBodyType.Low]
    close = candles[:, CandleBodyType.Close]

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


def linear_regression_candles_ugurvu_tv(
    candles: np.array,
    lin_reg_length: int,
    smoothing_length: int,
    smoothing_type: Callable = sma_tv,
) -> tuple[np.array, np.array]:
    """
    [Linear regression indicator](https://www.tradingview.com/script/hMaQO1FX-Linear-Regression-Candles/)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    lin_reg_length : int
        Number of bars for lin reg
    smoothing_length : int
        Number of bars for singal line
    smoothing_type : Callable
        function to process the smoothing of the singal line

    Returns
    -------
    tuple[np.array, np.array]
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume], signal
    """
    open = candles[:, CandleBodyType.Open]
    high = candles[:, CandleBodyType.High]
    low = candles[:, CandleBodyType.Low]
    close = candles[:, CandleBodyType.Close]

    lin_reg_candles = np.full_like(candles, np.nan)

    x = np.arange(0, lin_reg_length)
    A = np.vstack([x, np.ones(len(x))]).T

    lin_reg_length_m_1 = lin_reg_length - 1

    for i in range(lin_reg_length_m_1, close.size):
        m, b = np.linalg.lstsq(A, open[i - lin_reg_length_m_1 : i + 1], rcond=None)[0]
        lin_reg_candles[i, CandleBodyType.Open] = b + m * (lin_reg_length_m_1)

        m, b = np.linalg.lstsq(A, high[i - lin_reg_length_m_1 : i + 1], rcond=None)[0]
        lin_reg_candles[i, CandleBodyType.High] = b + m * (lin_reg_length_m_1)

        m, b = np.linalg.lstsq(A, low[i - lin_reg_length_m_1 : i + 1], rcond=None)[0]
        lin_reg_candles[i, CandleBodyType.Low] = b + m * (lin_reg_length_m_1)

        m, b = np.linalg.lstsq(A, close[i - lin_reg_length_m_1 : i + 1], rcond=None)[0]
        lin_reg_candles[i, CandleBodyType.Close] = b + m * (lin_reg_length_m_1)

    signal = smoothing_type(
        source=lin_reg_candles[:, CandleBodyType.Close],
        length=smoothing_length,
    )

    lin_reg_candles[:, CandleBodyType.Timestamp] = candles[:, CandleBodyType.Timestamp]
    lin_reg_candles[:, CandleBodyType.Volume] = candles[:, CandleBodyType.Volume]

    return lin_reg_candles, signal


def revolution_volatility_bands_tv(
    length: int,
    source: np.array,
):
    basis = ema_tv(source=source, length=length)

    a = source - basis
    b = np.where(a < 0, a * -1, a)
    d = ema_tv(source=b, length=length)

    len_div = int(length / 5) - 1

    upper = basis + d
    upper_max = np.where(upper > source, upper, source)
    upper_smooth = ema_tv(source=upper_max, length=length)
    upper_diff = np.diff(upper_smooth, prepend=np.nan)
    upper_falling = np.full_like(upper, np.nan)

    lower = basis - d
    lower_min = np.where(lower < source, lower, source)
    lower_smooth = ema_tv(source=lower_min, length=length)
    lower_diff = np.diff(lower_smooth, prepend=np.nan)
    lower_rising = np.full_like(lower, np.nan)

    for x in range(len_div, source.size):
        if not (lower_diff[x - len_div : x + 1] > 0).all():
            continue

        if not (upper_diff[x - len_div : x + 1] < 0).all():
            continue

        lower_rising[x] = lower_smooth[x]
        upper_falling[x] = upper_smooth[x]

    return upper_smooth, upper_falling, lower_smooth, lower_rising


# def range_detextor_lux_algo_tv(
#     candles: np.array,
#     min_range_length: int,
#     atr_multi: int,
#     atr_length: int,
# ) -> tuple[np.array, np.array]:
#     """
#     https://www.tradingview.com/script/QOuZIuvH-Range-Detector-LuxAlgo/
#     """
#     close = candles[:, CandleBodyType.Close]
#     timestamp = candles[:, CandleBodyType.Timestamp]
#     box_y = np.full(close.size * 2, np.nan)
#     box_x = np.full(close.size * 2, np.nan)
#     atr = atr_tv(candles=candles, length=atr_length) * atr_multi
#     sma = sma_tv(source=close, length=min_range_length)

#     count = -1
#     box_index = 0
#     box_top = 0
#     box_bottom = 0
#     len_m_1 = min_range_length - 1
#     for i in range(atr_length, close.size):
#         prev_count = count
#         current_sma = sma[i]
#         current_atr = atr[i]
#         current_timestamp = timestamp[i]
#         lookback_timestamp = timestamp[i - len_m_1]
#         abs_c_m_sma = np.absolute(close[i - len_m_1 : i + 1] - current_sma)
#         count = np.where(abs_c_m_sma > current_atr, 1, 0).sum()

#         # Box = bottom left, top left, top right, bottom right, bottom left
#         # Box =     0           1           2           3           4

#         if count == 0:
#             if count != prev_count:
#                 if lookback_timestamp <= box_x[box_index + 2]:
#                     box_top = max(current_sma + current_atr, box_top)
#                     box_bottom = min(current_sma - current_atr, box_bottom)

#                     # Top
#                     box_y[[box_index + 1, box_index + 2]] = box_top

#                     # Bottom
#                     box_y[[box_index, box_index + 3, box_index + 4]] = box_bottom

#                     # right
#                     box_x[[box_index + 2, box_index + 3]] = timestamp[i]

#                 else:
#                     box_top = current_sma + current_atr
#                     box_bottom = current_sma - current_atr

#                     # Top
#                     box_y[[box_index + 1, box_index + 2]] = box_top

#                     # Bottom
#                     box_y[[box_index, box_index + 3, box_index + 4]] = box_bottom

#                     # Left
#                     box_x[[box_index + 2, box_index + 3]] = current_timestamp

#                     # Right
#                     box_x[[box_index, box_index + 1, box_index + 4]] = lookback_timestamp

#                     box_index += 6
#             else:
#                 box_x[[box_index + 2, box_index + 3]] = current_timestamp
#     return box_x[: box_index - 1], box_y[: box_index - 1]
