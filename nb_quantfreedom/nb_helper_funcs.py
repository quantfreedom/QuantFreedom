import plotly.graph_objects as go
import numpy as np
import logging
import pandas as pd
from quantfreedom.enums import OrderSettings, OrderSettingsArrays
from numba import njit

info_logger = logging.getLogger("info")

@njit()
def get_to_the_upside_nb(
    gains_pct: float,
    wins_and_losses_array_no_be: np.array,
):
    x = np.arange(1, len(wins_and_losses_array_no_be) + 1)
    y = wins_and_losses_array_no_be.cumsum()

    xm = x.mean()
    ym = y.mean()

    y_ym = y - ym
    if y_ym.all() == 0:
        y_ym = np.array([1])
    y_ym_s = y_ym**2

    x_xm = x - xm
    if x_xm.all() == 0:
        x_xm = np.array([1])
    x_xm_s = x_xm**2

    b1 = (x_xm * y_ym).sum() / x_xm_s.sum()
    b0 = ym - b1 * xm

    y_pred = b0 + b1 * x

    yp_ym = y_pred - ym

    yp_ym_s = yp_ym**2

    to_the_upside = yp_ym_s.sum() / y_ym_s.sum()

    if gains_pct <= 0:
        to_the_upside = -to_the_upside
    return round(to_the_upside, 4)

@njit()
def create_os_cart_product_nb(order_settings_arrays: OrderSettingsArrays):
    # cart array loop
    n = 1
    for x in order_settings_arrays:
        n *= x.size
    out = np.empty((n, len(order_settings_arrays)))

    for i in range(len(order_settings_arrays)):
        m = int(n / order_settings_arrays[i].size)
        out[:n, i] = np.repeat(order_settings_arrays[i], m)
        n //= order_settings_arrays[i].size

    n = order_settings_arrays[-1].size
    for k in range(len(order_settings_arrays) - 2, -1, -1):
        n *= order_settings_arrays[k].size
        m = int(n / order_settings_arrays[k].size)
        for j in range(1, order_settings_arrays[k].size):
            out[j * m : (j + 1) * m, k + 1 :] = out[0:m, k + 1 :]

    return OrderSettingsArrays(
        increase_position_type=out.T[0].astype(np.int_),
        leverage_type=out.T[1].astype(np.int_),
        max_equity_risk_pct=out.T[2],
        long_or_short=out.T[3].astype(np.int_),
        risk_account_pct_size=out.T[4],
        risk_reward=out.T[5],
        sl_based_on_add_pct=out.T[6],
        sl_based_on_lookback=out.T[7].astype(np.int_),
        sl_candle_body_type=out.T[8].astype(np.int_),
        sl_to_be_based_on_candle_body_type=out.T[9].astype(np.int_),
        sl_to_be_when_pct_from_candle_body=out.T[10],
        sl_to_be_zero_or_entry_type=out.T[11].astype(np.int_),
        static_leverage=out.T[12],
        stop_loss_type=out.T[13].astype(np.int_),
        take_profit_type=out.T[14].astype(np.int_),
        tp_fee_type=out.T[15].astype(np.int_),
        trail_sl_based_on_candle_body_type=out.T[16].astype(np.int_),
        trail_sl_by_pct=out.T[17],
        trail_sl_when_pct_from_candle_body=out.T[18],
        num_candles=out.T[19].astype(np.int_),
        entry_size_asset=out.T[20].astype(np.int_),
        max_trades=out.T[21].astype(np.int_),
    )

@njit()
def get_order_setting(os_cart_arrays: OrderSettingsArrays, order_settings_index: int):
    return OrderSettings(
        increase_position_type=os_cart_arrays.increase_position_type[order_settings_index],
        leverage_type=os_cart_arrays.leverage_type[order_settings_index],
        max_equity_risk_pct=os_cart_arrays.max_equity_risk_pct[order_settings_index] / 100,
        long_or_short=os_cart_arrays.long_or_short[order_settings_index],
        risk_account_pct_size=os_cart_arrays.risk_account_pct_size[order_settings_index] / 100,
        risk_reward=os_cart_arrays.risk_reward[order_settings_index],
        sl_based_on_add_pct=os_cart_arrays.sl_based_on_add_pct[order_settings_index] / 100,
        sl_based_on_lookback=os_cart_arrays.sl_based_on_lookback[order_settings_index],
        sl_candle_body_type=os_cart_arrays.sl_candle_body_type[order_settings_index],
        sl_to_be_based_on_candle_body_type=os_cart_arrays.sl_to_be_based_on_candle_body_type[order_settings_index],
        sl_to_be_when_pct_from_candle_body=os_cart_arrays.sl_to_be_when_pct_from_candle_body[order_settings_index]
        / 100,
        sl_to_be_zero_or_entry_type=os_cart_arrays.sl_to_be_zero_or_entry_type[order_settings_index],
        static_leverage=os_cart_arrays.static_leverage[order_settings_index],
        stop_loss_type=os_cart_arrays.stop_loss_type[order_settings_index],
        take_profit_type=os_cart_arrays.take_profit_type[order_settings_index],
        tp_fee_type=os_cart_arrays.tp_fee_type[order_settings_index],
        trail_sl_based_on_candle_body_type=os_cart_arrays.trail_sl_based_on_candle_body_type[order_settings_index],
        trail_sl_by_pct=os_cart_arrays.trail_sl_by_pct[order_settings_index] / 100,
        trail_sl_when_pct_from_candle_body=os_cart_arrays.trail_sl_when_pct_from_candle_body[order_settings_index]
        / 100,
        num_candles=os_cart_arrays.num_candles[order_settings_index],
        entry_size_asset=os_cart_arrays.entry_size_asset[order_settings_index],
        max_trades=os_cart_arrays.max_trades[order_settings_index],
    )


@njit
def nb_round_size_by_tick_step(user_num: float, exchange_num: float) -> float:
    return round(user_num, exchange_num)


def plot_candles(candles: pd.DataFrame):
    fig = go.Figure()
    fig.add_candlestick(
        x=candles.index,
        open=candles.open,
        high=candles.high,
        low=candles.low,
        close=candles.close,
        name="Candles",
    )
    fig.show()
