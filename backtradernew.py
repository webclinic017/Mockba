import os
from dotenv import load_dotenv
import sys
import pandas as pd
import numpy as np
from math import floor
import psycopg2
from decimal import *
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
def act_trader_nextOps(data, env):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"INSERT INTO {env}.trader(qty,nextopsval,nextOps,sellflag,counterbuy,ops,close_time,trend,token,pair,timeframe) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
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

################################################BACKTEST#######################################################

def backtest(values, env, token, timeframe, pair):

    # Define variables operation
    marginSell = 0
    marginBuy = 0
    StopLoss = 0
    counterbuy = 0  # Counter how many ops buy
    fee = 0
    nextOps = 0
    qty = 0  # Qty buy
    ticker = []

    data = (0, 0, 'counterBuy', 0, 0, 0, 0, 0, token, pair, timeframe)
    act_trader_nextOps(data, env)

    print("Backtesting in progress, this take time...")

    # Set the display options for float formatting
    pd.set_option('display.float_format', '{:.8f}'.format)

    # # Function to get historical data
    def get_historical_data(pair, timeframe, token, values):
        field = '"timestamp"'
        table = pair + "_" + timeframe + '_' + str(token)
        f = "'" + values.split('|')[0] + "'"
        t = "'" + values.split('|')[1] + "'"
        query = f"SELECT {field}, close_time, close"
        query += f' FROM public."{table}"'
        query += f" WHERE timestamp >= {f}"
        query += f" AND timestamp <= {t}"
        query += f" ORDER BY 1"
        #print(query)
        df = pd.read_sql(query, con=db_con)
        return df
    

    # # Get historical data
    df = get_historical_data(pair, timeframe, token, values)

    # # Variables for backtest
    invest = float(values.split('|')[2])  # Initial value
    feeBuy = 0.099921 / 100  # Binance fee when buying
    feeSell = 0.1 / 100  # Binance fee when selling

    # Build aditional clumns to dataframe
    df['op_action'] = "" # First Buy
    df['qty'] = 0 # The counter buy
    df['nextOps'] = 0  # Next operation to trade
    df['vltrend'] = 0  # Trend
    df['MarginBuy'] = 0 # The margin Buy
    df['MarginSell'] = 0 # The margin sell
    df['StopLoss'] = 0 # The Stop Loss
    df['vlparam'] = "" # The Param
    # df['trend'] = "" # The Trend
    df['ma'] = 0 # The MA
    df['rsi'] = 0 # The RSI

    ma_period = pd.read_sql(f"SELECT value FROM {env}.indicators WHERE token = '{token}' AND timeframe = '{timeframe}' AND pair = '{pair}' AND indicator = 'MA'", con=db_con)['value'][0].astype(int)
    rsi_period = pd.read_sql(f"SELECT value FROM {env}.indicators WHERE token = '{token}' AND timeframe = '{timeframe}' AND pair = '{pair}' AND indicator = 'RSI'", con=db_con)['value'][0].astype(int)
    trendParams = pd.read_sql(f"SELECT * FROM  {env}.trend where token = '{token}' AND timeframe = '{timeframe}' AND pair = '{pair}'", con=db_con)
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
    # # Trending
    # Vectorizing the trend to avoid a foor loop that makes the calculation slower
    # Assuming you have a DataFrame named 'df' with a column 'close'
    window_size = int(trendParams['trend'][0])
    df['trend'] = ''
    for i in range(len(df)):
        prices = df['close'].iloc[max(0, i - window_size + 1):i + 1].tolist()
        df.at[i, 'trend'] = tr.calculate_trend(prices , window_size, float(trendParams['tolerance'][0])) if tr.calculate_trend(prices , window_size, float(trendParams['tolerance'][0])) != 'Not enough data' else 'normaltrend'
    
    # # Operations
    operations = pd.read_sql(f"SELECT * FROM {env}.trader where token = '{token}' and pair = '{pair}' and timeframe ='{timeframe}'", con=db_con)

    # # Getting the first params
    params = pd.read_sql(f"SELECT * FROM {env}.parameters where  token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
    
    #  # Getting trend params
    trendParams = pd.read_sql(f"SELECT * FROM {env}.trend where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}'", con=db_con)

    marginSell = float(params['margingsell'][0] / 100) + 1  # %
    marginBuy = float(params['margingbuy'][0] / 100) + 1    # %
    StopLoss = float(params['stoploss'][0] / 100) + 1  # %
    fee = float((invest / df['close'][0]) * feeBuy)
    qty = float((invest / df['close'][0]) - fee)
    nextOps = float(df['close'][0] * marginSell)
    sellflag = 1  
    
    # # Updating dataframe colums  
    df.loc[0, 'MarginBuy'] = marginBuy if operations['counterbuy'][0] == 0 else 0
    df.loc[0, 'MarginSell'] = marginSell if operations['counterbuy'][0] == 0 else 0
    df.loc[0, 'StopLoss'] = StopLoss if operations['counterbuy'][0] == 0 else 0
    df.loc[0, 'op_action'] = 'firstbuy' if operations['counterbuy'][0] == 0 else 0
    df.loc[0, 'qty'] = qty if operations['counterbuy'][0] == 0 else 0
    df.loc[0, 'nextOps'] = nextOps if operations['counterbuy'][0] == 0 else 0
    counterbuy = 1
    # Updating trader operation dataframe
    operations.loc[0, 'qty'] = qty
    operations.loc[0, 'nextopsval'] = nextOps
    operations.loc[0, 'nextops'] = 'sell'
    operations.loc[0, 'sellflag'] = sellflag
    operations.loc[0, 'counterbuy'] = 1
    operations.loc[0, 'ops'] = 'firstbuy'
    operations.loc[0, 'close_time'] = '444444444'
    operations.loc[0, 'trend'] = 'normaltrend'
    operations.loc[0, 'token'] = token
    operations.loc[0, 'pair'] = pair
    operations.loc[0, 'timeframe'] = timeframe

    # # Starting loop all the dataframe
    for i in range(len(df['close'])):
        # Now implement our margin and sell if signal for rsi and ma
        if check_conditionsSell(df['close'][i], float(operations['nextopsval'][0]), operations['sellflag'][0], df['ma'][i], df['rsi'][i]):
            params_filtered = params[(params['trend'] == df['trend'][i])]
            # Assign values depending trend
            marginSell = float(params_filtered['margingsell'] / 100) + 1  # %
            marginBuy = float(params_filtered['margingbuy'] / 100) + 1    # %
            StopLoss = float(params_filtered['stoploss'] / 100) + 1  # %
            fee = (((invest / df['close'][i]) * df['close'][i])) * feeSell
            qty = (operations['qty'][0] *  df['close'][i]) - fee  # Sell amount
            nextOps = qty / ((qty / df['close'][i]) * marginBuy)  # Next buy
            sellflag = 0
            # Updating dataframe colums  
            df.loc[i, 'MarginBuy'] = marginBuy
            df.loc[i, 'MarginSell'] = marginSell
            df.loc[i, 'StopLoss'] = StopLoss
            df.loc[i, 'op_action'] = 'mySell'
            df.loc[i, 'qty'] = qty
            df.loc[i, 'nextOps'] = nextOps
            # df.loc[i, 'vlparam'] = trendquery
            # Updating trader operation dataframe
            operations.loc[0, 'qty'] = qty
            operations.loc[0, 'nextopsval'] = nextOps
            operations.loc[0, 'nextops'] = 'buy'
            operations.loc[0, 'sellflag'] = sellflag
            operations.loc[0, 'counterbuy'] = 1
            operations.loc[0, 'ops'] = 'mySell'
            operations.loc[0, 'close_time'] = '444444444'
            # operations.loc[0, 'trend'] = trendquery
            operations.loc[0, 'token'] = token
            operations.loc[0, 'pair'] = pair
            operations.loc[0, 'timeframe'] = timeframe
            # print('sell')
        # # Force sell
        elif (df['close'][i] <= (float(operations['nextopsval'][0]) - ((float(operations['nextopsval'][0]) * StopLoss)))) & (operations['sellflag'][0] == 1):
            params_filtered = params[(params['trend'] == df['trend'][i])]
            # Assign values depending trend
            marginSell = float(params_filtered['margingsell'][0] / 100) + 1  # %
            marginBuy = float(params_filtered['margingbuy'][0] / 100) + 1    # %
            StopLoss = float(params_filtered['stoploss'][0] / 100) + 1  # %
            fee = (((invest / df['close'][i]) * df['close'][i])) * feeSell
            qty = (operations['qty'][0] *  df['close'][i]) - fee  # Sell amount
            nextOps = qty / ((qty / df['close'][i]) * marginBuy)  # Next buy
            sellflag = 0
            # Updating dataframe colums  
            df.loc[i, 'MarginBuy'] = marginBuy
            df.loc[i, 'MarginSell'] = marginSell
            df.loc[i, 'StopLoss'] = StopLoss
            df.loc[i, 'op_action'] = 'stopLoss'
            df.loc[i, 'qty'] = qty
            df.loc[i, 'nextOps'] = nextOps
            # df.loc[i, 'vlparam'] = trendquery
            # Updating trader operation dataframe
            operations.loc[0, 'qty'] = qty
            operations.loc[0, 'nextopsval'] = nextOps
            operations.loc[0, 'nextops'] = 'buy'
            operations.loc[0, 'sellflag'] = sellflag
            operations.loc[0, 'counterbuy'] = 1
            operations.loc[0, 'ops'] = 'stoploss'
            operations.loc[0, 'close_time'] = '444444444'
            #operations.loc[0, 'trend'] = trendquery
            operations.loc[0, 'token'] = token
            operations.loc[0, 'pair'] = pair
            operations.loc[0, 'timeframe'] = timeframe
            # print('force sell')
        # # Now find the next value for sell or apply stop loss
        elif check_conditionsBuy(df['close'][i], float(operations['nextopsval'][0]), operations['sellflag'][0], df['ma'][i], df['rsi'][i]):  
            params_filtered = params[(params['trend'] == df['trend'][i])]
            # Assign values depending trend
            marginSell = float(params_filtered['margingsell'] / 100) + 1  # %
            marginBuy = float(params_filtered['margingbuy'] / 100) + 1    # %
            StopLoss = float(params_filtered['stoploss'] / 100) + 1  # %
            fee = (operations['qty'][0] / df['close'][i]) * feeBuy
            qty = (qty /  df['close'][i]) - fee  # Buy amount
            nextOps = df['close'][i] * marginSell
            sellflag = 1
            # Updating dataframe colums  
            df.loc[i, 'MarginBuy'] = marginBuy
            df.loc[i, 'MarginSell'] = marginSell
            df.loc[i, 'StopLoss'] = StopLoss
            df.loc[i, 'op_action'] = 'myBuy'
            df.loc[i, 'qty'] = qty
            df.loc[i, 'nextOps'] = nextOps
            # df.loc[i, 'vlparam'] = trendquery
            # Updating trader operation dataframe
            operations.loc[0, 'qty'] = qty
            operations.loc[0, 'nextopsval'] = nextOps
            operations.loc[0, 'nextops'] = 'sell'
            operations.loc[0, 'sellflag'] = sellflag
            operations.loc[0, 'counterbuy'] = 1
            operations.loc[0, 'ops'] = 'buy'
            operations.loc[0, 'close_time'] = '444444444'
            #operations.loc[0, 'trend'] = trendquery
            operations.loc[0, 'token'] = token
            operations.loc[0, 'pair'] = pair
            operations.loc[0, 'timeframe'] = timeframe 
            # print('buy')
        # # Stop Loss after
        elif (df['close'][i] >= (float(operations['nextopsval'][0]) + ((float(operations['nextopsval'][0]) * StopLoss)))) & (operations['sellflag'][0] == 0): 
            params_filtered = params[(params['trend'] == df['trend'][i])]
            # Assign values depending trend
            marginSell = float(params_filtered['margingsell'] / 100) + 1  # %
            marginBuy = float(params_filtered['margingbuy'] / 100) + 1    # %
            StopLoss = float(params_filtered['stoploss'] / 100) + 1  # %
            fee = (operations['qty'][0] / df['close'][i]) * feeBuy
            qty = (qty /  df['close'][i]) - fee  # Buy amount
            nextOps = df['close'][i] * marginSell
            sellflag = 1
            # Updating dataframe colums  
            df.loc[i, 'MarginBuy'] = marginBuy
            df.loc[i, 'MarginSell'] = marginSell
            df.loc[i, 'StopLoss'] = StopLoss
            df.loc[i, 'op_action'] = 'stopLoss'
            df.loc[i, 'qty'] = qty
            df.loc[i, 'nextOps'] = nextOps
            # df.loc[i, 'vlparam'] = trendquery
            # Updating trader operation dataframe
            operations.loc[0, 'qty'] = qty
            operations.loc[0, 'nextopsval'] = nextOps
            operations.loc[0, 'nextops'] = 'sell'
            operations.loc[0, 'sellflag'] = sellflag
            operations.loc[0, 'counterbuy'] = 1
            operations.loc[0, 'ops'] = 'buy'
            operations.loc[0, 'close_time'] = '444444444'
            #operations.loc[0, 'trend'] = trendquery
            operations.loc[0, 'token'] = token
            operations.loc[0, 'pair'] = pair
            operations.loc[0, 'timeframe'] = timeframe
    
 
    # Delete rows where column 'A' is equal to zero
    df = df[df['qty'] != 0]
    # # Export DataFrame to Excel
    df.to_excel(str(pair) + "_" + str(timeframe) + "_" + str(token) + ".xlsx")

# start = datetime.now()
# pair = 'FTMUSDT'
# token = '556159355'
# timeframe = '5m'
# env = 'backtest'
    
# if check_params(env, token, pair, timeframe):
#     print('No data for this selection, check you have parameter, ma, rsi and historical data for ' + pair + ' of ' + timeframe)
# else:   
#     backtest('2023-01-01|2023-06-30|10000',env, token, timeframe, pair)
#     print('Tiempo de ejecución  ' + str(datetime.now() - start))    
