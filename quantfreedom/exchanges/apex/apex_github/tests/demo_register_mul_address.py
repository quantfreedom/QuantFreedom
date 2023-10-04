import os
import sys

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)

from apexpro.http_private import HttpPrivate
from apexpro.constants import APEX_HTTP_TEST, NETWORKID_TEST, APEX_HTTP_MAIN, NETWORKID_MAIN

print("Hello, Apexpro")
priKey = "your eth private key"

client = HttpPrivate(APEX_HTTP_MAIN, network_id=NETWORKID_MAIN, eth_private_key=priKey)
configs = client.configs()

stark_key_pair_with_y_coordinate = client.derive_stark_key(client.default_address)

nonceRes = client.generate_nonce(starkKey=stark_key_pair_with_y_coordinate['public_key'],ethAddress=client.default_address,chainId=NETWORKID_MAIN)

#api_key = client.recover_api_key_credentials(nonce=nonceRes['data']['nonce'], ethereum_address=client.default_address)
#print(api_key)

regRes = client.register_user(nonce=nonceRes['data']['nonce'],starkKey=stark_key_pair_with_y_coordinate['public_key'],stark_public_key_y_coordinate=stark_key_pair_with_y_coordinate['public_key_y_coordinate'],ethereum_address=client.default_address,
                              eth_mul_address="your mul eth address")
key = regRes['data']['apiKey']['key']
secret = regRes['data']['apiKey']['secret']
passphrase = regRes['data']['apiKey']['passphrase']

#back stark_key_pair, apiKey,and accountId for private Api or create-oreder or withdraw
print(stark_key_pair_with_y_coordinate)
print(regRes['data']['account']['positionId'])
print(regRes['data']['apiKey'])
print("end, Apexpro")



