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
    url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1d"
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

#ticker = [3512.53,3496.55,3492.86,3492.6,3498.1,3493.55]
ticker = [3498.1,3493.55,3476.92,3458.84,3461,3451.93]
print(trend(ticker))
#print(trendBot(6))