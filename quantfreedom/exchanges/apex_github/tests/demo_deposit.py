import os
import sys
import time

from apexpro.helpers.util import wait_for_condition

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.http_private import HttpPrivate
from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

print("Hello, Apexpro")
priKey = "your eth private key"

key = 'your apiKey-key from register'
secret = 'your apiKey-secret from register'
passphrase = 'your apiKey-passphrase from register'

public_key = 'your stark_public_key from register'
public_key_y_coordinate = 'your stark_public_key_y_coordinate from register'
private_key = 'your stark_private_key from register'


client = HttpPrivate(APEX_HTTP_MAIN, network_id=NETWORKID_MAIN, eth_private_key=priKey,
                     stark_public_key=public_key,
                     stark_private_key=private_key,
                     stark_public_key_y_coordinate=public_key_y_coordinate,
                     api_key_credentials={'key': key, 'secret': secret, 'passphrase': passphrase})
configs = client.configs()

account = client.get_account()

# If you have not approve usdc on eth, please approve first
# Set allowance on the Starkware perpetual contract, for the deposit.
#approve_tx_hash = client.eth.set_token_max_allowance(
#    client.eth.get_exchange_contract().address,
#)
print('Waiting for allowance...')
# Don't worry if you encounter a timeout request while waiting. Execution on the chain takes a certain time
#client.eth.wait_for_tx(approve_tx_hash)
print('...done.')

# Send an on-chain deposit.
deposit_tx_hash = client.eth.deposit_to_exchange(
    client.account['positionId'],
    0.1,
)
print('Waiting for deposit...')
# Don't worry if you encounter a timeout request while waiting. Execution on the chain takes a certain time

client.eth.wait_for_tx(deposit_tx_hash)
print('...done.')



