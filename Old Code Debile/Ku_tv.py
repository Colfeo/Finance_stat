from tradingview_ta import TA_Handler, Interval, Exchange
#https://tvdb.brianthe.dev/
#class Interval:
#    INTERVAL_1_MINUTE = "1m"
#    INTERVAL_5_MINUTES = "5m"
#    INTERVAL_15_MINUTES = "15m"
#    INTERVAL_30_MINUTES = "30m"
#    INTERVAL_1_HOUR = "1h"
#    INTERVAL_2_HOURS = "2h"
#    INTERVAL_4_HOURS = "4h"
#    INTERVAL_1_DAY = "1d"
#    INTERVAL_1_WEEK = "1W"
#    INTERVAL_1_MONTH = "1M"

tesla = TA_Handler(
    symbol="TSLA",
    screener="america",
    exchange="NASDAQ",
    interval=Interval.INTERVAL_1_DAY
)

xmr_kucoin = TA_Handler(
    symbol="XMRUSDT",
    screener="crypto",
    exchange="KUCOIN",
    interval=Interval.INTERVAL_5_MINUTES
)

print(xmr_kucoin.get_analysis().summary)
# Example output: {"RECOMMENDATION": "BUY", "BUY": 8, "NEUTRAL": 6, "SELL": 3}