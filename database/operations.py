import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

#Cloud
#db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
#Local
#db_con = sqlite3.connect('storage/backtest/mockba.db', check_same_thread=False)

engine = create_engine("postgresql://openbizview:openbizview@localhost:5432/mockba")    
df = ""

# Def get api
# Return the api key
def getApi(token, schema):
    global df
    try:
       df = pd.read_sql("SELECT * FROM " + schema + ".t_api where token='" + token + "'", con=engine)
    except Exception as e:
        print(str(e))   
    return df

# print(getApi("556159355"))