import pandas as pd
import numpy as np
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt
from decimal import *
import sqlite3
import trend as trend
# plt.rcParams['figure.figsize'] = (20, 10)
# plt.style.use('fivethirtyeight')

# db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)


# Retrieving historical data from database
def get_historical_data():
    # Conexión a base de datos
    db_con = sqlite3.connect('storage/mockba.db')
    query = "select timestamp close_time"
    query += ' , cast(close as float) as close, close_time as ct'
    query += '  from historical_ETHUSDT'
    query += "  where timestamp >= '2021-08-01'"
    # query += "  and timestamp <= '2021-01-02'"
    query += " order by 1"
    # print(query)
    df = pd.read_sql(query, con=db_con, index_col='close_time')
    # df.to_excel("data.xlsx")
    return df

eth = get_historical_data()
ticker = []
value = 0
# Variables for backtest
position = []
action = [] # Take action
invest = 158 # Initial value
qty = [] # Qty buy
counterBuy = 0 # Counter how many ops buy
counterSell = 0 # Counter how manu ops sell
counterStopLoss = 0 # Counter to stop when to loose
counterForceSell = 0 # Force sell
#
feeBuy = 0.099921 # 0.9%
feeBuy = round((feeBuy / 100),9) # Binance fee when buy
#
feeSell = 0.1 # 1%
feeSell = round((feeSell / 100),9) # Binance fee sell
fee = 0
################STRATEGY PARAMS############################
###########################################################
def trendResul(trend):
    result = 'normaltrend'
    if trend < -4:
        result = 'downtrend'
    elif trend > 6:
        result = 'uptrend'
    else:
        result = 'normaltrend'  
    return result          

marginSell = 0
ForceSell = 0
marginBuy = 0
StopLoss = 0
############################################################
############################################################
#
nextOps = []
vltrend = []
vlmb = []
vlms = []
vlfs = []
vlsl = []
vlparam = []
sellFlag = 0

print("Backtesting in progress, this take time...")
# Firstly, we are defining a function named ‘get_macd’ 
# that takes the stock’s price (‘prices’), length of the slow EMA (‘slow’), length 
# of the fast EMA (‘fast’), and the period of the Signal line (‘smooth’).
def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join = 'inner', axis = 1)
    #print(df)
    # df.to_excel("get_macd.xlsx")
    return df    

eth_macd = get_macd(eth['close'], 26, 12, 9)

# First, we are defining a function named 
# implement_macd_strategy which takes the stock prices (‘data’), and MACD 
# data (‘data’) as parameters
# Inside the function, we are creating three empty lists (buy_price, sell_price, 
# and macd_signal) in which the values will be appended while creating the 
# trading strategy.
def implement_macd_strategy(prices, data):    
    buy_price = []
    sell_price = []
    macd_signal = []
    signal = 0

    for i in range(len(data)):
        if data['macd'][i] > data['signal'][i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        elif data['macd'][i] < data['signal'][i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            macd_signal.append(0)
            
    return buy_price, sell_price, macd_signal
            
buy_price, sell_price, macd_signal = implement_macd_strategy(eth['close'], eth_macd)


for i in range(len(macd_signal)):
    if macd_signal[i] > 1:
        position.append(0)
        action.append(0)
        qty.append(0)
        nextOps.append(0)
        vltrend.append(0)
        vlmb.append(0)
        vlms.append(0)
        vlfs.append(0)
        vlsl.append(0)
        vlparam.append(0)
    else:
        position.append(1)
        action.append(0)
        qty.append(0)
        nextOps.append(0)
        vltrend.append(0)
        vlmb.append(0)
        vlms.append(0)
        vlfs.append(0)
        vlsl.append(0)
        vlparam.append(0)

for i in range(len(eth['close'])):
    # First signals based on macd
    if macd_signal[i] == 1 and counterBuy == 0:
        params = pd.read_sql("SELECT * FROM parameters where trend= 'normaltrend'",con=db_con)
        marginSell = float(params['margingsell'].values) #%
        marginSell = marginSell / 100 + 1 # Earning from each sell
        ForceSell = float(params['forcesell'].values / 100) # %
        #
        #
        marginBuy = float(params['margingbuy'].values) #%
        marginBuy = marginBuy / 100 + 1 # Earning from each buy
        StopLoss = float(params['stoploss'].values / 100) # %
        position[i] = 1
        action[i] = 'firstbuy'
        counterBuy =  i
        fee = (invest / eth['close'][i]) * feeBuy
        qty[i] = (invest / eth['close'][i]) - fee
        vlms[i] = marginSell
        nextOps[i] = eth['close'][i] * marginSell
        sellFlag = 1
        counterForceSell = 1
    # Now implement our margin and sell if true
    elif eth['close'][i] >= nextOps[i - (i - counterBuy)] and sellFlag == 1:
         # print(i)
         for x in reversed(range(6)):
             val = i - x # last six periods (5 minutes each, total 30 minutes)
             value = float(eth['close'][val])
             ticker.append(value)
         params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
         marginSell = float(params['margingsell'].values) #%
         marginSell = marginSell / 100 + 1 # Earning from each sell
         ForceSell = float(params['forcesell'].values / 100) # %
         #
         #
         marginBuy = float(params['margingbuy'].values) #%
         marginBuy = marginBuy / 100 + 1 # Earning from each buy
         StopLoss = float(params['stoploss'].values / 100) # %     
         # print(trendResul(trend.trend(ticker)))
         # print(i)
         # print(ticker)
         vltrend[i] = trend.trend(ticker)
         vlparam[i] = trendResul(trend.trend(ticker))
         
         vlmb[i] = marginBuy
         vlfs[i] = ForceSell
         vlsl[i] = StopLoss
         counterSell = i
         fee = (((invest / eth['close'][i - (i - counterBuy)]) * eth['close'][i])) * feeSell
         qty[i] = (qty[i - (i - counterBuy)] * eth['close'][i]) - fee # Sell amount
         action[i] = 'mySell'
         nextOps[i] = qty[i] / ((qty[i] / eth['close'][i]) * marginBuy) # Next buy
         sellFlag = 0
         counterStopLoss = 1
         ticker = []
         # print(ForceSell)
    # Force sell  24 hour
    # elif eth['close'][i] >= (nextOps[i - (i - counterBuy)] * marginLossSell) and sellFlag == 1:
    elif eth['close'][i] <=  nextOps[i - (i - counterBuy)] - (nextOps[i - (i - counterBuy)] * ForceSell) and sellFlag == 1:
         for x in reversed(range(6)):
             val = i - x # last six periods (5 minutes each, total 30 minutes)
             value = float(eth['close'][val])
             ticker.append(value)
         # trend.trend(ticker)
         params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
         marginSell = float(params['margingsell'].values) #%
         marginSell = marginSell / 100 + 1 # Earning from each sell
         ForceSell = float(params['forcesell'].values / 100) # %
         #
         #
         marginBuy = float(params['margingbuy'].values) #%
         marginBuy = marginBuy / 100 + 1 # Earning from each buy
         StopLoss = float(params['stoploss'].values / 100) # %
         vltrend[i] = trend.trend(ticker)
         vlparam[i] = trendResul(trend.trend(ticker))
         vlmb[i] = marginBuy
         vlfs[i] = ForceSell
         vlsl[i] = StopLoss
         fee = (((invest / eth['close'][i - (i - counterBuy)]) * eth['close'][i])) * feeSell
         qty[i] = (qty[i - (i - counterBuy)] * eth['close'][i]) - fee # Sell amount
         nextOps[i] = qty[i] / ((qty[i] / eth['close'][i]) * marginBuy) # Next buy
         sellFlag = 0
         counterStopLoss = 1
         action[i] = 'forceSell'
         counterSell = i 
         ticker = []
    # Now find the next value for sell or apply stop loss 
    elif eth['close'][i] <= nextOps[i - (i - counterSell)] and sellFlag == 0:
         for x in reversed(range(6)):
             val = i - x # last six periods (5 minutes each, total 30 minutes)
             value = float(eth['close'][val])
             ticker.append(value)
         # trend.trend(ticker)
         params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
         marginSell = float(params['margingsell'].values) #%
         marginSell = marginSell / 100 + 1 # Earning from each sell
         ForceSell = float(params['forcesell'].values / 100) # %
         #
         #
         marginBuy = float(params['margingbuy'].values) #%
         marginBuy = marginBuy / 100 + 1 # Earning from each buy
         StopLoss = float(params['stoploss'].values / 100) # %
         vltrend[i] = trend.trend(ticker)
         vlparam[i] = trendResul(trend.trend(ticker))
         vlms[i] = marginSell
         vlfs[i] = ForceSell
         vlsl[i] = StopLoss
         counterBuy = i
         fee = (qty[i - (i - counterSell)] / eth['close'][i]) * feeBuy
         qty[i] = (qty[i - (i - counterSell)] / eth['close'][i]) - fee # Buy amount
         nextOps[i] = eth['close'][i] * marginSell
         action[i] = 'myBuy'
         sellFlag = 1
         counterForceSell = 1
         ticker = []
    # elif eth['close'][i] <= (nextOps[i - (i - counterSell)] * marginLossBuy) and counterStopLoss ==  24 and sellFlag == 0: 
    # Stop Loss after 1 hour of inactivity
    elif eth['close'][i] >=  nextOps[i - (i - counterSell)] + (nextOps[i - (i - counterSell)] * StopLoss) and sellFlag == 0:  
         for x in reversed(range(6)):
             val = i - x # last six periods (5 minutes each, total 30 minutes)
             value = float(eth['close'][val])
             ticker.append(value)
         # trend.trend(ticker) 
         params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
         marginSell = float(params['margingsell'].values) #%
         marginSell = marginSell / 100 + 1 # Earning from each sell
         ForceSell = float(params['forcesell'].values / 100) # %
         #
         #
         marginBuy = float(params['margingbuy'].values) #%
         marginBuy = marginBuy / 100 + 1 # Earning from each buy
         StopLoss = float(params['stoploss'].values / 100) # %
         vltrend[i] = trend.trend(ticker)
         vlparam[i] = trendResul(trend.trend(ticker))
         vlms[i] = marginSell
         vlfs[i] = ForceSell
         vlsl[i] = StopLoss
         # print(counterStopLoss)     
         action[i] = 'stopLoss'
         counterBuy =  i
         fee = (qty[i - (i - counterSell)] / eth['close'][i]) * feeBuy
         qty[i] = (qty[i - (i - counterSell)] / eth['close'][i]) - fee # Buy amount
         nextOps[i] = (eth['close'][i] * marginSell)
         sellFlag = 1   
         counterForceSell = 1
         ticker = []
    elif macd_signal[i] == -1:
        position[i] = 0
        action[i] = 'sell'
        counterStopLoss = counterStopLoss +1 
        counterForceSell = counterForceSell + 1
    else:
        position[i] = position[i-1]
        counterStopLoss = counterStopLoss + 1 
        counterForceSell = counterForceSell + 1

macd = eth_macd['macd']
signal = eth_macd['signal']
close_price = eth['close']
macd_signal = pd.DataFrame(macd_signal).rename(columns = {0:'macd_signal'}).set_index(eth.index)
position = pd.DataFrame(position).rename(columns = {0:'macd_position'}).set_index(eth.index)
action = pd.DataFrame(action).rename(columns = {0:'macd_action'}).set_index(eth.index)
qty = pd.DataFrame(qty).rename(columns = {0:'qty'}).set_index(eth.index)
nextOps = pd.DataFrame(nextOps).rename(columns = {0:'nextOps'}).set_index(eth.index)
vltrend = pd.DataFrame(vltrend).rename(columns = {0:'vltrend'}).set_index(eth.index)
vlmb = pd.DataFrame(vlmb).rename(columns = {0:'MBuy'}).set_index(eth.index)
vlms = pd.DataFrame(vlms).rename(columns = {0:'MSell'}).set_index(eth.index)
vlfs = pd.DataFrame(vlfs).rename(columns = {0:'FSell'}).set_index(eth.index)
vlsl = pd.DataFrame(vlsl).rename(columns = {0:'SLoss'}).set_index(eth.index)
vlparam = pd.DataFrame(vlparam).rename(columns = {0:'vlparam'}).set_index(eth.index)
# frames = [close_price, macd, signal, macd_signal, position, action, qty, nextOps]
frames = [close_price,  action, qty, nextOps, vltrend, vlmb, vlms, vlfs, vlsl, vlparam]
strategy = pd.concat(frames, join = 'inner', axis = 1)

print("The strategy")
# strategy = strategy[strategy['macd_action'] != '0']
# print(strategy)
strategy.to_excel("ETHUSDT-strategy.xlsx")

print("End")