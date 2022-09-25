import sqlite3
import pandas as pd

#Cloud
#db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
#Local
#db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)
#Backtest
db_con = sqlite3.connect('storage/mockbabacktest.db', check_same_thread=False)

# Def get api
# Return the api key
def getApi(token):
    df = pd.read_sql("SELECT * FROM t_api where token='" + token + "'", con=db_con)
    return df

#print(getNextOps("556159355"))