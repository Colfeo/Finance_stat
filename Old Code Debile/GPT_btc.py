import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests

def plot_candlestick_chart():
  # Récupérer les données de prix du Bitcoin en temps réel à l'aide de l'API CoinDesk
  url = "https://api.coindesk.com/v1/bpi/currentprice.json"
  response = requests.get(url)
  data = response.json()
  prices = data["bpi"]
  time = data["time"]

  # Créer un DataFrame pandas avec les données de prix
  df = pd.DataFrame({
    "Date": time["updated"],
    "Open": prices["USD"]["rate_float"],
    "High": prices["USD"]["rate_float"],
    "Low": prices["USD"]["rate_float"],
    "Close": prices["USD"]["rate_float"]
  })
  df = df.set_index("Date")  # Ajouter cette ligne

  # Tracer le graphique en chandelier du Bitcoin en utilisant Plotly
  fig = px.candlestick(df, x="Date", open="Open", high="High", low="Low", close="Close")
  fig.show()

plot_candlestick_chart()