import numpy as np
from numba import njit



@njit(cache=True)
def create_os_cart_product_nb(
    order_settings_arrays: OrderSettingsArrays,
):
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
        risk_account_pct_size=out.T[0],
        sl_based_on_add_pct=out.T[1],
        sl_based_on_lookback=out.T[2],
        risk_reward=out.T[3],
        leverage_type=out.T[4],
        candle_body=out.T[5],
        entry_size_type=out.T[6],
        stop_loss_type=out.T[7],
        take_profit_type=out.T[8],
        max_equity_risk_pct=out.T[9],
    )

