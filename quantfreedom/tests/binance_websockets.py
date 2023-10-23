from datetime import datetime
import json
import websocket
from pprint import pprint
from my_stuff import MufexKeys


def on_open(ws):
    print("opened")
    # ws.send(json.dumps({"op": "auth", "args": MufexKeys.api_key}))
    # ws.send(json.dumps({"op": "subscribe", "args": ["trades-100.BTCUSDT"]}))


def on_close(ws):
    print("closed connection")


def on_message(ws, message):
    """
    https://binance-docs.github.io/apidocs/futures/en/#aggregate-trade-streams

    {
      "e": "aggTrade",  // Event type
      "E": 123456789,   // Event time
      "s": "BTCUSDT",    // Symbol
      "a": 5933014,     // Aggregate trade ID
      "p": "0.001",     // Price
      "q": "100",       // Quantity
      "f": 100,         // First trade ID
      "l": 105,         // Last trade ID
      "T": 123456785,   // Trade time
      "m": true,        // Is the buyer the market maker?
    }

    """
    pprint(json.loads(message))


socket = "wss://fstream.binance.com/ws/btcusdt@aggTrade"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever(ping_interval=5)
