import os
import sys

from apexpro.helpers.request_helpers import calc_bind_owner_key_sig_hash, starkex_sign, starkex_verify

root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-2])
sys.path.append(root_path)


print("Hello, Apexpro")

hash = calc_bind_owner_key_sig_hash('your stark_key_pair pubic key', "your eth address")
print(hash.hex())

signature = starkex_sign(hash, 'your stark_key_pair private key')
print("signature:" + signature)

bVerify = starkex_verify(hash, signature, 'your stark_key_pair pubic key')
print("Verify:" +str( bVerify))



