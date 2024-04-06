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

sub = 'ETH-USDT'
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


msg_list = []
classic_candle = []
#1440 = 24h
maximum_size_heikin_candle_list = 1440
heikin_candle = []

def sort_classic_candle():

    if(len(classic_candle) == 0):
        classic_candle.append(msg_list[0])
    elif(len(classic_candle) == 1):
        if(msg_list[0][CANDLE_START_TIME] == msg_list[1][CANDLE_START_TIME]):
            classic_candle[0] = msg_list[1]
        #premiere candle avec start tilme different
        else:
            classic_candle.append(msg_list[1])
            init_candle_array()
    elif(len(classic_candle) == 2):
        if(msg_list[0][CANDLE_START_TIME] == msg_list[1][CANDLE_START_TIME]):
            classic_candle[1] = msg_list[1]
        else:
            classic_candle.pop(0)
            classic_candle.append(msg_list[1])
    else:
        print(f'ERROR_1')
    
    if(1 == 0):
        print('classic_candle')
        print(classic_candle)
        print('--------------------')
        print('')
    
def compute_heikin():

    if(len(classic_candle) == 2):

        open = (classic_candle[0][CANDLE_OPEN_PRICE] + classic_candle[0][CANDLE_CLOSE_PRICE])/2
        close = (classic_candle[1][CANDLE_OPEN_PRICE] + classic_candle[1][CANDLE_CLOSE_PRICE] + classic_candle[1][CANDLE_LOW_PRICE] + classic_candle[1][CANDLE_HIGH_PRICE])/4
        candle = [classic_candle[1][CANDLE_START_TIME], open, close, classic_candle[1][CANDLE_HIGH_PRICE], classic_candle[1][CANDLE_LOW_PRICE], classic_candle[1][CANDLE_TRANSACTION_VOLUME], classic_candle[1][CANDLE_TRANSACTION_AMOUNT], classic_candle[1][CANDLE_TIME]]
        if(len(heikin_candle) == 0):
            heikin_candle.append(candle)
        elif(candle[CANDLE_START_TIME] == heikin_candle[-1][CANDLE_START_TIME]):
            heikin_candle[-1] = candle
        else:
            heikin_candle.append(candle)
            if(len(heikin_candle) > maximum_size_heikin_candle_list):
                heikin_candle.pop(0)

        if(1 == 1):
            print('heikin_candle')
            #print(len(heikin_candle))
            print(heikin_candle[-1])
            #print(heikin_candle[-2])
            #print(heikin_candle[-3])
            print('--------------------')
            print('')


def init_candle_array():
    print('START_INIT')
    path = '/api/v1/market/candles?type=1min&symbol=' + sub + '&startAt=' + str(int(msg_list[-1][CANDLE_START_TIME]) - (maximum_size_heikin_candle_list * 60)) + '&endAt=' + msg_list[-1][CANDLE_START_TIME]
    r = requests.get(base_url+path)
    candle = r.json()
    for i in range((len(candle['data'])-1), 0, -1):
        open = (float(candle['data'][i][CANDLE_OPEN_PRICE]) + float(candle['data'][i][CANDLE_CLOSE_PRICE]))/2
        close = (float(candle['data'][i-1][CANDLE_OPEN_PRICE]) + float(candle['data'][i-1][CANDLE_CLOSE_PRICE]) + float(candle['data'][i-1][CANDLE_LOW_PRICE]) + float(candle['data'][i-1][CANDLE_HIGH_PRICE]))/4
        #No time
        heikin = [candle['data'][i-1][CANDLE_START_TIME], open, close, float(candle['data'][i-1][CANDLE_HIGH_PRICE]), float(candle['data'][i-1][CANDLE_LOW_PRICE]), candle['data'][i-1][CANDLE_TRANSACTION_VOLUME], candle['data'][i-1][CANDLE_TRANSACTION_AMOUNT]]
        heikin_candle.append(heikin)
    print('STOP_INIT')
    

async def main():
    global loop

    # callback function that receives messages from the socket
    async def handle_evt(msg):

        if msg['topic'] == '/market/candles:' + sub + '_1hour':
            msg_list.append([msg["data"]["candles"][CANDLE_START_TIME], float(msg["data"]["candles"][CANDLE_OPEN_PRICE]), float(msg["data"]["candles"][CANDLE_CLOSE_PRICE]), float(msg["data"]["candles"][CANDLE_HIGH_PRICE]), float(msg["data"]["candles"][CANDLE_LOW_PRICE]), msg["data"]["candles"][CANDLE_TRANSACTION_VOLUME], msg["data"]["candles"][CANDLE_TRANSACTION_AMOUNT], msg["data"]["time"]])
            print(msg_list[-1])

            sort_classic_candle()

            compute_heikin()

            if(len(msg_list) == 2):
                msg_list.pop(0)
                

            
            

    client = Client(api_key, api_secret, api_passphrase)

    ksm = await KucoinSocketManager.create(loop, client, handle_evt)

    # for private topics such as '/account/balance' pass private=True
    #ksm_private = await KucoinSocketManager.create(loop, client, handle_evt, private=True)
    await ksm.subscribe('/market/candles:' + sub + '_1min')

    while True:
        print("sleeping to keep loop open")
        await asyncio.sleep(20, loop=loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

