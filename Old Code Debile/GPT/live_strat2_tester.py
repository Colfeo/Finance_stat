import asyncio
from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager
import requests
import json
import pandas as pd
from datetime import datetime
import numpy as np

#Heure donnee en UTC

sub = 'XMR-USDT'
base_url = 'https://api.kucoin.com'

api_key = '<api_key>'
api_secret = '<api_secret>'
api_passphrase = '<api_passphrase>'

TIME = 0
OPEN = 1
CLOSE = 2
HIGH = 3
LOW = 4
VOLUME = 5
TURNOVER = 6


msg_list = []
classic_candle = []
#1440 = 24h
maximum_size_heikin_candle_list = 1440
maximum_size_classic_candle_list = 1440
maximum_size_msg_list = 2
INIT = False
heikin_candle = []

def sort_classic_candle(msg):
    global classic_candle
    if(msg[-1][TIME] == msg[-2][TIME]):
        classic_candle[-1] = msg[-1]
    
    else:
        classic_candle.append(msg[-1])
    
    if(len(classic_candle)>maximum_size_classic_candle_list):
        for i in range(len(classic_candle)-maximum_size_classic_candle_list):
            classic_candle.pop(0)
  
    if(1 == 0):
        print('classic_candle')
        print(classic_candle[-1])
        print(classic_candle[-2])
        print(classic_candle[-3])
        print('----------------------------------------')
    
def sort_heikin_candle(msg):
    global heikin_candle

    if(msg[-1][TIME] == msg[-2][TIME]):
        heikin_candle[-1] = compute_heikin(msg[-1])

    else:
        heikin_candle.append(compute_heikin(msg[-1]))
    
    if(len(heikin_candle)>maximum_size_heikin_candle_list):
        for i in range(len(heikin_candle)-maximum_size_heikin_candle_list):
            heikin_candle.pop(0)

    if(1 == 0):
        print('heikin_candle')
        #print(len(heikin_candle))
        print(heikin_candle[-1])
        print(heikin_candle[-2])
        #print(heikin_candle[-3])
        print('----------------------------------------')

def compute_classic(data):
    global classic_candle
    i = len(classic_candle)
    classic_candle.append([data[TIME], data[OPEN], data[CLOSE], data[HIGH], data[LOW], data[VOLUME], data[TURNOVER]])

def compute_heikin(data):
    global heikin_candle
    i = len(heikin_candle)
    if(i != 0):
        #Open parfois bizzare
        h_open = (heikin_candle[-1][OPEN] + heikin_candle[-1][CLOSE])/2.0
        h_close = (data[OPEN] + data[HIGH] + data[LOW] + data[CLOSE])/4.0
        h_high = max(data[HIGH], h_open, h_close)
        h_low = min(data[LOW], h_open, h_close)
        return [data[TIME], h_open, h_close, h_high, h_low, data[VOLUME], data[TURNOVER]]
    else:
        h_open = (data[OPEN] + data[CLOSE])/2.0
        h_close = (data[OPEN] + data[HIGH] + data[LOW] + data[CLOSE])/4.0
        h_high = max(data[HIGH], h_open, h_close)
        h_low = min(data[LOW], h_open, h_close)
        return [data[TIME], h_open, h_close, h_high, h_low, data[VOLUME], data[TURNOVER]]

def init_candle_array():
    global INIT
    global msg_list
    global classic_candle
    global heikin_candle
    if(INIT == False and len(msg_list) == 2):
        if(msg_list[-1][TIME] != msg_list[-2][TIME]):
            print('START_INIT')
            path = f"/api/v1/market/candles?type=1min&symbol={sub}&startAt={str(int(msg_list[-1][TIME]) - (maximum_size_heikin_candle_list * 60))}&endAt={msg_list[-1][TIME]}"
            while(True):
                response = requests.get(base_url + path)
                if(str(response) == "<Response [200]>"):
                    break
                else:
                    print("HTTP ERROR")

            candle = response.json()
            candle = candle['data']
            for i in range(len(candle)-1, -1, -1):
                buf = [int(candle[i][TIME]), float(candle[i][OPEN]), float(candle[i][CLOSE]), float(candle[i][HIGH]), float(candle[i][LOW]), float(candle[i][VOLUME]), float(candle[i][TURNOVER])]
                compute_classic(buf)
                heikin_candle.append(compute_heikin(buf))

                times.append(int(candle[i][TIME]))

                compute_indicators()

            INIT = True
            print('STOP_INIT')
            print('--------------------------------------------------------------------------------')
            print('--------------------------------------------------------------------------------')
            print('--------------------------------------------------------------------------------')
            print('--------------------------------------------------------------------------------')
            print('--------------------------------------------------------------------------------')

            if(1 == 0):
                print('heikin_candle_end_init')
                #print(len(heikin_candle))
                print(heikin_candle[-1])
                print(heikin_candle[-2])
                print(heikin_candle[-3])
                print('----------------------------------------')

            if(1 == 0):
                data = [times, ema_25, sma_25, sma_m_sum_25, rsi_14, rsi_u_14, rsi_d_14, stoch_rsi_14, sma_stoch_14, stoch_m]
                a = np.array(data)
                a = np.transpose(a)
                dt = pd.DataFrame(a, columns=['time', 'ema_25', 'sma_25', 'sma_m_sum_25', 'rsi_14', 'rsi_u_14', 'rsi_d_14', 'stoch_rsi_14', 'sma_stoch_14', 'stoch_m'])
                dt.to_excel("live_rsi_data.xlsx", index=False)
                b = pd.DataFrame(heikin_candle)
                b.to_excel("live_data_candle.xlsx", index=False)

def sma(source, length, type):
    i = len(source) - 1
    sum = 0.0
    for j in range(length):
        if((i-j) < 0):
            return source[i - j][type]

        sum = sum + source[i - j][type] / length
    return sum

def sma_2D(source, length):
    i = len(source) - 1
    sum = 0.0
    for j in range(length):
        if((i-j) < 0):
            return source[i - j]

        sum = sum + source[i - j] / length
    return sum

def ema(ema_, source, length):
    alpha = 2 / (length + 1)
    ema = 0
    if(len(ema_) == 0):
        ema = source
    else:
        ema = (1 - alpha) * ema_[-1] + alpha * source
    return ema

def append2_max(array, elem):
    array.append(elem)
    len_ = len(array)
    if(len_>maximum_size_indicators):
        for i in range(len_-maximum_size_indicators):
            array.pop(0)

def m_rate_candle(source, type):
    i = len(source) - 1
    if(i == 0):
        return 1
    return source[i][type]/source[i-1][type]

def m_rate_2DArray(source, type):
    i = len(source) - 1
    if(i == 0):
        return 1
    return source[i]/source[i-1]

def rsi(u, d, source, length, type):
    i = len(source) - 1
    rma_u = rma(u, max(source[i][type] - source[i-1][type], 0), length)
    rma_d = rma(d, max(source[i-1][type] - source[i][type], 0), length)
    #u.append(rma_u)
    #d.append(rma_d)
    append2_max(u, rma_u)
    append2_max(d, rma_d)

    if(i<length): return 50
    rs = rma_u / rma_d
    res = 100 - (100 / (1 + rs))
    return res

def rma(rma_, source, length):
    alpha = 1 / length
    rma = 0
    if(len(rma_) == 0):
        rma = source
    else:
        rma = (1 - alpha) * rma_[-1] + alpha * source
    return rma

def stoch(stoch_, rsi, length):
    i = len(rsi) - 1
    if i <= length:
        return 50
    den = (max(rsi[i-length:i]) - min(rsi[i-length:i]))
    if(den == 0):
        return stoch_[i-1]
    stoch = 100 * (rsi[i] - min(rsi[i-length:i])) / den
    if(stoch > 100): stoch = 100
    if(stoch < 0): stoch = 0
    return stoch

def delta_2D(source):
    i = len(source) - 1
    if(i == 0):
        return 0
    return source[i] - source[i-1]

def compare_N_previous_Values_to_Treshold(length, source, type, threshold):
    if(len(source)<(length + 1)):
        return False
    for j in range(length):
        if(type == "Above"):
            if(source[-1*(2+j)] <= threshold):
                return False
        if(type == "Under"):
            if(source[-1*(2+j)] >= threshold):
                return False
    return True

def print_info_trade_start2():
    global Long_total_percentage
    global Short_total_percentage
    global total_percentage
    global last_trade_percentage
    print("TRADE PERCENTAGE : " + str(last_trade_percentage))
    print("Long percentage : " + str(Long_total_percentage))
    print("Short percentage : " + str(Short_total_percentage))
    print("TOTAL percentage : " + str(total_percentage))
    print('--------------------------------------------------------------------------------')
    print('--------------------------------------------------------------------------------')

def strat2_StochRsiM(sma_m, stoch_delta, stoch_rsi, source):
    i = len(source) - 1
    global last_trade_time
    global Long_total_percentage
    global Short_total_percentage
    global trade_strat2
    global total_percentage
    global last_trade_percentage
    if(trade_strat2 == "Aucun"):
        #Attend que le systeme soit stable
        if(i>50):  
            #Marche haussier
            if(sma_m[i] > 1):
                #Delta dans le stoch rsi avec pente elevee et stoch rsi > 20
                if(stoch_delta[i] >= 10 and stoch_rsi[i] >= 20):
                    #Les 5 derniere minutes de stoch rsi sont inférieure a 20
                    if(compare_N_previous_Values_to_Treshold(5, stoch_rsi, "Under", 20) == True):
                        print("BUY Long " + str(pd.to_datetime(source[i][TIME], unit='s')) + " Price : " + str(source[i][CLOSE]) + " Slope sma : " + str(sma_m[i]))
                        #BUY_Long.append(source[i][CLOSE])
                        append2_max(BUY_Long, source[i][CLOSE])
                        trade_strat2 = "Long"
                        last_trade_time = source[i][TIME]
                        
            #Marche baisier
            if(sma_m[i] < 1):
                #Delta dans le stoch rsi avec pente faible
                if(stoch_delta[i] >= -10 and stoch_rsi[i] <= 20):
                    #Les 5 derniere minutes de stoch rsi sont superieure a 20
                    if(compare_N_previous_Values_to_Treshold(5, stoch_rsi, "Above", 80) == True):
                        
                        print("BUY Short " + str(pd.to_datetime(source[i][TIME], unit='s')) + " Price : " + str(source[i][CLOSE]) + " Slope sma : " + str(sma_m[i]))
                        #BUY_Short.append(source[i][CLOSE])
                        append2_max(BUY_Short, source[i][CLOSE])
                        trade_strat2 = "Short"
                        last_trade_time = source[i][TIME]

    if(trade_strat2 == "Long"):
        if(stoch_delta[i] < 0 and last_trade_time != source[i][CLOSE]):
            
            print("SELL Long " + str(pd.to_datetime(source[i][TIME], unit='s')) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
            #SELL_Long.append(source[i][CLOSE])
            append2_max(SELL_Long, source[i][CLOSE])
            trade_strat2 = "Aucun"
            last_trade_percentage = 100 * (SELL_Long[-1] - BUY_Long[-1])/BUY_Long[-1]
            Long_total_percentage += last_trade_percentage
            total_percentage += last_trade_percentage
            print_info_trade_start2()


    if(trade_strat2 == "Short"):
        if(stoch_delta[i] > 0 and last_trade_time != source[i][CLOSE]):
            
            print("SELL Short " + str(pd.to_datetime(source[i][TIME], unit='s')) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
            #SELL_Short.append(source[i][CLOSE])
            append2_max(SELL_Short, source[i][CLOSE])
            trade_strat2 = "Aucun"
            last_trade_percentage = 100 * (BUY_Short[-1] - SELL_Short[-1])/SELL_Short[-1]
            Short_total_percentage += last_trade_percentage
            total_percentage += last_trade_percentage
            print_info_trade_start2()

def compute_indicators():

    append2_max(sma_25, sma(heikin_candle,  25, CLOSE))
    append2_max(ema_25, ema(ema_25, heikin_candle[-1][CLOSE], 25))
    append2_max(sum_25, (ema_25[-1]+sma_25[-1])/2)
    append2_max(sma_m_sum_25, m_rate_2DArray(sum_25, CLOSE))
    append2_max(rsi_14, rsi(rsi_u_14, rsi_d_14, heikin_candle, 18, CLOSE))
    append2_max(stoch_rsi_14, stoch(stoch_rsi_14, rsi_14, 18))
    append2_max(sma_stoch_14, sma_2D(stoch_rsi_14, 4))
    append2_max(stoch_m, delta_2D(sma_stoch_14))

    strat2_StochRsiM(sma_m_sum_25, stoch_m, sma_stoch_14, heikin_candle)

times = []
wait_sleep_print = 0

maximum_size_indicators = 1440
ema_25 = []
sma_25 = []
sum_25 = []
sma_m_sum_25 = []

rma_14 = []
rsi_14 = []
rsi_u_14 = []
rsi_d_14 = []
stoch_rsi_14 = []
sma_stoch_14 = []
stoch_m = []
trade_strat2 = "Aucun"

Long_total_percentage = 0
Short_total_percentage = 0
total_percentage = 0
last_trade_percentage = 0
BUY_Long = []
SELL_Long = []
BUY_Short = []
SELL_Short = []
last_trade_time = 0

async def main():
    global loop

    # callback function that receives messages from the socket
    async def handle_evt(msg):

        if msg['topic'] == '/market/candles:' + sub + '_1min':
            #Recover fresh data
            msg_list.append([int(msg["data"]["candles"][TIME]), float(msg["data"]["candles"][OPEN]), float(msg["data"]["candles"][CLOSE]), float(msg["data"]["candles"][HIGH]), float(msg["data"]["candles"][LOW]), float(msg["data"]["candles"][VOLUME]), float(msg["data"]["candles"][TURNOVER])])
            if(len(msg_list) > maximum_size_msg_list):
                msg_list.pop(0)
            if(INIT == False):
                print("MSG :")
                print(msg_list[-1])
                print("----------------------------------------")


            #Initialise les 2 candles arrays
            init_candle_array()

            if(INIT == True):

                #Sort classic, sort and compute heikin
                sort_classic_candle(msg_list)
                sort_heikin_candle(msg_list)

                #Compute indicators
                compute_indicators()
                #print(len(stoch_m))
                
                #Compute strategies
                strat2_StochRsiM(sma_m_sum_25, stoch_m, sma_stoch_14, heikin_candle)


                

            
            

    client = Client(api_key, api_secret, api_passphrase)

    ksm = await KucoinSocketManager.create(loop, client, handle_evt)

    # for private topics such as '/account/balance' pass private=True
    #ksm_private = await KucoinSocketManager.create(loop, client, handle_evt, private=True)
    await ksm.subscribe('/market/candles:' + sub + '_1min')

    while True:

        global wait_sleep_print
        global INIT
        wait_sleep_print += 1
        # 1min = 3
        if(wait_sleep_print >= 3 and INIT == True):
            print(str(heikin_candle[-2]))
            wait_sleep_print = 0
        #print("sleeping to keep loop open")
        await asyncio.sleep(20, loop=loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

