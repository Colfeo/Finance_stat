import requests
import pandas as pd
from datetime import datetime

# Fonction pour récupérer les données sur le prix du Bitcoin à partir de l'API Kucoin
def get_bitcoin_price(start_timestamp, end_timestamp):
  # Appeler l'API avec les paramètres de date de début et de fin
  url = f"https://api.kucoin.com/v1/open/kline?symbol=BTC-USDT&type=1min&startTime={start_timestamp}&endTime={end_timestamp}"
  headers = {
    "KC-API-KEY": "YOUR_API_KEY",
    "KC-API-SECRET": "YOUR_API_SECRET",
  }
  response = requests.get(url, headers=headers)
  data = response.json()

  # Charger les données dans un dataframe pandas
  df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"])

  # Formater la colonne timestamp en date
  df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

  # Renvoyer le dataframe
  return df

# Appeler la fonction avec les timestamps de début et de fin souhaités
start_timestamp = int(datetime(2018, 1, 1).timestamp() * 1000)
end_timestamp = int(datetime(2018, 1, 2).timestamp() * 1000)
df = get_bitcoin_price(start_timestamp, end_timestamp)

# Afficher les premières lignes du dataframe
print(df.head())

# Enregistrer le dataframe dans un fichier Excel
df.to_excel("bitcoin_prices.xlsx", index=False)
