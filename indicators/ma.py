import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime as dt
import sys
# loading the .env file
load_dotenv()
# access the environment variables
PATH_OPERATIONS = os.getenv("PATH_OPERATIONS")
# Add the path to the system path
sys.path.append(PATH_OPERATIONS)
import operations

db_con = operations.db_con

def ma(pair, interval, token):
    # get the moving average of the last n candles
    ma = pd.read_sql("SELECT value FROM backtest.indicators where token ='" + token + "' and timeframe = '" + interval + "' and pair = '" + pair.upper() + "' and indicator = 'MA'" ,con=db_con)
    print("SELECT value FROM backtest.indicators where token ='" + token + "' and timeframe = '" + interval + "' and pair = '" + pair.upper() + "' and indicator = 'MA'")
    # Define strategy parameters
    ma_period = int(ma['value']) if len(ma) > 0 else 0
    ma_period_search = ma_period + 1
    # Fetching the data from the crypto exchange 
    # Read in the data
    df = pd.read_sql('SELECT * FROM public."' + pair.upper() +'_' + interval + '" order by timestamp desc limit ' + str(ma_period_search) ,con=db_con)

    df['ma'] = df['close'].rolling(ma_period).mean()

    print(df['ma'].iloc[-1] if ma_period > 0 else 0)
    return df['ma'].iloc[-1] if ma_period > 0 else 0

ma("LUNCBUSD", "15m", "556159355") 