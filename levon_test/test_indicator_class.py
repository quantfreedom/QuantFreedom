from quantfreedom import generate_candles
from quantfreedom.levon_qf.talib_ind_levon import from_talib

price_data = generate_candles(
    number_of_candles=200,
    plot_candles=False,
    seed=None,
)
rsi_data = from_talib(
     func_name="rsi",
     price_data=price_data,
    timeperiod=20,
    plot_results=False,
    # price="low",
)
rsi_ema_ind = from_talib(
    func_name='ema',
    indicator_data=rsi_data.data,
    cart_product=False,
    combos=False,
    timeperiod=15,
)
print(rsi_data.is_below(user_args=45))
print(rsi_ema_ind.data)
print(rsi_data.is_below(indicator_data=rsi_ema_ind.data))
print(rsi_data.combined_data_frame(['is_below0', 'is_below1']))