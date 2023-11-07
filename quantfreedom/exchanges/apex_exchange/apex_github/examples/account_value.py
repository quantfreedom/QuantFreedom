import decimal
import time
from threading import Timer

from quantfreedom.exchanges.apex_exchange.apex_github.constants import APEX_WS_TEST, APEX_HTTP_TEST, NETWORKID_TEST
from quantfreedom.exchanges.apex_exchange.apex_github.http_private import HttpPrivate
from quantfreedom.exchanges.apex_exchange.apex_github.http_public import HttpPublic
from quantfreedom.exchanges.apex_exchange.apex_github.websocket_api import WebSocket

key = "your apiKey-key from register"
secret = "your apiKey-secret from register"
passphrase = "your apiKey-passphrase from register"

ticker_time = 10

# Connect with authentication!
ws_client = WebSocket(endpoint=APEX_WS_TEST)
client = HttpPrivate(
    APEX_HTTP_TEST,
    network_id=NETWORKID_TEST,
    api_key_credentials={"key": key, "secret": secret, "passphrase": passphrase},
)

symbol_list = client.configs().get("data").get("perpetualContract")
print("symbol_list:", symbol_list)


wallets = {}
openPositions = {}
orders = {}

allTickerPrice = []


def all_ticker(message):
    global allTickerPrice
    print("all_ticker: ", message)
    newAllTickerPrice = message.get("data")

    if len(wallets) == 0:
        allTickerPrice = newAllTickerPrice
        handle_account()
        return

    if newAllTickerPrice is not None:
        for k, position in enumerate(openPositions):
            oldPrice = decimal.Decimal(get_symbol_price(position.get("symbol")))
            symbolData = get_symbol_config(position.get("symbol"))
            for k, v in enumerate(newAllTickerPrice):
                if (
                    v["s"] == symbolData.get("symbol")
                    or v["s"] == symbolData.get("crossSymbolName")
                    or v["s"] == symbolData.get("symbolDisplayName")
                ):
                    if v.get("op") is not None:
                        newPrice = decimal.Decimal(v.get("op"))
                        if oldPrice != newPrice:
                            print(v["s"] + "  oldPrice: " + str(oldPrice) + "  newPrice: " + str(newPrice))
                            handle_account()
                            allTickerPrice = newAllTickerPrice
                            return
        allTickerPrice = newAllTickerPrice


ws_client.all_ticker_stream(all_ticker)


def handle_account():
    print("current time:", time.time())
    global client, wallets, openPositions, orders
    account = client.get_account()
    if account.get("data") is not None and account.get("data").get("wallets") is not None:
        wallets = account.get("data").get("wallets")
    if account.get("data") is not None and account.get("data").get("openPositions") is not None:
        openPositions = account.get("data").get("openPositions")

    get_orders = client.open_orders()
    if get_orders.get("data") is not None:
        orders = get_orders.get("data")

    totalAccountValue = decimal.Decimal("0.0")
    for k, wallet in enumerate(wallets):
        if wallet.get("asset") == "USDC":
            totalAccountValue = (
                decimal.Decimal(wallet.get("balance"))
                - decimal.Decimal(wallet.get("pendingWithdrawAmount"))
                - decimal.Decimal(wallet.get("pendingTransferOutAmount"))
            )
    for k, position in enumerate(openPositions):
        positionValue = decimal.Decimal(position.get("size")) * decimal.Decimal(
            get_symbol_price(position.get("symbol"))
        )
        if position.get("side") == "SHORT":
            positionValue = positionValue * decimal.Decimal(-1)
        totalAccountValue = totalAccountValue + positionValue

    print("totalAccountValue is :" + str(totalAccountValue))

    totalInitialMarginRequirement = decimal.Decimal("0.0")
    for k, position in enumerate(openPositions):
        totalInitialMarginRequirement = totalInitialMarginRequirement + decimal.Decimal(
            position.get("entryPrice")
        ) * decimal.Decimal(position.get("size")) * decimal.Decimal(
            get_symbol_config(position.get("symbol")).get("initialMarginRate")
        )

    orderTotalInitialMarginRequirement = decimal.Decimal("0.0")
    for k, order in enumerate(orders):
        orderTotalInitialMarginRequirement = orderTotalInitialMarginRequirement + decimal.Decimal(
            order.get("price")
        ) * decimal.Decimal(order.get("size")) * decimal.Decimal(
            get_symbol_config(position.get("symbol")).get("initialMarginRate")
        )
        orderTotalInitialMarginRequirement = orderTotalInitialMarginRequirement + decimal.Decimal(
            order.get("price")
        ) * decimal.Decimal(order.get("size")) * decimal.Decimal(account.get("data").get("takerFeeRate"))

    availableValue = totalAccountValue - totalInitialMarginRequirement - orderTotalInitialMarginRequirement

    print("availableValue is :" + str(availableValue))

    totalMaintenanceMarginRequirement = decimal.Decimal("0.0")
    for k, position in enumerate(openPositions):
        totalMaintenanceMarginRequirement = totalMaintenanceMarginRequirement + decimal.Decimal(
            position.get("size")
        ) * decimal.Decimal(get_symbol_price(position.get("symbol"))) * decimal.Decimal(
            get_symbol_config(position.get("symbol")).get("maintenanceMarginRate")
        )

    print("totalMaintenanceMarginRequirement is :" + str(totalMaintenanceMarginRequirement))


def get_symbol_config(symbol):
    for k, v in enumerate(symbol_list):
        if v.get("symbol") == symbol or v.get("crossSymbolName") == symbol or v.get("symbolDisplayName") == symbol:
            return v


def get_symbol_price(symbol):
    global allTickerPrice
    symbolData = get_symbol_config(symbol)
    for k, v in enumerate(allTickerPrice):
        if (
            v["s"] == symbolData.get("symbol")
            or v["s"] == symbolData.get("crossSymbolName")
            or v["s"] == symbolData.get("symbolDisplayName")
        ):
            return v.get("op")


while True:
    # Run your main trading logic here.
    time.sleep(2)
    timer = Timer(ticker_time, handle_account)
    timer.start()
    timer.join()
