from my_stuff import MufexKeys
from quantfreedom.exchanges.mufex_exchange.mufex import Mufex
from lightweight_charts import Chart
from time import sleep

mufex_main = Mufex(
    api_key=MufexKeys.api_key,
    secret_key=MufexKeys.secret_key,
    use_test_net=False,
)
symbol="BTCUSDT"
candles = mufex_main.get_candles_df(
    symbol=symbol,
    timeframe='1m',
    candles_to_dl=300,
    limit=200
)

if __name__ == '__main__':
    chart = Chart()

    df1 = candles[:150]
    df2 = candles[150:]

    chart.set(df1)

    chart.show()

    last_close = df1.close.iloc[-1]

    for i, series in df2.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')
            
        last_close = series['close']
        sleep(0.1)