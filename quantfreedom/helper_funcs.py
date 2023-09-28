import numpy as np

from quantfreedom.enums import OrderSettingsArrays


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
        increase_position_type=out.T[0],
        leverage_type=out.T[1],
        max_equity_risk_pct=out.T[2],
        order_type=out.T[3],
        risk_account_pct_size=out.T[4],
        risk_reward=out.T[5],
        sl_based_on_add_pct=out.T[6],
        sl_based_on_lookback=out.T[7],
        sl_candle_body_type=out.T[8],
        sl_to_be_based_on_candle_body_type=out.T[9],
        sl_to_be_when_pct_from_candle_body=out.T[10],
        sl_to_be_zero_or_entry_type=out.T[11],
        static_leverage=out.T[12],
        stop_loss_type=out.T[13],
        take_profit_type=out.T[14],
        tp_fee_type=out.T[15],
        trail_sl_based_on_candle_body_type=out.T[16],
        trail_sl_by_pct=out.T[17],
        trail_sl_when_pct_from_candle_body=out.T[18],
    )
