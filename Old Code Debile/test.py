import requests
import pandas as pd
from datetime import datetime
import hmac
import hashlib
import time
import json
from kucoin.client import Client

symbol = "XMR-USDT"

#api_key = '63bc574520958500011dc92d'
#api_secret = '3da1c93f-48db-4c89-8302-dd203e248195'
#api_passphrase = 'alfred-vava'

def place_buy_order(api_key, api_secret, symbol, size, price=None):
    """
    Place a long buy order on Kucoin.
    """
    # Set the API endpoint URL
    url = "https://api.kucoin.com/api/v1/orders"

    # Set the request method and content type
    method = "POST"
    content_type = "application/json"

    # Set the request timestamp
    timestamp = str(time.time())

    # Construct the request body
    if price is None:
        # Market order
        body = {
            "symbol": symbol,
            "type": "MARKET",
            "side": "BUY",
            "size": size
        }
    else:
        # Limit order
        body = {
            "symbol": symbol,
            "type": "LIMIT",
            "side": "BUY",
            "size": size,
            "price": price
        }

    # Serialize the request body to JSON
    body = json.dumps(body)

    # Construct the message to be signed
    message = f"{timestamp}{method}{content_type}{body}"

    # Sign the message using the API secret
    signature = hmac.new(bytes(api_secret, "latin1"), msg=bytes(message, "latin1"), digestmod=hashlib.sha256).hexdigest()

    # Set the request headers
    headers = {
        "Content-Type": content_type,
        "KC-API-KEY": api_key,
        "KC-API-TIMESTAMP": timestamp,
        "KC-API-SIGNATURE": signature
    }

    # Send the request
    response = requests.post(url, data=body, headers=headers)

    # Print the response status code
    print(response.status_code)


#place_buy_order(api_key, api_secret, symbol, 0.1, price=None)

b = pd.to_datetime(1673538300, unit='s')
print(b)

#client = Client(api_key, api_secret, api_passphrase)

# place a market buy order
#order = client.create_market_order('XMR-USDT', Client.SIDE_SELL, size=0.1)

def append2_max(array, elem, msg_l=None):
    if(msg_l == None):
        array.append(elem)
    else:
        if(msg_l[-1] == msg_l[-2]):
            array[-1] = elem
    
        else:
            array.append(elem)

    len_ = len(array)

msg_list = [0, 1]
a = [0, 1, 2]
append2_max(a, 5, msg_list)
print(a)