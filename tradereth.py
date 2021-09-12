from binance.client import Client
import apis as api
import sqlite3
import pandas as pd
import requests
import time

api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)
db_con = sqlite3.connect('storage/mockba.db')

print('Trading')
# Variables for trading
invest = 400 # Initial value
qty = 0 # Qty buy
counterStopLoss = 0 # Counter to stop when to loose
counterForceSell = 0 # Force sell
#
feeBuy = 0.099921 # 0.9%
feeBuy = round((feeBuy / 100),9) # Binance fee when buy
#
feeSell = 0.1 # 1%
feeSell = round((feeSell / 100),9) # Binance fee sell
fee = 0
################STRATEGY PARAMS############################
###########################################################
marginSell = 18 #%
marginSell = marginSell / 100 + 1 # Earning from each sell
timeFrameForceSell = 1152 # 96 hour 96*60/5, 8 days
#
#
marginBuy = 3 #%
marginBuy = marginBuy / 100 + 1 # Earning from each buy
timeFrameStopLoss = 288 # 24 hour 24*60/5
############################################################
############################################################
#
nextOps = 0
sellFlag = 0
# asset_balance_coin = client.get_asset_balance(asset='ETH')['free']
#

#
def getTicker():
   url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=5m"
   r = requests.get(url)
   df = pd.DataFrame(r.json()) 
   return df

# Def insert last data ops
def act_trader_nextOps(data):
    sql = ''' INSERT INTO trader(qty,nextOps,sellFlag,counterStopLoss,counterForceSell,counterBuy,ops,close_time)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = db_con.cursor()
    cur.execute(sql, data)
    db_con.commit()

# Def update ops
def update_trader_nextOps():
    sql = 'update trader set counterStopLoss = counterStopLoss + 1, counterForceSell = counterForceSell + 1'
    cur = db_con.cursor()
    cur.execute(sql)
    db_con.commit() 

# Def update clos_time
def update_trader_close_time(close_time):
    sql = "update trader set close_time = '" + str(close_time) + "'"
    cur = db_con.cursor()
    cur.execute(sql)
    db_con.commit()        

# Def get next ops
def getNextOps():
    df = pd.read_sql('SELECT * FROM trader',con=db_con)
    return df

while True:
    # get ticker
    eth = getTicker()
    # Enable o dibale bot
    signal = pd.read_sql('SELECT * FROM t_signal',con=db_con)
    # operations values
    operations = getNextOps()
    if signal['status'].values == 0:
        print('Bot is down') 
    elif operations['close_time'].values != eth[0][499]:
        print('Calculando')
        # Fisrt buy
        if operations['counterBuy'].values == 0:
            print('First Buy')
            fee = (invest / float(eth[4][499])) * feeBuy
            qty = (invest / float(eth[4][499])) - fee
            nextOps = float(eth[4][499]) * marginSell
            sellFlag = 1
            counterForceSell = 1
            data = (qty,nextOps,sellFlag,counterStopLoss,counterForceSell,1,'buy',str(eth[0][499]))
            act_trader_nextOps(data)
            # client.order_market_buy(symbol="ETHUSDT", quantity=qty)
        # Sell    
        elif float(eth[4][499]) >= operations['nextOps'].values and operations['sellFlag'].values == 1:
            print('Sell')
            fee = (operations['qty'].values * float(eth[4][499]) * feeSell)
            qty = (operations['qty'].values * float(eth[4][499]) - fee) # Sell amount
            nextOps = qty / ((qty / float(eth[4][499]) * marginBuy)) # Next buy
            counterStopLoss = 1
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'sell',str(eth[0][499]))
            act_trader_nextOps(data)
            # client.order_market_sell(symbol="ETHUSDT", quantity=qty)
        # force sell     
        elif operations['counterForceSell'].values ==  timeFrameForceSell and operations['sellFlag'].values == 1:
            print('Force Sell')
            fee = (operations['qty'].values * float(eth[4][499]) * feeSell)
            qty = (operations['qty'].values * float(eth[4][499]) - fee) # Sell amount
            nextOps = qty / ((qty / float(eth[4][499]) * marginBuy)) # Next buy
            counterStopLoss = 1 
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'forceSell',str(eth[0][499]))
            act_trader_nextOps(data)
            # client.order_market_sell(symbol="ETHUSDT", quantity=qty) 
        # Buy     
        elif float(eth[4][499]) <= operations['nextOps'].values and operations['sellFlag'].values == 0:
            print('Buy')
            fee = (operations['qty'].values / float(eth[4][499])) * feeBuy
            qty = (operations['qty'].values / float(eth[4][499])) - fee # Buy amount
            nextOps = float(eth[4][499]) * marginSell
            sellFlag = 1
            counterForceSell = 1 
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'buy',str(eth[0][499]))
            act_trader_nextOps(data)
            # client.order_market_buy(symbol="ETHUSDT", quantity=qty)
        elif operations['counterStopLoss'].values ==  timeFrameStopLoss and operations['sellFlag'].values == 0:   
            print('Stop Loss')     
            fee = (operations['qty'].values / float(eth[4][499])) * feeBuy
            qty = (operations['qty'].values / float(eth[4][499])) - fee # Buy amount
            nextOps = float(eth[4][499]) * marginSell
            sellFlag = 1
            counterForceSell = 1 
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'stopLoss',str(eth[0][499]))
            act_trader_nextOps(data)  
            # client.order_market_buy(symbol="ETHUSDT", quantity=qty)    
        else:
            update_trader_nextOps()
            update_trader_close_time(eth[0][499])
    else:
        print('Waiting candelstick 5m close...........') 
    time.sleep(20)    
