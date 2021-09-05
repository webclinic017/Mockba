import predict_proximity as pp
import pandas as pd
import numpy as np
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt
from decimal import *
# plt.rcParams['figure.figsize'] = (20, 10)
# plt.style.use('fivethirtyeight')

# pp.predict_proximity(3120,30)

# Retrieving historical data from database
def get_historical_data():
    # gh.get_all_binance("ETHUSDT", "5m", save=True)
    # Conexión a base de datos
    postgre_con = pg.Postgres().postgre_con
    query = "select to_char(TO_TIMESTAMP(close_time/1000),'dd/mm/yyyy HH24:MI:SS') close_time"
    query += ' , cast(close as float) as close, close_time as close_time1'
    query += '  from public."historical_ETHUSDT"'
    query += "  where to_timestamp( close_time/1000)::date >= '2021-01-01'"
    query += "  and to_timestamp( close_time/1000)::date <= '2021-08-31'"
    query += ' order by close_time1'
    # print(query)
    df = pd.read_sql(query, con=postgre_con, index_col='close_time')
    df.to_excel("data.xlsx")
    return df

eth = get_historical_data()
# print(len(eth['close']))


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



# In this step, we are going to create a list that indicates 1 if we hold the stock 
# or 0 if we don’t own or hold the stock.
# First, we are creating an empty list named ‘position’. We 
# are passing two for-loops, one is to generate values for the ‘position’ list to
# just match the length of the ‘signal’ list. The other for-loop is the one we are
# using to generate actual position values. Inside the second for-loop, we are
# iterating over the values of the ‘signal’ list, and the values of the ‘position’ 
# list get appended concerning which condition gets satisfied. The value of 
# the position remains 1 if we hold the stock or remains 0 if we sold or don’t 
# own the stock. Finally, we are doing some data manipulations to combine 
# all the created lists into one dataframe.
position = []
action = []
invest = 400
cantidadc_coin = []
counter_buy = 0
counter_sell = 0
commission_buy_binance = 0.099921 # 0.9%
commission_buy_binance = round((commission_buy_binance / 100),9)
#
commission_sell_binance = 0.1 # 1%
commission_sell_binance = round((commission_sell_binance / 100),9)
comision = 0
#
margin = 0.5
margin = margin / 100 + 1
next_buy = 0
sell_flag = 0
kill_ops = 0

for i in range(len(macd_signal)):
    if macd_signal[i] > 1:
        position.append(0)
        action.append(0)
        cantidadc_coin.append(0)
    else:
        position.append(1)
        action.append(0)
        cantidadc_coin.append(0)
        
for i in range(len(eth['close'])):
    if macd_signal[i] == 1 and counter_buy == 0:
        position[i] = 1
        action[i] = 'buy'
        counter_buy =  i
        comision = (invest / eth['close'][i]) * commission_buy_binance
        cantidadc_coin[i] = (invest / eth['close'][i]) - comision
        sell_flag = 1
    elif macd_signal[i] == 1 and eth['close'][i] <= next_buy:
        position[i] = 1
        action[i] = 'buy'
        counter_buy =  i
        comision = (invest / eth['close'][i]) * commission_buy_binance
        cantidadc_coin[i] = (invest / eth['close'][i]) - comision    
        # set flag one that indicates sell
        sell_flag = 1
        kill_ops = 0
    elif macd_signal[i] == 1:
        position[i] = 1
        action[i] = 'buy'
        kill_ops =  kill_ops + 1 
        if kill_ops == 3:
           #print('kill and buy again')
           # if are 3 signal and nothing happend, kill and buy again
           counter_buy =  i
           comision = (invest / eth['close'][i]) * commission_buy_binance
           cantidadc_coin[i] = (invest / eth['close'][i]) - comision    
           # set flag one that indicates sell
           sell_flag = 1
           kill_ops = 0    
    elif macd_signal[i] == -1 and sell_flag == 1:
        position[i] = 0
        action[i] = 'sell'
        counter_sell = i
        # Find last buy in ethereum
        comision = (((invest / eth['close'][i - (counter_sell - counter_buy)]) * eth['close'][i])) * commission_sell_binance
        cantidadc_coin[i] = ((invest / eth['close'][i - (counter_sell - counter_buy)]) * eth['close'][i]) - comision
        # Mark next buy, when margin reach the espected value
        next_buy = cantidadc_coin[i] / (cantidadc_coin[i - (counter_sell - counter_buy)] * margin)
        # set flag cero that indicates not to sell
        sell_flag = 0
    else:
        position[i] = position[i-1]
        action[i] = 'hold'
        cantidadc_coin[i] = 0
 
macd = eth_macd['macd']
signal = eth_macd['signal']
close_price = eth['close']
macd_signal = pd.DataFrame(macd_signal).rename(columns = {0:'macd_signal'}).set_index(eth.index)
position = pd.DataFrame(position).rename(columns = {0:'macd_position'}).set_index(eth.index)
action = pd.DataFrame(action).rename(columns = {0:'macd_action'}).set_index(eth.index)
cantidadc_coin = pd.DataFrame(cantidadc_coin).rename(columns = {0:'cantidadc_coin'}).set_index(eth.index)

frames = [close_price, macd, signal, macd_signal, position, action, cantidadc_coin]
# frames = [close_price,  action, cantidadc_coin]
strategy = pd.concat(frames, join = 'inner', axis = 1)

print("The strategy")
# strategy = strategy[strategy['macd_action'] != 'hold']
strategy.to_excel("ETHUSDT-strategy.xlsx")
# print(strategy)




#########################################################################################
# Backtesting
#########################################################################################

#eth_ret = pd.DataFrame(np.diff(eth['close'])).rename(columns = {0:'returns'})
#print(eth_ret)
'''
macd_strategy_ret = []

for i in range(len(eth_ret)):
    try:
        returns = eth_ret['returns'][i]*strategy['macd_position'][i]
        macd_strategy_ret.append(returns)
    except:
        pass
    
macd_strategy_ret_df = pd.DataFrame(macd_strategy_ret).rename(columns = {0:'macd_returns'})

investment_value = 100000
number_of_stocks = floor(investment_value/eth['close'][-1])
macd_investment_ret = []

for i in range(len(macd_strategy_ret_df['macd_returns'])):
    returns = number_of_stocks*macd_strategy_ret_df['macd_returns'][i]
    macd_investment_ret.append(returns)

macd_investment_ret_df = pd.DataFrame(macd_investment_ret).rename(columns = {0:'investment_returns'})
total_investment_ret = round(sum(macd_investment_ret_df['investment_returns']), 2)
profit_percentage = floor((total_investment_ret/investment_value)*100)
print(cl('Profit gained from the MACD strategy a day 5 minutes by investing $ ' + str(investment_value) + ' in ETH : {}'.format(total_investment_ret), attrs = ['bold']))
print(cl('Profit percentage of the MACD strategy : {}%'.format(profit_percentage), attrs = ['bold']))


'''
print("End")