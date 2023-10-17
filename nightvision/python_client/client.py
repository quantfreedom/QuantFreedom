import requests
from my_stuff import MufexKeys
from quantfreedom.exchanges.mufex_exchange.mufex import Mufex
import pandas as pd

mufex_main = Mufex(
    api_key=MufexKeys.api_key,
    secret_key=MufexKeys.secret_key,
    use_test_net=False,
)
symbol = "BTCUSDT"
candles = mufex_main.get_candles_df(symbol=symbol, timeframe="1m", candles_to_dl=300)
candles = pd.DataFrame(candles).values.tolist()

# The POST request to our NightVision server
res = requests.post("http://127.0.0.1:7779/plot", json=candles)

# Convert response data to json
returned_data = res.json()

print(returned_data)
