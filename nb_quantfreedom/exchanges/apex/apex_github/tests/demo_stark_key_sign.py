import decimal
import os
import sys
import time

from apexpro.helpers.util import round_size
from apexpro.http_private_stark_key_sign import HttpPrivateStark

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

print("Hello, Apexpro")


# need api_key_credentials={'key': key,'secret': secret, 'passphrase': passphrase} for private api
# need starkey for withdraw and createOrder

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

public_key = 'your stark_public_key from register'
public_key_y_coordinate = 'your stark_public_key_y_coordinate from register'
private_key = 'your stark_private_key from register'


client = HttpPrivateStark(APEX_HTTP_TEST, network_id=NETWORKID_TEST,
                          stark_public_key=public_key,
                          stark_private_key=private_key,
                          stark_public_key_y_coordinate=public_key_y_coordinate,
                          api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs()
client.get_user()
print(client.get_account())

# sample1
# When create an order, optimize the size of the order according to the stepSize of the currency symbol,
# and optimize the price of the order according to the tickSize
symbolData = {}
for k, v in enumerate(configs.get('data').get('perpetualContract')):
    if v.get('symbol') == "BTC-USDC":
        symbolData = v

print(round_size("0.0116", symbolData.get('stepSize')))
print(round_size("25555.8", symbolData.get('tickSize')))

# sample2
# Create a limit order
currentTime = time.time()
limitFeeRate = client.account['takerFeeRate']

size = round_size("0.01", symbolData.get('stepSize'))
price = round_size("28888.5", symbolData.get('tickSize'))
createOrderRes = client.create_order(symbol="BTC-USDC", side="BUY",
                                           type="LIMIT", size=size, expirationEpochSeconds= currentTime,
                                           price=price, limitFeeRate=limitFeeRate)
print(createOrderRes)

# sample3
# Create a conditional order

createOrderRes = client.create_order(symbol="ETH-USDC", side="BUY",
                                     type="STOP_LIMIT", size="0.01",expirationEpochSeconds= currentTime,
                                     price="1811.5", limitFeeRate=limitFeeRate, triggerPriceType="INDEX", triggerPrice="1811")
print(createOrderRes)

# sample4
# Create a market order
# first, get a worstPrice from server.( market order price must not none)

worstPrice = client.get_worst_price(symbol="BTC-USDC", side="SELL", size="0.1")
price = worstPrice['data']['worstPrice']

createOrderRes = client.create_order(symbol="BTC-USDC", side="SELL",
                                     type="MARKET", size="1", price=price, limitFeeRate=limitFeeRate,
                                     expirationEpochSeconds= currentTime )
print(createOrderRes)

# sample5
# Create a TP/SL order
# first, Set a slippage to get an acceptable price
# if timeInForce="GOOD_TIL_CANCEL" or "POST_ONLY", slippage is recommended to be greater than 0.1
# if timeInForce="FILL_OR_KILL" or "IMMEDIATE_OR_CANCEL", slippage is recommended to be greater than 0.2
# when buying, the price = price*(1 + slippage). when selling, the price = price*(1 - slippage)

slippage = decimal.Decimal("0.1")
price =  round_size(decimal.Decimal("28888") * (decimal.Decimal("1") + slippage), symbolData.get('tickSize'))

createOrderRes = client.create_order(symbol="BTC-USDC", side="BUY", isPositionTpsl = True, reduceOnly= True,
                                     type="TAKE_PROFIT_MARKET", size="0.1", price=price, limitFeeRate=limitFeeRate,
                                     expirationEpochSeconds= currentTime, triggerPriceType="INDEX", triggerPrice="28888" )
print(createOrderRes)

#createWithdrawRes = client.create_withdrawal(amount='1001',expirationEpochSeconds= currentTime,asset='USDC')
#print(createWithdrawRes)

#feeRes = client.uncommon_withdraw_fee(amount='1002',chainId='5')
#print(feeRes)
#fastWithdrawRes = client.fast_withdrawal(amount='1002',expirationEpochSeconds= currentTime,asset='USDC',fee=feeRes['data']['fee'])
#print(fastWithdrawRes)

deleteOrderRes = client.delete_open_orders(symbol="BTC-USDC")
print(deleteOrderRes)

deleteOrderRes = client.delete_open_orders()
print(deleteOrderRes)


feeRes = client.uncommon_withdraw_fee(amount='1003',chainId='97')
print(feeRes)
crossWithdrawRes = client.cross_chain_withdraw(amount='1003',expirationEpochSeconds= currentTime,asset='USDC',fee=feeRes['data']['fee'],chainId='97')
print(crossWithdrawRes)

print("end, Apexpro")
