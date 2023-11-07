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
configs = client.configs_v2()

# userRes = client.get_user()
# print(userRes)


# modifyUserRes = client.modify_user(username="pythonTest",email="11@aa.com",emailNotifyGeneralEnable="false")
# print(modifyUserRes)

accountRes = client.get_account_v2()
print(accountRes)

fillsRes = client.fills_v2(limit=100, page=0, symbol="BTC-USDT", side="BUY", token="USDT")
print(fillsRes)

transfersRes = client.transfers_v2(limit=100, page=0, currencyId="USDT", chainIds="1,5,13,97")
print(transfersRes)

withdrawListRes = client.withdraw_list_v2(
    limit=100, page=0, beginTimeInclusive=1651406864000, endTimeExclusive=1657105971171
)
print(withdrawListRes)

uncommon_withdraw_feeRes = client.uncommon_withdraw_fee_v2(amount="101000.1", token="USDT", chainId=5)
print(uncommon_withdraw_feeRes)

transfer_limitRes = client.transfer_limit_v2(currencyId="USDT")
print(transfer_limitRes)

fillsRes = client.fills_v2(limit=100, page=0, symbol="BTC-USDT", side="BUY", token="USDT")
print(fillsRes)

deleteOrderRes = client.delete_order_v2(id="123456")
print(deleteOrderRes)

deleteOrderRes = client.delete_order_by_client_order_id_v2(id="123456")
print(deleteOrderRes)

openOrdersRes = client.open_orders_v2(token="USDT")
print(openOrdersRes)

deleteOrdersRes = client.delete_open_orders(symbol="BTC-USDC,ETH-USDC", token="USDT")
print(deleteOrdersRes)

historyOrdersRes = client.history_orders_v2(token="USDT")
print(historyOrdersRes)

getOrderRes = client.get_order_v2(id="123456")
print(getOrderRes)

getOrderRes = client.get_order_by_client_order_id_v2(id="123456")
print(getOrderRes)

fundingRes = client.funding_v2(limit=100, page=0, symbol="BTC-USDC", side="BUY", token="USDT")
print(fundingRes)

notifyListRes = client.notify_list(limit=100, page=0, unreadOnly="true", notifyCategory="1")
print(notifyListRes)

markNotifyReadRes = client.mark_notify_read(ids="113123,123123123")
print(markNotifyReadRes)

historicalPnlRes = client.historical_pnl_v2(
    limit=100, page=0, beginTimeInclusive=1651406864000, endTimeExclusive=1657105971171, symbol="BTC-USDC"
)
print(historicalPnlRes)

yesterdayPnlRes = client.yesterday_pnl_v2(token="USDT")
print(yesterdayPnlRes)

historyValueRes = client.history_value_v2(token="USDT")
print(historyValueRes)

markAllNotifyReadRes = client.mark_all_notify_read()
print(markAllNotifyReadRes)

setInitialMarginRateRes = client.set_initial_margin_rate_v2(symbol="BTC-USDC", initialMarginRate="0.1", token="USDT")
print(setInitialMarginRateRes)


print("end, Apexpro")
