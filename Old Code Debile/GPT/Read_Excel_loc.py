import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from datetime import datetime

TIME = 0
OPEN = 1
CLOSE = 2
HIGH= 3
LOW = 4
VOLUME = 5
TURNOVER = 6

# read the Excel file
df = pd.read_excel('test_prices.xlsx', sheet_name='Sheet1')
#df[0] =  pd.to_datetime(df[0], unit='s')
#print(df['time'])

# get the data from the DataFrame
data = df.values.tolist()
data = data[::-1]
data = np.array(data)
#print(data[:, 0])

#Heikin candle compute
heikin_candle = []
def compute_heikin(i):
    if(i != 0):
        h_open = (heikin_candle[i-1][OPEN] + heikin_candle[i-1][CLOSE])/2.0
        h_close = (data[i][OPEN] + data[i][HIGH] + data[i][LOW] + data[i][CLOSE])/4.0
        h_high = max(data[i][HIGH], h_open, h_close)
        h_low = min(data[i][LOW], h_open, h_close)
        heikin_candle.append([data[i][TIME], h_open, h_close, h_high, h_low, data[i][VOLUME], data[i][TURNOVER]])
    else:
        h_open = (data[i][OPEN] + data[i][CLOSE])/2.0
        h_close = (data[i][OPEN] + data[i][HIGH] + data[i][LOW] + data[i][CLOSE])/4.0
        h_high = max(data[i][HIGH], h_open, h_close)
        h_low = min(data[i][LOW], h_open, h_close)
        heikin_candle.append([data[i][TIME], h_open, h_close, h_high, h_low, data[i][VOLUME], data[i][TURNOVER]])

def sma(source, i, length, type):
    sum = 0.0
    for j in range(length):
        if((i-j) < 0):
            return source[i - j][type]

        sum = sum + source[i - j][type] / length
    return sum

def sma_2D(source, i, length):
    sum = 0.0
    for j in range(length):
        if((i-j) < 0):
            return source[i - j]

        sum = sum + source[i - j] / length
    return sum

def m_rate_candle(source, i, type):
    if(i == 0):
        return 1
    return source[i][type]/source[i-1][type]

def m_rate_2DArray(source, i, type):
    if(i == 0):
        return 1
    return source[i]/source[i-1]

def delta_2D(source, i):
    if(i == 0):
        return 0
    return source[i] - source[i-1]

def stochastic_rsi(source, period, type, i):
    global stoch_rsi
    
    if len(source) < 1:
        return
    
    # Calculate the next RSI value
    price = source[i][type]
    delta = price - source[i-1][type]
    if delta > 0:
        u = delta
        d = 0
    else:
        u = 0
        d = -delta
    u = (source[i][type] * (period-1) + u) / period
    d = (source[i][type] * (period-1) + d) / period
    if u != 0:
        rs = u / d
    else:
        rs = 0
    rsi = 100 - (100 / (1 + rs))
    
    # Calculate and update the stochastic RSI value
    if rsi > stoch_rsi[-1]:
        stoch_rsi.append((rsi - stoch_rsi[-1]) / (100 - stoch_rsi[-1]))
    else:
        stoch_rsi.append((stoch_rsi[-1] - rsi) / stoch_rsi[-1])

def rma(rma_, source, length):
    #For EMA
    #alpha = 2 / (length + 1)
    alpha = 1 / length
    rma = 0
    if(len(rma_) == 0):
        rma = source
    else:
        rma = (1 - alpha) * rma_[-1] + alpha * source
    return rma

def ema(ema_, source, length):
    alpha = 2 / (length + 1)
    ema = 0
    if(len(ema_) == 0):
        ema = source
    else:
        ema = (1 - alpha) * ema_[-1] + alpha * source
    return ema

def summ(x, length, i):
    sum = 0
    for j in range(length):
        sum += x[i - j]
    return sum

def rsi(u, d, source, i, length, type):
    #u.append(max(source[i][type] - source[i-1][type], 0))
    #d.append(max(source[i-1][type] - source[i][type], 0))
    rma_u = rma(u, max(source[i][type] - source[i-1][type], 0), length)
    rma_d = rma(d, max(source[i-1][type] - source[i][type], 0), length)
    u.append(rma_u)
    d.append(rma_d)

    if(i<length): return 50
    #rs = summ(u, length, i) / summ(d, length, i)
    rs = rma_u / rma_d
    res = 100 - (100 / (1 + rs))
    if(res > 100): res = 100
    if(res < 0): res = 0
    return res

def stoch(stoch_, rsi, length, i):
    
    if i <= length:
        return 50
    den = (max(rsi[i-length:i]) - min(rsi[i-length:i]))
    if(den == 0):
        return stoch_[i-1]
    stoch = 100 * (rsi[i] - min(rsi[i-length:i])) / den
    if(stoch > 100): stoch = 100
    if(stoch < 0): stoch = 0
    return stoch

def strat1_m_rate(source, i, length, rate):
    for j in range(length):
        if((i - j - 1) < 0):
            return
        if(rate[i - j - 1] > 1):
            return
    if(rate[i] > 1):
        print("BUY " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]))  

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

def strat2_StochRsiM(sma_m, stoch_delta, stoch_rsi, i, source):
    global Long_total_percentage
    global Short_total_percentage
    global trade_strat2
    global total_percentage
    global last_trade_percentage
    if(trade_strat2 == "Aucun"):
        #Attend que le systeme soit stables
        if(i>50):  
            #Marche haussier
            if(sma_m[i] > 1):
                #Delta dans le stoch rsi avec pente elevee et stoch rsi > 20
                if(stoch_delta[i] >= 10 and stoch_rsi[i] >= 20):
                    #Les 5 derniere minutes de stoch rsi sont inférieure a 20
                    if(compare_N_previous_Values_to_Treshold(5, stoch_rsi, "Under", 20) == True):
                        
                        print("BUY Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Slope sma : " + str(sma_m[i]))
                        BUY_Long.append(source[i][CLOSE])
                        trade_strat2 = "Long"
                        
            #Marche baisier
            if(sma_m[i] < 1):
                #Delta dans le stoch rsi avec pente faible
                if(stoch_delta[i] >= -10 and stoch_rsi[i] <= 80):
                    #Les 5 derniere minutes de stoch rsi sont superieure a 20
                    if(compare_N_previous_Values_to_Treshold(5, stoch_rsi, "Above", 80) == True):
                        
                        print("BUY Short " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Slope sma : " + str(sma_m[i]))
                        BUY_Short.append(source[i][CLOSE])
                        trade_strat2 = "Short"

    if(trade_strat2 == "Long"):
        if(stoch_delta[i] < 0):
            
            print("SELL Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
            SELL_Long.append(source[i][CLOSE])
            trade_strat2 = "Aucun"
            last_trade_percentage = 100 * (SELL_Long[-1] - BUY_Long[-1])/BUY_Long[-1]
            Long_total_percentage += last_trade_percentage
            total_percentage += last_trade_percentage
            print_info_trade_start2()


    if(trade_strat2 == "Short"):
        if(stoch_delta[i] > 0):
            
            print("SELL Short " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
            SELL_Short.append(source[i][CLOSE])
            trade_strat2 = "Aucun"
            last_trade_percentage = 100 * (BUY_Short[-1] - SELL_Short[-1])/SELL_Short[-1]
            Short_total_percentage += last_trade_percentage
            total_percentage += last_trade_percentage
            print_info_trade_start2()

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

def strat3_StochRsiM(sma_m, stoch_delta, stoch_rsi, i, source):
    global Long_total_percentage
    global Short_total_percentage
    global trade_strat2
    global total_percentage
    global last_trade_percentage
    if(trade_strat2 == "Aucun"):
        #Attend que le systeme soit stables
        if(i>50):  
            #Delta dans le stoch rsi avec pente elevee et stoch rsi > 20
            if(stoch_delta[i] >= 10 and stoch_rsi[i] >= 20 and stoch_rsi[i] <= 40 and ((source[i][LOW]) >= (source[i][OPEN]))):
            #if(stoch_rsi[i] >= 20):
                #Les 5 derniere minutes de stoch rsi sont inférieure a 20
                if(compare_N_previous_Values_to_Treshold(5, stoch_rsi, "Under", 20) == True):
                    
                    print("BUY Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " S_RSI : " + str(stoch_rsi[i]) + " S_Delta : " + str(stoch_delta[i]))
                    BUY_Long.append(source[i][CLOSE])
                    trade_strat2 = "Long"
                        
            #Delta dans le stoch rsi avec pente faible
            #if(stoch_delta[i] >= -10 and stoch_rsi[i] <= 20):
            #    #Les 5 derniere minutes de stoch rsi sont superieure a 20
            #    if(compare_N_previous_Values_to_Treshold(5, stoch_rsi, "Above", 20) == True):
            #        
            #        print("BUY Short " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Slope sma : " + str(sma_m[i]))
            #        BUY_Short.append(source[i][CLOSE])
            #        trade_strat2 = "Short"

    if(trade_strat2 == "Long"):
        if(stoch_rsi[i] >= 90):
            if(stoch_delta[i] <= -5):

                print("SELL Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
                SELL_Long.append(source[i][CLOSE])
                trade_strat2 = "Aucun"
                last_trade_percentage = 100 * (SELL_Long[-1] - BUY_Long[-1])/BUY_Long[-1]
                Long_total_percentage += last_trade_percentage
                total_percentage += last_trade_percentage
                print_info_trade_start2()
        else:
            if(stoch_delta[i] < 0):

                print("SELL Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
                SELL_Long.append(source[i][CLOSE])
                trade_strat2 = "Aucun"
                last_trade_percentage = 100 * (SELL_Long[-1] - BUY_Long[-1])/BUY_Long[-1]
                Long_total_percentage += last_trade_percentage
                total_percentage += last_trade_percentage
                print_info_trade_start2()


    if(trade_strat2 == "Short"):
        if(stoch_rsi[i] <= 10):
            if(stoch_delta[i] >= 10):

                print("SELL Short " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
                SELL_Short.append(source[i][CLOSE])
                trade_strat2 = "Aucun"
                last_trade_percentage = 100 * (BUY_Short[-1] - SELL_Short[-1])/SELL_Short[-1]
                Short_total_percentage += last_trade_percentage
                total_percentage += last_trade_percentage
                print_info_trade_start2()
        else:
            if(stoch_delta[i] > 0):

                print("SELL Short " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
                SELL_Short.append(source[i][CLOSE])
                trade_strat2 = "Aucun"
                last_trade_percentage = 100 * (BUY_Short[-1] - SELL_Short[-1])/SELL_Short[-1]
                Short_total_percentage += last_trade_percentage
                total_percentage += last_trade_percentage
                print_info_trade_start2()

def strat4_StochRsiM(sma_m, stoch_delta, stoch_rsi, i, source):
    global Long_total_percentage
    global Short_total_percentage
    global trade_strat2
    global total_percentage
    global last_trade_percentage
    global trade_MAX
    if(trade_strat2 == "Aucun"):
        #Attend que le systeme soit stables
        if(i>50):  
            #Delta dans le stoch rsi avec pente elevee et stoch rsi > 20
            if(stoch_delta[i] >= 10 and stoch_rsi[i] >= 15 and stoch_rsi[i] <= 40):
            #if(stoch_rsi[i] >= 20):
                #Les 5 derniere minutes de stoch rsi sont inférieure a 20
                if((compare_N_previous_Values_to_Treshold(2, stoch_rsi, "Under", 10) == True)):# and (compare_N_previous_Values_to_Treshold(4, stoch_delta, "Above", -3) == True)):
                    
                    print("BUY Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " S_RSI : " + str(stoch_rsi[i]) + " S_Delta : " + str(stoch_delta[i]))
                    BUY_Long.append(source[i][CLOSE])
                    trade_MAX = max(trade_MAX, source[i][CLOSE])
                    trade_strat2 = "Long"
                        

    if(trade_strat2 == "Long"):
        trade_MAX = max(trade_MAX, source[i][CLOSE])
        #print((100 * (source[i][CLOSE] - trade_MAX)/trade_MAX))
        print(trade_MAX)
        if((100 * (source[i][CLOSE] - BUY_Long[-1])/BUY_Long[-1]) <= -0.5):
            
            print("SELL Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
            SELL_Long.append(source[i][CLOSE])
            trade_strat2 = "Aucun"
            trade_MAX = 0
            last_trade_percentage = 100 * (SELL_Long[-1] - BUY_Long[-1])/BUY_Long[-1]
            Long_total_percentage += last_trade_percentage
            total_percentage += last_trade_percentage
            print_info_trade_start2()
        
        elif((100 * (source[i][CLOSE] - trade_MAX)/trade_MAX) <= -0.2):
            
            print("SELL Long " + str(source[i][TIME]) + " Price : " + str(source[i][CLOSE]) + " Delta stoch RSI : " + str(stoch_delta[i]))
            SELL_Long.append(source[i][CLOSE])
            trade_strat2 = "Aucun"
            trade_MAX = 0
            last_trade_percentage = 100 * (SELL_Long[-1] - BUY_Long[-1])/BUY_Long[-1]
            Long_total_percentage += last_trade_percentage
            total_percentage += last_trade_percentage
            print_info_trade_start2()

def rsi_(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n - 1) + upval)/n
        down = (down*(n - 1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)

    return rsi

#ef stochrsi(prices, n=14, k=3, d=3):
#   rsi = rsi_(prices, n)
#   stoch_k = np.zeros_like(rsi)
#   stoch_d = np.zeros_like(rsi)
#   for i in range(len(prices)):
#       if i >= n:
#           rsi_range = rsi[i-n+1:i+1]
#           stoch_k[i] = (rsi[i] - np.min(rsi_range)) / (np.max(rsi_range) - np.min(rsi_range)) * 100
#           if i > n:
#               stoch_d[i] = stoch_k[i-(d-1):i+1].mean()
#   return stoch_d
#
def StochRSI(series, period=14, smoothK=3, smoothD=3):
    # Calculate RSI 
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period-1]] = np.mean( ups[:period] ) #first value is sum of avg gains
    ups = ups.drop(ups.index[:(period-1)])
    downs[downs.index[period-1]] = np.mean( downs[:period] ) #first value is sum of avg losses
    downs = downs.drop(downs.index[:(period-1)])
    rs = ups.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
         downs.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() 
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI 
    stochrsi  = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.rolling(smoothK).mean()
    stochrsi_D = stochrsi_K.rolling(smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D

#MAIN LOOP
Long_total_percentage = 0
Short_total_percentage = 0
total_percentage = 0
last_trade_percentage = 0
BUY_Long = []
SELL_Long = []
BUY_Short = []
SELL_Short = []
trade_MAX = 0

volume = []
vol_sma_25 = []
vol_sma_50 = []


sma_7 = []
sma_49 = []
m_rate_1 = [] 
m_rate_sma_7 = []
ema_25 = []
sma_25 = []
sum_25 = []

rma_14 = []
rsi_14 = []
rsi_u_14 = []
rsi_d_14 = []
stoch_rsi_14 = []
sma_stoch_14 = []

sma_m_sum_25 = []
stoch_m = []
trade_strat2 = "Aucun"

for i in range(len(data)):


    #volume.append(data[i][VOLUME])
    #Compute candle
    compute_heikin(i)
    #vol_sma_25.append(sma_2D(volume, i, 25))
    #vol_sma_50.append(sma_2D(volume, i, 50))

    #Compute indicators
    sma_7.append(sma(heikin_candle, i, 7, CLOSE))
    sma_49.append(sma(heikin_candle, i, 49, CLOSE))
    sma_25.append(sma(heikin_candle, i, 25, CLOSE))
    ema_25.append(ema(ema_25, heikin_candle[i][CLOSE], 25))
    sum_25.append((ema_25[i]+sma_25[i])/2)
    sma_m_sum_25.append(m_rate_2DArray(sum_25, i, CLOSE))
    m_rate_1.append(m_rate_candle(heikin_candle, i, CLOSE))
    m_rate_sma_7.append(m_rate_2DArray(sma_7, i, CLOSE))
    #RSI(heikin_candle, 14, i, CLOSE, RSI_14)

    #rma_14.append(rma(rma_14, heikin_candle[i][CLOSE], 14))
    #rsi_14.append(rsi(rma_14, heikin_candle, i, 14, CLOSE))
    rsi_14.append(rsi(rsi_u_14, rsi_d_14, heikin_candle, i, 14, CLOSE))
    stoch_rsi_14.append(stoch(stoch_rsi_14, rsi_14, 14, i))
    sma_stoch_14.append(sma_2D(stoch_rsi_14, i, 3))
    stoch_m.append(delta_2D(sma_stoch_14, i))
    #stoch_rsi.append(stochastic_rsi(heikin_candle, i, CLOSE, 14))
    
    #Compute strategies
    #strat1_m_rate(heikin_candle, i, 5, m_rate_1)
    #strat1_m_rate(heikin_candle, i, 3, m_rate_sma_7)
    #strat2_StochRsiM(sma_m_sum_25, stoch_m, sma_stoch_14, i, heikin_candle)
    #strat3_StochRsiM(sma_m_sum_25, stoch_m, sma_stoch_14, i, heikin_candle)
    #strat4_StochRsiM(sma_m_sum_25, stoch_m, sma_stoch_14, i, heikin_candle)

    #Treat trade


s = pd.DataFrame(heikin_candle)
stochrsi, stochrsi_K, stochrsi_D = StochRSI(s[2], period=14, smoothK=3, smoothD=3)
total_percentage = Long_total_percentage + Short_total_percentage
print("Long percentage : " + str(Long_total_percentage))
print("Short percentage : " + str(Short_total_percentage))
print("TOTAL percentage : " + str(total_percentage))
print("Nbr trade : " + str(len(BUY_Long)))

# PLOTS

# Create a Candlestick trace
trace = go.Candlestick(
    x=data[:, TIME],
    open=data[:, OPEN],
    high=data[:, HIGH],
    low=data[:, LOW],
    close=data[:, CLOSE]
)

heikin_candle = np.array(heikin_candle)
heikin = go.Candlestick(
    x=heikin_candle[:, TIME],
    open=heikin_candle[:, OPEN],
    high=heikin_candle[:, HIGH],
    low=heikin_candle[:, LOW],
    close=heikin_candle[:, CLOSE]
)

#print(stoch_m)
#print(rsi_u_14)
#print(rsi_d_14)

#Excel output
if(1 == 0):
    data = [heikin_candle[:, TIME], ema_25, sma_25, sma_m_sum_25, rsi_14, rsi_u_14, rsi_d_14, stoch_rsi_14, sma_stoch_14, stoch_m]
    a = np.array(data)
    a = np.transpose(a)
    dt = pd.DataFrame(a, columns=['time', 'ema_25', 'sma_25', 'sma_m_sum_25', 'rsi_14', 'rsi_u_14', 'rsi_d_14', 'stoch_rsi_14', 'sma_stoch_14', 'stoch_m'])
    dt.to_excel("rsi_data.xlsx", index=False)
    b = pd.DataFrame(heikin_candle)
    b.to_excel("read_data_candle.xlsx", index=False)

# Create the plot
if(True):
    #plot = go.Figure(data=[trace])
    plot = go.Figure(data=[heikin])

    #plot.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=stochrsi_K, mode='lines', name='sma_7'))
    #plot.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=sma_49, mode='lines', name='sma_49'))
    #plot.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=sma_25, mode='lines', name='sma_25'))
    #plot.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=ema_25, mode='lines', name='ema_25'))
    #plot.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=sum_25, mode='lines', name='sum_25'))
    # Show the plot
    #plot.show()

    #print(stoch_rsi)
    fig = go.Figure()
    #fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=rsi_14, mode='lines', name='rsi_14'))
    #fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=stoch_rsi_14, mode='lines', name='stoch_14'))
    #fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=sma_stoch_14, mode='lines', name='sma_stoch_4'))
    fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=np.ones(len(heikin_candle[:, TIME]))*20, mode='lines', name='20'))
    fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=np.ones(len(heikin_candle[:, TIME]))*80, mode='lines', name='80'))
    fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=sma_stoch_14, mode='lines', name='old'))
    fig.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=stochrsi*100, mode='lines', name='new'))
    fig.show()

    vol = go.Figure()
    #vol.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=s_rsi, mode='lines', name='delta S_RSI'))
    #vol.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=volume, mode='lines', name='volume'))
    #vol.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=vol_sma_25, mode='lines', name='sma'))
    #vol.add_trace(go.Scatter(x=heikin_candle[:, TIME], y=vol_sma_50, mode='lines', name='sma'))
    #vol.show()

