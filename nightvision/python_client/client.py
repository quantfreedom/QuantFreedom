import requests
import datetime
import math
import random
from my_stuff import MufexKeys
from quantfreedom.exchanges.mufex_exchange.mufex import Mufex
from time import sleep
import numpy as np

mufex_main = Mufex(
    api_key=MufexKeys.api_key,
    secret_key=MufexKeys.secret_key,
    use_test_net=False,
)
symbol = "BTCUSDT"
candles = mufex_main.get_candles_df(symbol=symbol, timeframe="1m", candles_to_dl=300, limit=200).reset_index()
# candles.timestamp = candles.timestamp.dt.strftime("%Y-%m-%d %X")
candles.timestamp = candles.timestamp.astype(np.int64) // 100000
candles = candles.values.tolist()
candles


# Generate some fake data
# time_series = []
# for i in range(30):
#     time = datetime.datetime.strptime("2022-11-" + str(i + 1), "%Y-%m-%d")
#     t = math.floor(time.timestamp()) * 1000
#     time_series.append([t, random.random() * (i + 1)])

# Data that we will send in POST request


# The POST request to our NightVision server
res = requests.post("http://127.0.0.1:7779/plot", json=candles)

# Convert response data to json
returned_data = res.json()

print(returned_data)
