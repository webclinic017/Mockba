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
    #print(data)
    # check if values are exactly same
    # Assuming you have the 'data' variable with the necessary data
    df = pd.DataFrame({'ticker': data})  # Create the DataFrame with the 'ticker' column

    if len(df) <= 1:
        slope = 0
        print(0)
    else:
        slope = trendline(df['ticker'])
    # print(slope)
    return slope
    

def trendBot(vlrange, pair, interval):
    url = "https://api.binance.com/api/v3/klines?symbol="+pair+"&interval="+interval
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

    return ticker


# def calculate_trend 0.5% tolerance:
def calculate_trend(market_prices, ma_period, tolerance):
    if len(market_prices) < ma_period:
        return "Not enough data"

    ma = np.mean(market_prices[-ma_period:])  # Calculate the moving average using the last `ma_period` prices
    current_price = market_prices[-1]  # Get the current price from the market prices list

    percent_change = (current_price - ma) / ma

    trend = np.where(percent_change >= tolerance, "uptrend",
                     np.where(percent_change <= -tolerance, "downtrend", "normaltrend"))

    return trend     

    
# ticker = [3512.53,3496.55,3492.86,3492.6,3498.1,3493.55]
# # ticker = [3498.1,3493.55,3476.92,3458.84,3461,3451.93]
# print(calculate_trend(ticker))
# # print(trendBot(4))
# market_prices = trendBot(500, "LUNCUSDT", "5m") # [0.00009123, 0.00009123, 0.00009111, 0.00009113, 0.00009099, 0.00009058, 0.00009042, 0.00009027, 0.00009029]  # Sample market prices
# ma_period = 15  # Moving average period
# trend = calculate_trend(market_prices, ma_period, 0.005)
# print("Market trend:", trend)