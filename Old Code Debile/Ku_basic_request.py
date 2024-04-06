import requests
import json
from datetime import datetime

base_url = 'https://api.kucoin.com'
#path = '/api/v1/symbols'
path = '/api/v1/market/candles?type=1min&symbol=BTC-USDT&startAt=1566763297&endAt=1566789757'

r = requests.get(base_url+path)
candle = r.json()
#print(candle['data'][0])
##obj = json.loads(r.json())
#print(obj)
#json_formatted_str = json.dumps(obj, indent=4)
#print(json_formatted_str)

start_timestamp = int(datetime(2018, 1, 1).timestamp())# * 1000)
end_timestamp = int(datetime(2018, 1, 2).timestamp())# * 1000)
#url = f"https://api.kucoin.com/v1/open/kline?symbol=BTC-USDT&type=1min&startTime={start_timestamp}&endTime={end_timestamp}"
url = f"/api/v1/market/candles?type=1min&symbol=BTC-USDT&startAt={start_timestamp}&endAt={end_timestamp}"
#url = f"https://api.kucoin.com/v1/open/kline?symbol=BTC-USDT&type=1min&startTime=1566763297&endTime=1566789757"

response = requests.get(base_url + url)
print(response)
data = response.json()
print(data['data'])
