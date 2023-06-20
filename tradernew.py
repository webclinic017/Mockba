import os
from dotenv import load_dotenv
import sys
import pandas as pd
import numpy as np
from math import floor
import psycopg2
from decimal import *
import time
#import trend as trend
from indicators import trend
from datetime import datetime
# loading the .env file
load_dotenv()
# access the environment variables
PATH_OPERATIONS = os.getenv("PATH_OPERATIONS")
# Add the path to the system path
sys.path.append(PATH_OPERATIONS)
import operations
db_con = operations.db_con
from indicators import trend as tr

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")

# Def params
def check_params(token, pair, timeframe):
    """
    Function to check multiple conditions.
    Parameters:
    env : The enviroment backtest or main.
    token: The user token.
    pair: The pair, ex LUNCBUSD.
    timeframe: Thetimeframe.
    rsi: The rsi value.
    Returns:
    bool: True if all conditions are satisfied, False otherwise.
    """
    global gmessage
    ##First check ma
    ma = pd.read_sql(f"SELECT * FROM main.indicators where token = '{token}' and timeframe = '{timeframe}'and pair = '{pair}' and indicator = 'MA'", con=db_con)
    ##Check rsi
    rsi = pd.read_sql(f"SELECT * FROM main.indicators where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}' and indicator = 'RSI'", con=db_con)
    ##Check param
    param = pd.read_sql(f"SELECT * FROM main.parameters where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}'", con=db_con)
    ##Check table
    check_table_exists = f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{pair}_{timeframe}_{token}';"
    table_exists = pd.read_sql(check_table_exists, db_con).iloc[0, 0] > 0
    if ma.empty:
       return True
    elif rsi.empty:
        return True
    elif param.empty:
        return True 
    elif table_exists:
        return False      
    else:
        return False  

# # Function to check trend result
def trendResult(trend, trendParams):
    # print("{:.10f}".format(trend), float(trendParams['downtrend'][0]), float(trendParams['uptrend'][0]), abs(float(trend)) < float(trendParams['downtrend'][0]), abs(float(trend)) > float(trendParams['uptrend'][0]))
    if float(trend) < float(trendParams['downtrend'][0]):
        return 'downtrend'
    elif float(trend) > float(trendParams['uptrend'][0]):
        return 'uptrend'
    else:
        return 'normaltrend'   

# # Function to check conditions for sell
def check_conditionsSell(close, nextopsval, sellflag, ma, rsi):
    return (close >= nextopsval) & (sellflag == 1) & (close < ma) & (rsi < 59)

# # Function to check conditions for buy
def check_conditionsBuy(close, nextopsval, sellflag, ma, rsi):
    return (close <= nextopsval) & (sellflag == 0) & (close > ma) & (rsi > 59) 

# Def insert last data ops
def act_trader_nextOps(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"INSERT INTO main.trader(qty,nextopsval,nextOps,sellflag,counterbuy,ops,close_time,trend,token,pair,timeframe) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, data)
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()           
# Def insert last data ops
def act_trader_history(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"INSERT INTO main.trader_history(qty,nextopsval,nextOps,sellflag,counterbuy,ops,close_time,trend,token,pair,timeframe) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, data)
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 

# Def get trend periods
def getTrendPeriods(token, pair, timeframe):
    df = pd.read_sql(f"SELECT * FROM main.trend where token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'",con=db_con)
    return df  

# # Function to get historical data
def get_historical_data(pair, timeframe):
    url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={timeframe}"
    r = requests.get(url)
    df = pd.DataFrame(r.json()) 
    return df     
################################################TRADER#######################################################

# Define variables operation
marginSell = 0
marginBuy = 0
StopLoss = 0
counterbuy = 0  # Counter how many ops buy
fee = 0
nextOps = 0
qty = 0  # Qty buy
ticker = []

# Endless loop
while True:
    print('Looping')
    trader = pd.read_sql(f"SELECT token, pair, timeframe, percentage_of_available FROM main.parameters group by token, pair, timeframe, percentage_of_available", con=db_con)

    # looping all parameters of tokens, getting tokens, pairs, timeframe and percentajes
    # Loop through the DataFrame rows using itertuples()
    for row in trader.itertuples():
        # Proceed only if there are params for this dataframe
        if  check_params(row.token, row.pair, row.timeframe) == False:
            print('No params')
        elif signal['status'][0] == 0:
            print('Bot is down for this pair and timeframe')
        else:               
            # # Get historical data
            df = get_historical_data(row.pair, row.timeframe)

            # # Variables for backtest
            feeBuy = 0.099921 / 100  # Binance fee when buying
            feeSell = 0.1 / 100  # Binance fee when selling

            ma_period = pd.read_sql(f"SELECT value FROM main.indicators WHERE token = '{row.token}' AND timeframe = '{row.timeframe}' AND pair = '{row.pair}' AND indicator = 'MA'", con=db_con)['value'][0].astype(int)
            rsi_period = pd.read_sql(f"SELECT value FROM main.indicators WHERE token = '{row.token}' AND timeframe = '{row.timeframe}' AND pair = '{row.pair}' AND indicator = 'RSI'", con=db_con)['value'][0].astype(int)

            # # Calculate moving average and RSI
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['ma'] = df['close'].rolling(ma_period).mean()
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
 
            periods = getTrendPeriods(row.token, row.pair, row.timeframe)
            # Enable o dibale bot
            signal = pd.read_sql(f"SELECT * FROM t_signal where token = {row.token} adn pair = '{row.pair}' and timeframe = '{row.timeframe}'",con=db_con)
            # operations values
            operations = pd.read_sql(f"SELECT * FROM main.trader where token = {row.token} and pair = '{row.pair}' and timeframe = '{row.timeframe}'",con=db_con)
            # Getting trend params
            trendParams = pd.read_sql(f"SELECT * FROM main.trend where token = '{row.token}' and timeframe = '{row.timeframe}' and pair = '{row.pair}'", con=db_con)
            # Params
            params = pd.read_sql(f"SELECT * FROM parameters where trend= 'normaltrend' and token = {row.token} and pair = '{row.pair}' and timeframe = '{row.timeframe}' ",con=db_con)
            
            if operations['close_time'].values != df[0][499]:
                # Fisrt buy
                if operations['counterBuy'][0] == 0: 
                    #print('First Buy')
                    ticker = []
                    marginSell = float(params['margingsell'][0] / 100) #%
                    marginSell = marginSell / 100 + 1 # Earning from each sell
                    #
                    marginBuy = float(params['margingbuy'][0] / 100) #%
                    marginBuy = marginBuy / 100 + 1 # Earning from each buy
                    StopLoss = float(params['stoploss'][0] / 100) # %  
                    #
                    availabeOf = float(params['percentage_of_available'][0] / 100)
                    invest = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'] * availabeOf) # Initial value
                    fee = (invest / float(df[4][499])) * feeBuy
                    qty = round(((invest / float(df[4][499])) - fee) ,1)
                    nextOps = round(float(df[4][499]) * marginSell,2)
                    sellFlag = 1
                    data = (qty,nextOps,'sell',sellFlag,1,'firstbuy',now.strftime("%d/%m/%Y %H:%M:%S"),'normaltrend',row.token, row.pair, row.timeframe)
                    client.order_market_buy(symbol=str(row.pair), quantity=qty)           
                    act_trader_nextOps(data)
                    act_trader_history(data)
                    #sm.sendMail('First Buy')
                    time.sleep(3)
                    #print('Done...')
                    fee = 0
                    qty = 0
                    nextOps = 0 
                # Now implement our margin and sell if signal for rsi and ma   
                elif check_conditionsSell(float(df[4][499]), float(operations['nextopsval'][0]), operations['sellflag'][0], df['ma'][0], df['rsi'][0]):    
                        #print('Sell')
                        ticker = []
                        for i in reversed(range(trendParams['trend'][0])):
                            val = 499 - i
                            value = float(df[4][val])
                            ticker.append(value)
                        trendquery =  tr.calculate_trend(ticker, int(trendParams['trend'][0]))
                        params_filtered = params[(params['trend'] == trendquery)]    
                        marginSell = float(params_filtered['margingsell'] / 100) #%
                        marginSell = marginSell / 100 + 1 # Earning from each sell
                        #
                        marginBuy = float(params_filtered['margingbuy'] / 100) #%
                        marginBuy = marginBuy / 100 + 1 # Earning from each buy
                        StopLoss = float(params_filtered['stoploss'] / 100) # %   
                        #
                        availabeOf = float(params_filtered['percentage_of_available'] / 100)
                        balance = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'] * availabeOf)
                        fee = (balance * feeSell)
                        qty = round(((balance * float(df[4][499])) - fee) /  float(df[4][499]) - 0.0001 ,1)# Sell amount
                        nextOps = round(qty / ((qty / float(df[4][499]) * marginBuy)),2) # Next buy
                        # print(nextOps)
                        sellFlag = 0
                        data = (float(qty),float(nextOps),'buy',sellFlag,1,'sell', now.strftime("%d/%m/%Y %H:%M:%S"), trendResult(trend.trend(ticker), trendParams), row.token, row.pair, row.timeframe)
                        client.order_market_sell(symbol=str(row.pair), quantity=qty)
                        act_trader_nextOps(data)
                        act_trader_history(data)
                        time.sleep(3)
                        #print('Done...')
                        fee = 0
                        qty = 0
                        nextOps = 0
                    # force sell     
                elif float(df[4][499]) <=  (float(operations['nextOpsVal'][0]) - ((float(operations['nextOpsVal'][0]) * StopLoss))) and operations['sellFlag'][0] == 1:
                        #print('Force Sell')
                        ticker = []
                        for i in reversed(range(trendParams['trend'][0])):
                            val = 499 - i
                            value = float(df[4][val])
                            ticker.append(value)
                        trendquery =  tr.calculate_trend(ticker, int(trendParams['trend'][0]))
                        params_filtered = params[(params['trend'] == trendquery)]    
                        marginSell = float(params_filtered['margingsell'] / 100) #%
                        marginSell = marginSell / 100 + 1 # Earning from each sell
                        #
                        marginBuy = float(params_filtered['margingbuy'] / 100) #%
                        marginBuy = marginBuy / 100 + 1 # Earning from each buy
                        StopLoss = float(params_filtered['stoploss'] / 100) # % 
                        #
                        availabeOf = float(params['percentage_of_available'][0] / 100)
                        balance = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'] * availabeOf)
                        fee = (balance * feeSell)
                        qty = round(((balance * float(df[4][499])) - fee) /  float(df[4][499]) - 0.0001 ,1)# Sell amount
                        nextOps = round(qty / ((qty / float(df[4][499]) * marginBuy)),2) # Next buy
                        # print(round(qty,4))
                        sellFlag = 0
                        data = (float(qty),float(nextOps),'buy',sellFlag,1,'forceSell',now.strftime("%d/%m/%Y %H:%M:%S"),trendResult(trend.trend(ticker), trendParams),row.token, row.pair, row.timeframe)
                        client.order_market_sell(symbol=str(row.pair), quantity=qty)
                        act_trader_nextOps(data)
                        act_trader_history(data)
                        time.sleep(3)
                        #print('Done...')
                        fee = 0
                        qty = 0
                        nextOps = 0
                    # Now find the next value for sell or apply stop loss
                elif check_conditionsBuy(float(df[4][499]), float(operations['nextopsval'][0]), operations['sellflag'][0], df['ma'][0], df['rsi'][0]):    
                        #print('Buy')
                        ticker = []
                        for i in reversed(range(trendParams['trend'][0])):
                            val = 499 - i
                            value = float(df[4][val])
                            ticker.append(value)
                        trendquery =  tr.calculate_trend(ticker, int(trendParams['trend'][0]))
                        params_filtered = params[(params['trend'] == trendquery)]    
                        marginSell = float(params_filtered['margingsell'] / 100) #%
                        marginSell = marginSell / 100 + 1 # Earning from each sell
                        #
                        marginBuy = float(params_filtered['margingbuy'] / 100) #%
                        marginBuy = marginBuy / 100 + 1 # Earning from each buy
                        StopLoss = float(params_filtered['stoploss'] / 100) # % 
                        #
                        availabeOf = float(params['percentage_of_available'][0] / 100)
                        balance_of = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'] * availabeOf)
                        fee = (balance_of / float(df[4][499])) * feeBuy
                        qty = round(((balance_of / float(df[4][499])) - fee) - 0.0001,1) # Buy amount
                        nextOps = round(float(df[4][499]) * marginSell,2)
                        sellFlag = 1
                        data = (float(qty),float(nextOps), 'sell',sellFlag,1,'buy',now.strftime("%d/%m/%Y %H:%M:%S"),trendResult(trend.trend(ticker), trendParams),row.token, row.pair, row.timeframe)
                        client.order_market_buy(symbol=str(row.pair), quantity=round(qty,4))
                        act_trader_nextOps(data)
                        act_trader_history(data)
                        time.sleep(3)
                        #print('Done...')
                        fee = 0
                        qty = 0
                        nextOps = 0
                    # Stop loss    
                elif float(df[4][499]) >=  (float(operations['nextOpsVal'][0]) + ((float(operations['nextOpsVal'][0]) * StopLoss))) and operations['sellFlag'][0] == 0:   
                        #print('Stop Loss')
                        ticker = [] 
                        for i in reversed(range(trendParams['trend'][0])):
                            val = 499 - i
                            value = float(df[4][val])
                            ticker.append(value)
                        trendquery =  tr.calculate_trend(ticker, int(trendParams['trend'][0]))
                        params_filtered = params[(params['trend'] == trendquery)]    
                        marginSell = float(params_filtered['margingsell'] / 100) #%
                        marginSell = marginSell / 100 + 1 # Earning from each sell
                        #
                        marginBuy = float(params_filtered['margingbuy'] / 100) #%
                        marginBuy = marginBuy / 100 + 1 # Earning from each buy
                        StopLoss = float(params_filtered['stoploss'] / 100) # % 
                        #     
                        availabeOf = float(params['percentage_of_available'][0] / 100)
                        balance_of = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'] * availabeOf)
                        fee = (balance_of / float(df[4][499])) * feeBuy
                        qty = ((balance_of / float(df[4][499])) - fee) - 0.0001 # Buy amount
                        nextOps = float(df[4][499]) * marginSell
                        sellFlag = 1
                        data = (float(qty),float(nextOps),'sell',sellFlag,1,'stopLoss',now.strftime("%d/%m/%Y %H:%M:%S"),trendResult(trend.trend(ticker), trendParams),row.token, row.pair, row.timeframe) 
                        client.order_market_buy(symbol=str(row.pair), quantity=round(qty,4))
                        act_trader_nextOps(data)
                        act_trader_history(data)
                        time.sleep(3)
                        #print('Done...')   
                        fee = 0
                        qty = 0
                        nextOps = 0                                        
    time.sleep(40) 