import numpy as np
import pandas as pd
import requests
import json
from requests.api import get


def trendline(data, order=1):
    coeffs = np.polyfit(data.index.values, list(data), order)
    slope = coeffs[-2]
    return float(slope)

# Return slope
def trend(data):
    # check if values are exactly same
    if (len(set(data))) <= 1:
        slope = 0
        print(0)
    else:
        df = pd.DataFrame({'ticker': data})

    slope = trendline(df['ticker'])
    # print(slope)
    return slope

def trendBot(vlrange):
    url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=5m"
    r = requests.get(url)
    df = pd.DataFrame(r.json()) 
    eth  = df


    #Sample Dataframe
    ticker = []
    value = 0

    for i in reversed(range(int(vlrange))):
        val = 499 - i # last six periods (5 minutes each, total 30 minutes)
        value = float(eth[4][val])
        ticker.append(value)
    print(ticker)

    return trend(ticker)

# print(trendBot(12))