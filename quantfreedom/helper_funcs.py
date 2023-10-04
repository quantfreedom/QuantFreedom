import numpy as np

from quantfreedom.enums import OrderSettings, OrderSettingsArrays


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
        increase_position_type=out.T[0],
        leverage_type=out.T[1],
        max_equity_risk_pct=out.T[2],
        long_or_short=out.T[3],
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


def get_order_setting_tuple_from_index(order_settings_array: OrderSettingsArrays, index: int):
    return OrderSettings(
        increase_position_type=order_settings_array.increase_position_type[index],
        leverage_type=order_settings_array.leverage_type[index],
        max_equity_risk_pct=order_settings_array.max_equity_risk_pct[index],
        long_or_short=order_settings_array.long_or_short[index],
        risk_account_pct_size=order_settings_array.risk_account_pct_size[index],
        risk_reward=order_settings_array.risk_reward[index],
        sl_based_on_add_pct=order_settings_array.sl_based_on_add_pct[index],
        sl_based_on_lookback=order_settings_array.sl_based_on_lookback[index],
        sl_candle_body_type=order_settings_array.sl_candle_body_type[index],
        sl_to_be_based_on_candle_body_type=order_settings_array.sl_to_be_based_on_candle_body_type[index],
        sl_to_be_when_pct_from_candle_body=order_settings_array.sl_to_be_when_pct_from_candle_body[index],
        sl_to_be_zero_or_entry_type=order_settings_array.sl_to_be_zero_or_entry_type[index],
        static_leverage=order_settings_array.static_leverage[index],
        stop_loss_type=order_settings_array.stop_loss_type[index],
        take_profit_type=order_settings_array.take_profit_type[index],
        tp_fee_type=order_settings_array.tp_fee_type[index],
        trail_sl_based_on_candle_body_type=order_settings_array.trail_sl_based_on_candle_body_type[index],
        trail_sl_by_pct=order_settings_array.trail_sl_by_pct[index],
        trail_sl_when_pct_from_candle_body=order_settings_array.trail_sl_when_pct_from_candle_body[index],
    )
