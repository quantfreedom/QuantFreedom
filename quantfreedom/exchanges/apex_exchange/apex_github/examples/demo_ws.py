from time import sleep

from quantfreedom.exchanges.apex_exchange.apex_github.constants import APEX_WS_TEST
from quantfreedom.exchanges.apex_exchange.apex_github.websocket_api import WebSocket

key = "your apiKey-key from register"
secret = "your apiKey-secret from register"
passphrase = "your apiKey-passphrase from register"

# Connect with authentication!
ws_client = WebSocket(
    endpoint=APEX_WS_TEST,
    api_key_credentials={"key": key, "secret": secret, "passphrase": passphrase},
)


def handle_account(message):
    print(message)
    contents_data = message["contents"]
    print(len(contents_data))


def h1(message):
    print(1, message)


def h2(message):
    print(2, message)


def h3(message):
    print(3, message)


def h4(message):
    print(4, message)


# ws_client.depth_stream(h1,'BTCUSDC',25)
# ws_client.ticker_stream(h2,'BTCUSDC')
# ws_client.trade_stream(h3,'BTCUSDC')
# ws_client.klines_stream(h4,'BTCUSDC',1)
ws_client.account_info_stream(handle_account)


while True:
    # Run your main trading logic here.
    sleep(1)
