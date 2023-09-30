import requests
import time
import hashlib
import hmac
import uuid

api_key='VwecPk0ZLIyiKpsFWe'
secret_key='WdpfMuGmdhj8OBNEYTlCTmLjtNrNzIYRIslT'
httpClient=requests.Session()
recv_window=str(5000)
url="https://api.mufex.finance" # Testnet endpoint

def HTTP_Request(endPoint,method,payload,Info):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genSignature(payload)
    headers = {
        'MF-ACCESS-API-KEY': api_key,
        'MF-ACCESS-SIGN': signature,
        'MF-ACCESS-SIGN-TYPE': '2',
        'MF-ACCESS-TIMESTAMP': time_stamp,
        'MF-ACCESS-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method=="POST"):
        response = httpClient.request(method, url+endPoint, headers=headers, data=payload)
    else:
        response = httpClient.request(method, url+endPoint+"?"+payload, headers=headers)
    print(response.text)
    print(Info + " Elapsed Time : " + str(response.elapsed))

def genSignature(payload):
    param_str= str(time_stamp) + api_key + recv_window + payload
    hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
    signature = hash.hexdigest()
    return signature