import predict_proximity as pp
import pandas as pd
import numpy as np
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt
from decimal import *
import sqlite3
# plt.rcParams['figure.figsize'] = (20, 10)
# plt.style.use('fivethirtyeight')

# pp.predict_proximity(3120,30)

# Retrieving historical data from database
def get_historical_data():
    # Conexión a base de datos
    db_con = sqlite3.connect('storage/mockba.db')
    query = "select timestamp close_time"
    query += ' , cast(close as float) as close, close_time as ct'
    query += '  from historical_ETHUSDT'
    query += "  where timestamp >= '2021-01-01'"
    # query += "  and timestamp <= '2021-01-02'"
    query += " order by 1"
    # print(query)
    df = pd.read_sql(query, con=db_con, index_col='close_time')
    # df.to_excel("data.xlsx")
    return df

eth = get_historical_data()

# Variables for backtest
position = []
action = [] # Take action
invest = 50 # Initial value
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
marginSell = 18 #%
marginSell = marginSell / 100 + 1 # Earning from each sell
timeFrameForceSell = 1152 # 96 hour 96*60/5, 8 days
#
#
marginBuy = 3 #%
marginBuy = marginBuy / 100 + 1 # Earning from each buy
timeFrameStopLoss = 288 # 24 hour 24*60/5
############################################################
############################################################
#
nextOps = []
sellFlag = 0
killOps = 0
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
    else:
        position.append(1)
        action.append(0)
        qty.append(0)
        nextOps.append(0)

for i in range(len(eth['close'])):
    # First signals based on macd
    if macd_signal[i] == 1 and counterBuy == 0:
        position[i] = 1
        action[i] = 'buy'
        counterBuy =  i
        fee = (invest / eth['close'][i]) * feeBuy
        qty[i] = (invest / eth['close'][i]) - fee
        nextOps[i] = eth['close'][i] * marginSell
        sellFlag = 1
        counterForceSell = 1
    # Now implement our margin and sell if true
    elif eth['close'][i] >= nextOps[i - (i - counterBuy)] and sellFlag == 1:
         counterSell = i
         fee = (((invest / eth['close'][i - (i - counterBuy)]) * eth['close'][i])) * feeSell
         qty[i] = (qty[i - (i - counterBuy)] * eth['close'][i]) - fee # Sell amount
         action[i] = 'mySell'
         nextOps[i] = qty[i] / ((qty[i] / eth['close'][i]) * marginBuy) # Next buy
         sellFlag = 0
         counterStopLoss = 1
    # Force sell  24 hour
    # elif eth['close'][i] >= (nextOps[i - (i - counterBuy)] * marginLossSell) and sellFlag == 1:
    elif counterForceSell ==  timeFrameForceSell and sellFlag == 1:
         # print('Counter Force Sell - ' + str(counterForceSell))
         fee = (((invest / eth['close'][i - (i - counterBuy)]) * eth['close'][i])) * feeSell
         qty[i] = (qty[i - (i - counterBuy)] * eth['close'][i]) - fee # Sell amount
         nextOps[i] = qty[i] / ((qty[i] / eth['close'][i]) * marginBuy) # Next buy
         sellFlag = 0
         counterStopLoss = 1
         action[i] = 'forceSell'
         counterSell = i 
    # Now find the next value for sell or apply stop loss 
    elif eth['close'][i] <= nextOps[i - (i - counterSell)] and sellFlag == 0:
         counterBuy = i
         fee = (qty[i - (i - counterSell)] / eth['close'][i]) * feeBuy
         qty[i] = (qty[i - (i - counterSell)] / eth['close'][i]) - fee # Buy amount
         nextOps[i] = eth['close'][i] * marginSell
         action[i] = 'myBuy'
         sellFlag = 1
         counterForceSell = 1
    # elif eth['close'][i] <= (nextOps[i - (i - counterSell)] * marginLossBuy) and counterStopLoss ==  24 and sellFlag == 0: 
    # Stop Loss after 1 hour of inactivity
    elif counterStopLoss ==  timeFrameStopLoss and sellFlag == 0:   
         # print(counterStopLoss)     
         action[i] = 'stopLoss'
         counterBuy =  i
         fee = (qty[i - (i - counterSell)] / eth['close'][i]) * feeBuy
         qty[i] = (qty[i - (i - counterSell)] / eth['close'][i]) - fee # Buy amount
         nextOps[i] = (eth['close'][i] * marginSell)
         sellFlag = 1   
         counterForceSell = 1
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
# frames = [close_price, macd, signal, macd_signal, position, action, qty, nextOps]
frames = [close_price,  action, qty, nextOps]
strategy = pd.concat(frames, join = 'inner', axis = 1)

print("The strategy")
# strategy = strategy[strategy['macd_action'] != '0']
# print(strategy)
strategy.to_excel("ETHUSDT-strategy.xlsx")

print("End")