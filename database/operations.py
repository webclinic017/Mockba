import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# loading the .env file
load_dotenv()

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")
 
db_con = create_engine("postgresql://"+str(user)+":"+str(password)+"@"+str(host)+":5432/"+str(database))  
df = ""
# Binance API URL
binance_url = "https://api.binance.com/api/v3/ticker/24hr"

# Def get api
# Return the api key
def getApi(token, schema):
    global df
    try:
       df = pd.read_sql("SELECT * FROM " + schema + ".t_api where token='" + token + "'", con=db_con)
    except Exception as e:
        print(str(e))   
    return df

# print(getApi("556159355", "backtest"))