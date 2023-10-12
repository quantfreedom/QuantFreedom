from datetime import datetime
import json
import websocket
from pprint import pprint
from my_stuff import MufexKeys


def on_open(ws):
    print("opened")
    ws.send(json.dumps({"op": "auth", "args": MufexKeys.api_key}))
    ws.send(json.dumps({"op": "subscribe", "args": ["trades-100.BTCUSDT"]}))


def on_close(ws):
    print("closed connection")


def on_message(ws, message):
    candle_info = json.loads(message)["data"]["d"][0]
    print("")
    print("New Trade")
    print(f"price       {float(candle_info[1])}")
    print(f"asset qty   {float(candle_info[2])}")
    print(f"usd qty     {round(float(candle_info[1]) * float(candle_info[2]),4)}")
    print(f"timestamp   {candle_info[3]}")
    print(f"sec time    {int(datetime.strptime(candle_info[3], '%Y-%m-%dT%H:%M:%SZ').timestamp())}")
    print(f"Side        {'Sell' if candle_info[4] == 'a' else 'Buy'}")


socket = "wss://ws.mufex.finance/realtime_public"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever(ping_interval=5)
