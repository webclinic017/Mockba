import sqlite3
import pandas as pd

#Cloud
#db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
#Local
db_con = sqlite3.connect('storage/backtest/mockba.db', check_same_thread=False)


# Def get api
# Return the api key
def getApi(token):
    try:
       df = pd.read_sql("SELECT * FROM t_api where token='" + token + "'", con=db_con)
    except Exception as e:
        print(str(e))   
    return df

# print(getApi("556159355"))