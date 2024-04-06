import requests
import pandas as pd
from datetime import datetime

base_url = 'https://api.kucoin.com'
i = 0

symbol = "XMR-USDT"
time = "1hour"
start = datetime(2023, 12, 1, 12, 00)
end = datetime(2023, 12, 31, 12, 00)
name = f"{symbol}_{time}_start={start}_end={end}.xlsx"
print(name)
start_timestamp = int(start.timestamp())#1673289720 - (120*60) 
end_timestamp = int(end.timestamp())#1673306760 + (30*60) +recent

# Fonction pour récupérer les données sur le prix du Bitcoin à partir de l'API Kucoin
def get_bitcoin_price(start_timestamp, end_timestamp):
  global i
  # Appeler l'API avec les paramètres de date de début et de fin
  #Type of candlestick patterns: 1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
  url = f"/api/v1/market/candles?type={time}&symbol={symbol}&startAt={start_timestamp}&endAt={end_timestamp}"
  while(True):
    response = requests.get(base_url + url)#, headers=headers)
    #print(response)
    #print(str(response) == "<Response [200]>")
    if(str(response) == "<Response [200]>"):
        break
    else:
        print("HTTP ERROR")

  print(str(i))
  i += 1
  data = response.json()
  #print(data['data'][0])
  # Charger les données dans un dataframe pandas
  #df = pd.DataFrame(data['data'], columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
  df = pd.DataFrame(data['data'])
  #print("start : " + str(start_timestamp))
  #print("end : " + str(end_timestamp))
  #print(str((end_timestamp - start_timestamp)/60))
  #print(df)
  #print("---------------------------------------------------------------------------------------------------")
  #df['time'] = pd.to_datetime(df['time'], unit='s')
  df[0] = pd.to_datetime(df[0], unit='s')
  return df

# Appeler la fonction avec les timestamps de début et de fin souhaités


df = pd.DataFrame()#columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
sum = end_timestamp
while(True):
    if((sum - start_timestamp) > 86400):
        df = pd.concat([df, get_bitcoin_price(sum - 86400, sum)])
        #print(df)
        sum -= 86400
    else:
        df = pd.concat([df, get_bitcoin_price(start_timestamp, sum)])
        break

#df = get_bitcoin_price(start_timestamp, end_timestamp)

# Afficher les premières lignes du dataframe


# Enregistrer le dataframe dans un fichier Excel
#df.to_excel("test_prices.xlsx", index=False)

data = df.values.tolist()
data = data[::-1]
data = pd.DataFrame(data)
data.columns = ['time', 'open', 'close', 'high', 'low', 'volume', 'turnover']

print(data)
data.to_excel("Data_csv/" + name, index=False)
#data.to_excel("test_prices.xlsx", index=False)