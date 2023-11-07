import os
import sys


root_path = os.path.abspath(__file__)
root_path = "/".join(root_path.split("/")[:-2])
sys.path.append(root_path)

from quantfreedom.exchanges.apex_exchange.apex_github.http_private import HttpPrivate

from quantfreedom.exchanges.apex_exchange.apex_github.constants import APEX_HTTP_TEST, NETWORKID_TEST

print("Hello, Apexpro")
# need api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase} for private api

key = "your apiKey-key from register"
secret = "your apiKey-secret from register"
passphrase = "your apiKey-passphrase from register"

client = HttpPrivate(
    APEX_HTTP_TEST,
    network_id=NETWORKID_TEST,
    api_key_credentials={"key": key, "secret": secret, "passphrase": passphrase},
)
configs = client.configs()

userRes = client.get_user()
print(userRes)

modifyUserRes = client.modify_user(username="pythonTest", email="11@aa.com", emailNotifyGeneralEnable="false")
print(modifyUserRes)

accountRes = client.get_account()
print(accountRes)


transfersRes = client.transfers(limit=100, page=0, currencyId="USDC", chainIds="1,5,13")
print(transfersRes)

withdrawListRes = client.withdraw_list(
    limit=100, page=0, beginTimeInclusive=1651406864000, endTimeExclusive=1657105971171
)
print(withdrawListRes)

uncommon_withdraw_feeRes = client.uncommon_withdraw_fee(amount="101000.1", chainId=5)
print(uncommon_withdraw_feeRes)

transfer_limitRes = client.transfer_limit(currencyId="USDC")
print(transfer_limitRes)

fillsRes = client.fills(limit=100, page=0, symbol="BTC-USDC", side="BUY")
print(fillsRes)

deleteOrderRes = client.delete_order(id="123456")
print(deleteOrderRes)

deleteOrderRes = client.delete_order_by_client_order_id(id="123456")
print(deleteOrderRes)

openOrdersRes = client.open_orders()
print(openOrdersRes)

deleteOrdersRes = client.delete_open_orders(symbol="BTC-USDC,ETH-USDC")
print(deleteOrdersRes)

historyOrdersRes = client.history_orders()
print(historyOrdersRes)

getOrderRes = client.get_order(id="123456")
print(getOrderRes)

getOrderRes = client.get_order_by_client_order_id(id="123456")
print(getOrderRes)

fundingRes = client.funding(limit=100, page=0, symbol="BTC-USDC", side="BUY")
print(fundingRes)

notifyListRes = client.notify_list(limit=100, page=0, unreadOnly="true", notifyCategory="1")
print(notifyListRes)

markNotifyReadRes = client.mark_notify_read(ids="113123,123123123")
print(markNotifyReadRes)

historicalPnlRes = client.historical_pnl(
    limit=100, page=0, beginTimeInclusive=1651406864000, endTimeExclusive=1657105971171, symbol="BTC-USDC"
)
print(historicalPnlRes)

yesterdayPnlRes = client.yesterday_pnl()
print(yesterdayPnlRes)

historyValueRes = client.history_value()
print(historyValueRes)

markAllNotifyReadRes = client.mark_all_notify_read()
print(markAllNotifyReadRes)

setInitialMarginRateRes = client.set_initial_margin_rate(symbol="BTC-USDC", initialMarginRate="0.1")
print(setInitialMarginRateRes)


print("end, Apexpro")
