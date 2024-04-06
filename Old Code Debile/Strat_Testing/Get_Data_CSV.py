#import requests

#base_url = 'https://api.kucoin.com'
#path = ''

import asyncio
from mimetypes import init
from pickle import FALSE

from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager
import requests
import json


sub = 'SHIB-USDT'
base_url = 'https://api.kucoin.com'

api_key = '<api_key>'
api_secret = '<api_secret>'
api_passphrase = '<api_passphrase>'

CANDLE_START_TIME = 0
CANDLE_OPEN_PRICE = 1
CANDLE_CLOSE_PRICE = 2
CANDLE_HIGH_PRICE = 3
CANDLE_LOW_PRICE = 4
CANDLE_TRANSACTION_VOLUME = 5
CANDLE_TRANSACTION_AMOUNT = 6
CANDLE_TIME = 7


candle_request_end_time = 1668962940
#1440 = 24h
maximum_size_candle_list = 3
classic_candle = []

print('START_INIT')
path = '/api/v1/market/candles?type=1min&symbol=' + sub + '&startAt=' + str(candle_request_end_time - (maximum_size_candle_list * 60)) + '&endAt=' + str(candle_request_end_time)
r = requests.get(base_url+path)
candle = r.json()x

for i in range((len(candle['data'])), 0, -1):
    print(i)
    classic = [candle['data'][i-1][CANDLE_START_TIME], candle['data'][i-1][CANDLE_OPEN_PRICE], candle['data'][i-1][CANDLE_CLOSE_PRICE], candle['data'][i-1][CANDLE_HIGH_PRICE], candle['data'][i-1][CANDLE_LOW_PRICE], candle['data'][i-1][CANDLE_TRANSACTION_VOLUME], candle['data'][i-1][CANDLE_TRANSACTION_AMOUNT]]
    classic_candle.append(classic)

print(classic_candle)
print("---")
