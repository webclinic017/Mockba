import predict_proximity as pp
import pandas as pd
import numpy as np
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt
import sqlite3
from decimal import *
# plt.rcParams['figure.figsize'] = (20, 10)
# plt.style.use('fivethirtyeight')

# pp.predict_proximity(3120,30)

# Retrieving historical data from database
def get_historical_data():
    # Conexión a base de datos
    db_con = sqlite3.connect('mockba.db')
    query = "select strftime('%d/%m/%Y %H %M %S', timestamp) close_time"
    query += ' , cast(close as float) as close'
    query += '  from historical_ETHUSDT'
    query += "  where timestamp >= '2021-01-01'"
    query += "  and timestamp <= '2021-08-31'"
    query += ' order by close_time'
    # print(query)
    df = pd.read_sql(query, con=db_con, index_col='close_time')
    df.to_excel("data.xlsx")
    return df

eth = get_historical_data()

# Variables for backtest
position = []
action = [] # Take action
invest = 400 # Initial value
qtycoin = [] # Qty buy
counterBuy = 0 # Counter how many ops buy
counterSell = 0 # Counter how manu ops sell
feeBuy = 0.099921 # 0.9%
feeBuy = round((feeBuy / 100),9) # Binance fee when buy
#
feeSell = 0.1 # 1%
feeSell = round((feeSell / 100),9) # Binance fee sell
fee = 0
#
marginSell = 0.9
marginSell = marginSell / 100 + 1 # Earning from each sell
#
marginBuy = 0.2
marginBuy = marginBuy / 100 + 1 # Earning from each buy
#
stopLoss = 2
stopLoss = stopLoss / 100 + 1 # Stop Loss
#
nextBuy = 0
sellFlag = 0
killOps = 0

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
    else:
        position.append(1)
        action.append(0)

for i in range(len(eth['close'])):
    if macd_signal[i] == 1 and counterBuy == 0:
        position[i] = 1
        action[i] = 'buy'
        sell_flag = 1
    elif macd_signal[i] == 1:
        position[i] = 1
        action[i] = 'buy'  
    elif macd_signal[i] == -1:
        position[i] = 0
        action[i] = 'sell'
    else:
        position[i] = position[i-1]
        action[i] = 'hold'       

macd = eth_macd['macd']
signal = eth_macd['signal']
close_price = eth['close']
macd_signal = pd.DataFrame(macd_signal).rename(columns = {0:'macd_signal'}).set_index(eth.index)
position = pd.DataFrame(position).rename(columns = {0:'macd_position'}).set_index(eth.index)
action = pd.DataFrame(action).rename(columns = {0:'macd_action'}).set_index(eth.index)

# frames = [close_price, macd, signal, macd_signal, position, action]
frames = [close_price,  action]
strategy = pd.concat(frames, join = 'inner', axis = 1)

print("The strategy")
# strategy = strategy[strategy['macd_action'] != 'hold']
strategy.to_excel("ETHUSDT-strategy.xlsx")

print("End")