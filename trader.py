from binance.client import Client
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

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")

now = datetime.now()
# print('Trading')
# Variables for trading
qty = 0 # Qty buy
#
feeBuy = 0.099921 # 0.09%
feeBuy = (feeBuy / 100) # Binance fee when buy
#
feeSell = 0.1 # 1%
feeSell = (feeSell / 100) # Binance fee sell
fee = 0
ticker = []
value = 0

##############read tokens####################################
# Def to get tokens, pair and timeframe from params and loop the trade
def getLoopParams():
    df = pd.read_sql('SELECT token, pair, timeframe FROM main.parameters',con=db_con)
    return df 


################STRATEGY PARAMS############################
###########################################################
def trendResul(trend, token, pair, timeframe):
    trendParams = pd.read_sql(f"SELECT * FROM trend where token = {token} and pair = '{pair}' and timeframe = '{timeframe}'",con=db_con)
    result = 'normaltrend'
    if trend < trendParams['downtrend'][0]:
        result = 'downtrend'
    elif trend > trendParams['uptrend'][0]:
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

#########signals##########################################
#########################################################
# Def check_conditionsSell
def check_conditionsSell(close, nextopsval, sellflag, ma, rsi):
    """
    Function to check multiple conditions.
    Parameters:
    close (float): The close value.
    nextopsval (float): The nextopsval value.
    sellflag (int): The sellflag value.
    ma (float): The ma value.
    rsi (float): The rsi value.
    Returns:
    bool: True if all conditions are satisfied, False otherwise.
    """
    return (close >= nextopsval) & (sellflag == 1) & (close < ma) & (rsi < 59)

# Def check_conditionsBuy
def check_conditionsBuy(close, nextopsval, sellflag, ma, rsi):
    """
    Function to check multiple conditions.
    Parameters:
    close (float): The close value.
    nextopsval (float): The nextopsval value.
    sellflag (int): The sellflag value.
    ma (float): The ma value.
    rsi (float): The rsi value.
    Returns:
    bool: True if all conditions are satisfied, False otherwise.
    """
    return (close <= nextopsval) and (sellflag == 0) and (close > ma) and (rsi > 59) 


# Def params
def check_params(env, token, pair, timeframe):
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
    ma = pd.read_sql(f"SELECT * FROM {env}.indicators where token = '{token}' and timeframe = '{timeframe}'and pair = '{pair}' and indicator = 'MA'", con=db_con)
    ##Check rsi
    rsi = pd.read_sql(f"SELECT * FROM {env}.indicators where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}' and indicator = 'RSI'", con=db_con)
    ##Check param
    param = pd.read_sql(f"SELECT * FROM {env}.parameters where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}'", con=db_con)
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

# Retrieving historical data from database
def get_historical_data(token, pair, timeframe):
    table = pair + "_" + timeframe + '_' + str(token)
    f = "'" + values.split('|')[0] + "'"
    t = "'" + values.split('|')[1] + "'"
    query = f"select timestamp close_time"
    query += f" , cast(close as float) as close, close_time as ct"
    query += f'  from public."{table}"'
    #query += f"  where timestamp >= {f}"
    #query += f"  and timestamp <=  {t}"
    query += f" order by 1"
    #print(query)
    df = pd.read_sql(query, con=db_con, index_col='close_time')
    # df.to_excel("data.xlsx")
    return df


# Def get next ops
def getNextOps(token, pair, timeframe):
    df = pd.read_sql(f"SELECT * FROM trader where token = {token} and pair = '{pair}' and timeframe = '{timeframe}'",con=db_con)
    return df 

#et ticker
def getTicker(symbol, interval):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"
    r = requests.get(url)
    df = pd.DataFrame(r.json()) 
    return df

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
def update_trader_nextOps(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"update main.trader set nextOpsVal = %s, trend = %s, updatedAt = %s where pair = %s and timeframe = %s"
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

# Def update close_time
def update_trader_close_time(close_time, data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"update trader set close_time = '" + str(close_time) + "' where pair = %s and timeframe = %s"
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

# Def get next ops
def getNextOps(token, pair, timeframe):
    df = pd.read_sql(f"SELECT * FROM main.trader where token = {token} and pair = {pair} and timeframe = {timeframe}",con=db_con)
    return df

# Def get trend periods
def getTrendPeriods(token, pair, timeframe):
    df = pd.read_sql(f"SELECT * FROM main.trend where token = {token} and pair = {pair} and timeframe = {timeframe}",con=db_con)
    return df    
    

while True:
    print('Looping')
    params = getLoopParams()
    # Loop through the DataFrame rows using itertuples()
    for row in params.itertuples():
        dfapi = operations.getApi(row.token)

        api_key = dfapi['api_key']
        api_secret = dfapi['api_secret']
        client = Client(api_key, api_secret)
        # operation values
        operations = getNextOps(row.token, row.pair, row.timeframe)

        if  check_params("main", row.token, row.pair, row.timeframe) == False:

            #Get the historical data
            df = getTicker(row.pair, row.timeframe)

            # get ma value
            maval = pd.read_sql(
                f"SELECT * FROM main.indicators where token = '{row.token}' and timeframe = '{row.timeframe}'and pair = '{row.pair}' and indicator = 'MA'", con=db_con)
            # get rsi value
            rsival = pd.read_sql(
                f"SELECT * FROM main.indicators where token = '{row.token}' and timeframe = '{row.timeframe}' and pair = '{row.pair}' and indicator = 'RSI'", con=db_con)
            # asigning values
            ma_period = maval['value'][0].astype(int)
            rsi_period = rsival['value'][0].astype(int)
            # # Calculate moving average and RSI
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df = df.dropna(subset=['close'])
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
            operations = getNextOps(row.token, row.pair, row.timeframe)

            if signal['status'][0] == 0:
                print('Bot is down for this pair and timeframe') 
            elif operations['close_time'].values != df[0][499]:
                # print('Calculando')
                # Fisrt buy
                if operations['counterBuy'][0] == 0:
                    #print('First Buy')
                    ticker = []
                    params = pd.read_sql(f"SELECT * FROM parameters where trend= 'normaltrend' whete token = {row.token} and pair = '{pair}' and timeframe = '{timeframe}' ",con=db_con)
                    marginSell = float(params['margingsell'][0]) #%
                    marginSell = marginSell / 100 + 1 # Earning from each sell
                    ForceSell = float(params['forcesell'][0] / 100) # %
                    #
                    #
                    marginBuy = float(params['margingbuy'][0]) #%
                    marginBuy = marginBuy / 100 + 1 # Earning from each buy
                    StopLoss = float(params['stoploss'][0] / 100) # %  
                    #
                    invest = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free']) # Initial value
                    fee = (invest / float(df[4][499])) * feeBuy
                    qty = round(((invest / float(df[4][499])) - fee) ,1)
                    nextOps = round(float(df[4][499]) * marginSell,2)
                    sellFlag = 1
                    data = (qty,nextOps,'sell',sellFlag,1,'firstbuy',now.strftime("%d/%m/%Y %H:%M:%S"),'normaltrend',row.token, row.pair, row.timeframe)
                    #print('Invest-------------------' + str(invest))
                    #print('First Buy-------------------' + str(qty))
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
                    params = pd.read_sql(f"SELECT * FROM parameters where trend= '{trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe) }' and token = {token} and pair = '{pair}' and timeframe ='{timeframe}'",con=db_con)
                    marginSell = float(params['margingsell'][0]) #%
                    marginSell = marginSell / 100 + 1 # Earning from each sell
                    ForceSell = float(params['forcesell'][0] / 100) # %
                    #
                    #
                    marginBuy = float(params['margingbuy'][0]) #%
                    marginBuy = marginBuy / 100 + 1 # Earning from each buy
                    StopLoss = float(params['stoploss'][0] / 100) # %   
                    #
                    #
                    balance = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'])
                    fee = (balance * feeSell)
                    qty = round(((balance * float(df[4][499])) - fee) /  float(df[4][499]) - 0.0001 ,1)# Sell amount
                    nextOps = round(qty / ((qty / float(df[4][499]) * marginBuy)),2) # Next buy
                    # print(nextOps)
                    sellFlag = 0
                    data = (float(qty),float(nextOps),'buy',sellFlag,1,'sell', now.strftime("%d/%m/%Y %H:%M:%S"), trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe), row.token, row.pair, row.timeframe)
                    client.order_market_sell(symbol=str(row.pair), quantity=qty)
                    act_trader_nextOps(data)
                    act_trader_history(data)
                    time.sleep(3)
                    #print('Done...')
                    fee = 0
                    qty = 0
                    nextOps = 0
                # force sell     
                elif float(df[4][499]) <=  (float(operations['nextOpsVal'][0]) - ((float(operations['nextOpsVal'][0]) * ForceSell))) and operations['sellFlag'][0] == 1:
                    #print('Force Sell')
                    ticker = []
                    for i in reversed(range(trendParams['trend'][0])):
                        val = 499 - i
                        value = float(df[4][val])
                        ticker.append(value)
                    params = pd.read_sql(f"SELECT * FROM parameters where trend= '{trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe) }' and token = {token} and pair = '{pair}' and timeframe ='{timeframe}'",con=db_con)
                    marginSell = float(params['margingsell'][0]) #%
                    marginSell = marginSell / 100 + 1 # Earning from each sell
                    ForceSell = float(params['forcesell'][0] / 100) # %
                    #
                    #
                    marginBuy = float(params['margingbuy'][0]) #%
                    marginBuy = marginBuy / 100 + 1 # Earning from each buy
                    StopLoss = float(params['stoploss'][0] / 100) # %   
                    #
                    #
                    balance = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'])
                    fee = (balance * feeSell)
                    qty = round(((balance * float(df[4][499])) - fee) /  float(df[4][499]) - 0.0001 ,1)# Sell amount
                    nextOps = round(qty / ((qty / float(df[4][499]) * marginBuy)),2) # Next buy
                    # print(round(qty,4))
                    sellFlag = 0
                    data = (float(qty),float(nextOps),'buy',sellFlag,1,'forceSell',now.strftime("%d/%m/%Y %H:%M:%S"),trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe),row.token, row.pair, row.timeframe)
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
                    params = pd.read_sql(f"SELECT * FROM parameters where trend= '{trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe) }' and token = {token} and pair = '{pair}' and timeframe ='{timeframe}'",con=db_con)
                    marginSell = float(params['margingsell'][0]) #%
                    marginSell = marginSell / 100 + 1 # Earning from each sell
                    ForceSell = float(params['forcesell'][0] / 100) # %
                    #
                    #
                    marginBuy = float(params['margingbuy'][0]) #%
                    marginBuy = marginBuy / 100 + 1 # Earning from each buy
                    StopLoss = float(params['stoploss'][0] / 100) # %   
                    #
                    #
                    balance_usdt = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'])
                    fee = (balance_usdt / float(df[4][499])) * feeBuy
                    qty = round(((balance_usdt / float(df[4][499])) - fee) - 0.0001,1) # Buy amount
                    nextOps = round(float(df[4][499]) * marginSell,2)
                    sellFlag = 1
                    data = (float(qty),float(nextOps), 'sell',sellFlag,1,'buy',now.strftime("%d/%m/%Y %H:%M:%S"),trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe),row.token, row.pair, row.timeframe)
                    client.order_market_buy(symbol=str(row.pair), quantity=round(qty,4))
                    act_trader_nextOps(data)
                    act_trader_history(data)
                    time.sleep(3)
                    #print('Done...')
                    fee = 0
                    qty = 0
                    nextOps = 0
                elif float(df[4][499]) >=  (float(operations['nextOpsVal'][0]) + ((float(operations['nextOpsVal'][0]) * StopLoss))) and operations['sellFlag'][0] == 0:   
                    #print('Stop Loss')
                    ticker = [] 
                    for i in reversed(range(trendParams['trend'][0])):
                        val = 499 - i
                        value = float(df[4][val])
                        ticker.append(value)
                    params = pd.read_sql(f"SELECT * FROM parameters where trend= '{trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe) }' and token = {token} and pair = '{pair}' and timeframe ='{timeframe}'",con=db_con)
                    marginSell = float(params['margingsell'][0]) #%
                    marginSell = marginSell / 100 + 1 # Earning from each sell
                    ForceSell = float(params['forcesell'][0] / 100) # %
                    #
                    #
                    marginBuy = float(params['margingbuy'][0]) #%
                    marginBuy = marginBuy / 100 + 1 # Earning from each buy
                    StopLoss = float(params['stoploss'][0] / 100) # %   
                    #
                    #     
                    balance_usdt = float(client.get_asset_balance(asset=x[str(row.pair):-3])['free'])
                    fee = (balance_usdt / float(df[4][499])) * feeBuy
                    qty = ((balance_usdt / float(df[4][499])) - fee) - 0.0001 # Buy amount
                    nextOps = float(df[4][499]) * marginSell
                    sellFlag = 1
                    data = (float(qty),float(nextOps),'sell',sellFlag,1,'stopLoss',now.strftime("%d/%m/%Y %H:%M:%S"),trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe),row.token, row.pair, row.timeframe) 
                    client.order_market_buy(symbol=str(row.pair), quantity=round(qty,4))
                    act_trader_nextOps(data)
                    act_trader_history(data)
                    time.sleep(3)
                    #print('Done...')   
                    fee = 0
                    qty = 0
                    nextOps = 0
            else:
                #print('Wait candle close 1d')
                data = (row.pair, row.timeframe) 
                update_trader_close_time(df[0][499], data)
                #Change strategy if the trend changes before next ops is true
                ticker = []
                operations = getNextOps()
                vsellFlag = operations['sellFlag'][0]
                vqty = operations['qty'][0]
                vtrend = operations['trend'][0]
                vnextOps = 0
                vticker = operations['price'][0]
                vOps = operations['nextOps'][0]
                #print(sellFlag)
                #print(qty)
                #print(vtrend)
                # print(trendParams['trend'][0])
                #
                for i in reversed(range(int(trendParams['trend'][0]))):
                    val = 499 - i
                    value = float(df[4][val])
                    ticker.append(value)   
                #print(ticker)
                #print(trendResul(trend.trend(ticker))) 
                #print(trend.trend(ticker)) 
                params = pd.read_sql(f"SELECT * FROM parameters where trend= '{trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe) }' and token = {token} and pair = '{pair}' and timeframe ='{timeframe}'",con=db_con)
                marginSell = float(params['margingsell'][0]) #%
                marginSell = marginSell / 100 + 1 # Earning from each sell
                ForceSell = float(params['forcesell'][0] / 100) # %
                #
                #
                marginBuy = float(params['margingbuy'][0]) #%
                marginBuy = marginBuy / 100 + 1 # Earning from each buy
                StopLoss = float(params['stoploss'][0] / 100) # % 
                if vsellFlag == 1:    
                    vnextOps = round(vticker * marginSell,2) 
                else:              
                    vnextOps = round(vqty / ((vqty / vticker * marginBuy)),2) # Next buy 
                #print(trendResul(trend.trend(ticker)) )       
                if vtrend != trendResul(trend.trend(ticker), row.token, row.pair, row.timeframe):
                   data = (float(vnextOps),trendResul(trend.trend(ticker)),now.strftime("%d/%m/%Y %H:%M:%S"), row.token, row.pair)
                #print('Updating')
                update_trader_nextOps(data)        
    time.sleep(20)