import requests
import time
import hashlib
import hmac
import uuid

api_key = "xxxxxxx"
secret_key = "xxxxxxxxxxxxxxxxxx"
httpClient = requests.Session()
recv_window = str(5000)
url = "https://api.mufex.finance"  # Testnet endpoint


def HTTP_Request(endPoint, method, payload, Info):
    global time_stamp
    time_stamp = str(int(time.time() * 10**3))
    param_str = str(time_stamp) + recv_window
    hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()
    headers = {
        # 'MF-ACCESS-API-KEY': api_key,
        'MF-ACCESS-SIGN': signature,
        "MF-ACCESS-SIGN-TYPE": "2",
        "MF-ACCESS-TIMESTAMP": time_stamp,
        "MF-ACCESS-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }
    if method == "POST":
        response = httpClient.request(method, url + endPoint, headers=headers, data=payload)
    else:
        response = httpClient.request(method, url + endPoint + "?",payload, headers=headers)
    return response.json()['data']['list']



# #Create Order
# endpoint="/private/v1/trade/create"
# method="POST"
# orderLinkId=uuid.uuid4().hex
# params='{"symbol": "BTCUSDT","side": "Buy","positionIdx": 0,"orderType": "Limit","qty": "0.001","price": "28000","timeInForce": "GoodTillCancel","orderLinkId": "' + orderLinkId + '"}'
# HTTP_Request(endpoint,method,params,"Create")

# #Get unfilled Orders
# endpoint="/private/v1/trade/activity-orders"
# method="GET"
# params='symbol=BTCUSDT'
# HTTP_Request(endpoint,method,params,"UnFilled")

# #Get Order List
# endpoint="/private/v1/trade/orders"
# method="GET"
# params="symbol=BTCUSDT&orderStatus=New&orderLinkId="+orderLinkId
# HTTP_Request(endpoint,method,params,"List")
