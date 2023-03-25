import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime as dt
import sys
# loading the .env file
load_dotenv()
PATH_OPERATIONS = os.getenv("PATH_OPERATIONS")
sys.path.append(PATH_OPERATIONS)
import operations

db_con = operations.db_con
# Define strategy parameters
ma_period = 99
ma_period_search = ma_period + 70
# Fetching the data from the crypto exchange 
# Read in the data
df = pd.read_sql('SELECT * FROM public."LUNCBUSD_5m" order by timestamp desc limit ' + str(ma_period_search) ,con=db_con)


df['ma'] = df['close'].rolling(ma_period).mean()

print(df['ma'].iloc[-1])