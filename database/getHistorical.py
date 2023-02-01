# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
# import operations
from database import operations

### API
api_telegram = ""
df = operations.getApi(api_telegram)
# Getting api from database
binance_api_key = df['api_key']
binance_api_secret = df['api_secret']

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "2h": 120, "4h": 240, "1d": 1440}
batch_size = 750
binance_client = Client(api_key=binance_api_key.to_string(index=False), api_secret=binance_api_secret.to_string(index=False))

#Database conection
db_con = operations.db_con
# postgre_con = create_engine('postgresql+psycopg2://openbizview:openbizview@localhost/mockba')

### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance":
        old = datetime.strptime("01 Jan 2020", '%d %b %Y')
    if source == "binance":
        new = pd.to_datetime(binance_client.get_klines(
            symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    return old, new
                      

def get_all_binance(symbol, kline_size, save=False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile('historical_data/'+filename):
        data_df = pd.read_csv('historical_data/'+filename)
    else:
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(
        symbol, kline_size, data_df, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    if oldest_point == datetime.strptime("01 Jan 2021", '%d %b %Y'):
        print('Downloading all available %s data for %s. Be patient..!' %
              (kline_size, symbol))
    else:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (
            delta_min, symbol, available_data, kline_size))
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime(
        "%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))  
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close',
                        'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = pd.concat([data_df,temp_df]).drop_duplicates(subset=['close_time'])
        #data_df = data_df.append(temp_df).drop_duplicates(subset=['close_time'])
    else:
        data_df = data.drop_duplicates(subset=['close_time'])
    data_df.set_index('timestamp', inplace=True)
    if save:
         data_df.to_csv('historical_data/'+filename)
    print('All caught up..!')
    return data_df

#get_all_binance("LUNCBUSD", "5m", save=True)