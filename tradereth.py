from binance.client import Client
import apis as api
import sqlite3
import pandas as pd
import requests
import time
import sendmail as sm

api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)
db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
# db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)

print('Trading')
# Variables for trading
invest = float(client.get_asset_balance(asset='USDT')['free']) #400 # Initial value
qty = 0 # Qty buy
counterStopLoss = 0 # Counter to stop when to loose
counterForceSell = 0 # Force sell
#
feeBuy = 0.099921 # 0.9%
feeBuy = (feeBuy / 100) # Binance fee when buy
#
feeSell = 0.1 # 1%
feeSell = (feeSell / 100) # Binance fee sell
fee = 0
################STRATEGY PARAMS############################
###########################################################
params = pd.read_sql('SELECT * FROM parameters',con=db_con)

marginSell = float(params['margingsell'].values) #% last 35% - new 0.5 non stop
marginSell = marginSell / 100 + 1 # Earning from each sell
timeFrameForceSell = int(params['forcesell'].values) # 96 hour 96*60/5, 8 days
#
#
marginBuy = float(params['margingbuy'].values) #% last 3% new 0.5 nonstop
marginBuy = marginBuy / 100 + 1 # Earning from each buy
timeFrameStopLoss = int(params['stoploss'].values) # 24 hour 24*60/5
############################################################
############################################################
#
nextOps = 0
sellFlag = 0
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

# Def update close_time
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
            qty = round(((invest / float(eth[4][499])) - fee) - 0.0001,4)
            nextOps = round(float(eth[4][499]) * marginSell,2)
            sellFlag = 1
            counterForceSell = 1
            data = (qty,nextOps,sellFlag,counterStopLoss,counterForceSell,1,'buy',str(eth[0][499]))
            client.order_market_buy(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            sm.sendMail('First Buy')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # Sell    
        elif float(eth[4][499]) >= float(operations['nextOps'].values) and operations['sellFlag'].values == 1:
            print('Sell')
            balance_eth = float(client.get_asset_balance(asset='ETH')['free'])
            fee = (balance_eth * feeSell)
            qty = round(((balance_eth * float(eth[4][499])) - fee) /  float(eth[4][499]) - 0.0001 ,4)# Sell amount
            print(balance_eth)
            print(feeSell)
            print(fee)
            print(qty)
            print(nextOps)
            nextOps = round(qty / ((qty / float(eth[4][499]) * marginBuy)),2) # Next buy
            print(nextOps)
            counterStopLoss = 1
            sellFlag = 0
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'sell',str(eth[0][499]))
            client.order_market_sell(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            sm.sendMail('Sell')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # force sell     
        elif int(operations['counterForceSell'].values) ==  int(timeFrameForceSell) and operations['sellFlag'].values == 1:
            print('Force Sell')
            fee = (balance_eth * feeSell)
            qty = round(((balance_eth * float(eth[4][499])) - fee) /  float(eth[4][499]) - 0.0001 ,4)# Sell amount
            nextOps = round(qty / ((qty / float(eth[4][499]) * marginBuy)),2) # Next buy
            print(round(qty,4))
            counterStopLoss = 1 
            sellFlag = 0
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'forceSell',str(eth[0][499]))
            client.order_market_sell(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            sm.sendMail('Force Sell')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # Buy     
        elif float(eth[4][499]) <= float(operations['nextOps'].values) and operations['sellFlag'].values == 0:
            print('Buy')
            balance_usdt = float(client.get_asset_balance(asset='USDT')['free'])
            fee = (balance_usdt / float(eth[4][499])) * feeBuy
            qty = round(((balance_usdt / float(eth[4][499])) - fee) - 0.0001,4) # Buy amount
            nextOps = round(float(eth[4][499]) * marginSell,2)
            sellFlag = 1
            counterForceSell = 1 
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'buy',str(eth[0][499]))
            client.order_market_buy(symbol="ETHUSDT", quantity=round(qty,4))
            act_trader_nextOps(data)
            sm.sendMail('Buy')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        elif int(operations['counterStopLoss'].values) ==  int(timeFrameStopLoss) and operations['sellFlag'].values == 0:   
            print('Stop Loss')     
            balance_usdt = float(client.get_asset_balance(asset='USDT')['free'])
            fee = (balance_usdt / float(eth[4][499])) * feeBuy
            qty = ((balance_usdt / float(eth[4][499])) - fee) - 0.0001 # Buy amount
            nextOps = float(eth[4][499]) * marginSell
            sellFlag = 1
            counterForceSell = 1 
            data = (float(qty),float(nextOps),sellFlag,counterStopLoss,counterForceSell,1,'stopLoss',str(eth[0][499]))  
            client.order_market_buy(symbol="ETHUSDT", quantity=round(qty,4))
            act_trader_nextOps(data)
            sm.sendMail('Stop Loss')
            time.sleep(3)
            print('Done...')   
            fee = 0
            qty = 0
            nextOps = 0
        else:
            update_trader_nextOps()
            update_trader_close_time(eth[0][499])
    else:
        print('Waiting candelstick 5m close...........') 
    time.sleep(30)    
