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

# # Function to check conditions for sell
def check_conditionsSell(close, nextopsval, sellflag, ma, rsi):
    return (close > nextopsval) & (sellflag == 1) & (close < ma) & (rsi < 60) 

# # Function to check conditions for buy
def check_conditionsBuy(close, nextopsval, sellflag, ma, rsi):
    return (close < nextopsval) & (sellflag == 0) & (close > ma) & (rsi > 60) 
  
################################################BACKTEST#######################################################

def backtest(values, env, token, timeframe, pair):
    
    # the loop will start in the row number of the MA, for example MA99 will start in row 98
    #
    print("Backtesting in progress, this take time...")

    # Define variables operation
    fee = 0
    qty = 0  # Qty buy

    # # Function to get historical data
    def get_historical_data(pair, timeframe, token, values):
        field = '"timestamp"'
        table = pair + "_" + timeframe + '_' + str(token)
        f = "'" + values.split('|')[0] + "'"
        t = "'" + values.split('|')[1] + "'"
        query = f"SELECT {field},  close"
        query += f' FROM public."{table}"'
        query += f" WHERE timestamp >= {f}"
        query += f" AND timestamp <= {t}"
        query += f" ORDER BY 1"
        # print(query)
        df = pd.read_sql(query, con=db_con)
        return df
    

    # # Get historical data
    df = get_historical_data(pair, timeframe, token, values)

    # # Variables for backtest
    invest = float(values.split('|')[2])  # Initial value
    feeBuy = 0.099921 / 100  # Binance fee when buying
    feeSell = 0.1 / 100  # Binance fee when selling
    counterBuy = 0 # Counter how many ops buy
    counterSell = 0 # Counter how manu ops sell

    # Build aditional clumns to dataframe
    df['op_action'] = "" # First Buy
    df['qty'] = 0 # The counter buy
    df['nextOps'] = 0  # Next operation to trade
    df['MarginBuy'] = 0 # Next margin buy
    df['MarginSell'] = 0 # The margin sell
    df['StopLoss'] = 0 # The Stop Loss
    df['ma'] = 0 # The MA
    df['rsi'] = 0 # The RSI
    df['trend'] = ""

    # fecth params from database
    ma_period = pd.read_sql(f"SELECT value FROM {env}.indicators WHERE token = '{token}' AND timeframe = '{timeframe}' AND pair = '{pair}' AND indicator = 'MA'", con=db_con)['value'][0].astype(int)
    rsi_period = pd.read_sql(f"SELECT value FROM {env}.indicators WHERE token = '{token}' AND timeframe = '{timeframe}' AND pair = '{pair}' AND indicator = 'RSI'", con=db_con)['value'][0].astype(int)
    trendParams = pd.read_sql(f"SELECT * FROM  {env}.trend where token = '{token}' AND timeframe = '{timeframe}' AND pair = '{pair}'", con=db_con)
    params = pd.read_sql(f"SELECT * FROM {env}.parameters where  token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
    
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
    for i in range(len(df)):
        prices = df['close'].iloc[max(0, i - window_size + 1):i + 1].tolist()
        df.at[i, 'trend'] = tr.calculate_trend(prices , window_size, float(trendParams['tolerance'][0])) if tr.calculate_trend(prices , window_size, float(trendParams['tolerance'][0])) != 'Not enough data' else 'normaltrend'
        # Vectorizing margins for
        params_filtered = params[(params['trend'] == df['trend'][i])]
        df.at[i, 'MarginBuy'] = float(params_filtered['margingbuy'] / 100) + 1 # %
        df.at[i, 'MarginSell'] = float(params_filtered['margingsell'] / 100) + 1 # %
        df.at[i, 'StopLoss'] = float(params_filtered['stoploss'] / 100) # %
    
    fee = float((invest / df['close'][int(ma_period-1)]) * feeBuy)
    qty = float((invest / df['close'][int(ma_period-1)]) - fee)
    nextOps = float(df['close'][0] * df['MarginSell'][0])
    sellflag = 1  
    
    # # # Updating dataframe colums  
    df.loc[int(ma_period-1), 'op_action'] = 'firstbuy'
    df.loc[int(ma_period-1), 'qty'] = qty
    df.loc[int(ma_period-1), 'nextOps'] = nextOps

    # # # Starting loop all the dataframe
    for i in range(int(ma_period), len(df['close'])):
         counterBuy =  i
         # Now implement our margin and sell if signal for rsi and ma
         # Assuming your DataFrame is named 'df'
         prev_next = df[df['nextOps'] > 0].index[-1]  # taking the previous position value, because we don't know when is next
         prev_qty = df[df['qty'] > 0].index[-1] # taking the previous value, because we don't know when is next
         
         if check_conditionsSell(df['close'][i], df['nextOps'][prev_next], sellflag, df['ma'][i-1], df['rsi'][i-1]):
             # Assign values depending trend
             fee = (((invest / df['close'][i]) * df['close'][i])) * feeSell
             qty = (df['qty'][prev_qty] *  df['close'][i]) - fee  # Sell amount
             nextOps = qty / ((qty / df['close'][i]) * float(df['MarginBuy'][i]))  # Next buy
             sellflag = 0
             # Updating dataframe colums  
             df.loc[i, 'op_action'] = 'mySell'
             df.loc[i, 'qty'] = qty
             df.loc[i, 'nextOps'] = nextOps
             counterSell = i
            # print('sell')
         # # Force sell
         elif (df['close'][i] <= (df['nextOps'][prev_next] - (df['nextOps'][prev_next] * float(df['StopLoss'][i])))) & (sellflag == 1):
             # Assign values depending trend
             fee = (((invest / df['close'][i]) * df['close'][i])) * feeSell
             qty = (df['qty'][prev_qty] *  df['close'][i]) - fee  # Sell amount
             nextOps = qty / ((qty / df['close'][i]) * float(df['MarginBuy'][i]))  # Next buy
             sellflag = 0
             # Updating dataframe colums  
             df.loc[i, 'op_action'] = 'stopLoss'
             df.loc[i, 'qty'] = qty
             df.loc[i, 'nextOps'] = nextOps
             counterSell = i 
             # print('force sell')
         # # Now find the next value for sell or apply stop loss
         elif check_conditionsBuy(df['close'][i], df['nextOps'][prev_next], sellflag, df['ma'][i-1], df['rsi'][i-1]):
             fee = (df['qty'][prev_qty] / df['close'][i]) * feeBuy
             qty = (df['qty'][prev_qty] /  df['close'][i]) - fee  # Buy amount
             nextOps = df['close'][i] * float(df['MarginSell'][i])
             sellflag = 1
             # Updating dataframe colums  
             df.loc[i, 'op_action'] = 'myBuy'
             df.loc[i, 'qty'] = qty
             df.loc[i, 'nextOps'] = nextOps
             counterBuy = i
             # print('buy')  
         # # Stop Loss after
         elif (df['close'][i] >= (df['nextOps'][prev_next] + ((df['nextOps'][prev_next] * float(df['StopLoss'][i]))))) & (sellflag == 0): 
             fee = (df['qty'][prev_qty] / df['close'][i]) * feeBuy
             qty = (df['qty'][prev_qty] /  df['close'][i]) - fee  # Buy amount
             nextOps = df['close'][i] * float(df['MarginSell'][i])
             sellflag = 1
             # Updating dataframe colums  
             df.loc[i, 'op_action'] = 'stopLoss'
             df.loc[i, 'qty'] = qty
             df.loc[i, 'nextOps'] = nextOps
             counterBuy =  i  
     
    # Delete rows where column 'A' is equal to zero
    df = df[df['qty'] != 0]
    # # Export DataFrame to Excel
    df.to_excel(str(pair) + "_" + str(timeframe) + "_" + str(token) + ".xlsx")

# start = datetime.now()
# pair = 'LUNCUSDT'
# token = '556159355'
# timeframe = '5m'
# env = 'backtest'
    
# if check_params(env, token, pair, timeframe):
#     print('No data for this selection, check you have parameter, ma, rsi and historical data for ' + pair + ' of ' + timeframe)
# else:   
#     backtest('2023-05-15|2023-06-30|100',env, token, timeframe, pair)
#     print('Execution time  ' + str(datetime.now() - start))    
