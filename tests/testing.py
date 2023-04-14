import quantfreedom as qf


price_data = qf.generate_candles(
    number_of_candles=200,
    plot_candles=False,
    seed=None,
)
rsi_data = qf.from_talib(
    func_name="rsi",
    price_data=price_data,
    timeperiod=20,
    plot_results=False,
    # price="low",
)