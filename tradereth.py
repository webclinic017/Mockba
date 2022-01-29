from binance.client import Client
import apis as api
import sqlite3
import pandas as pd
import requests
import time
import sendmail as sm
import trend as trend
from datetime import datetime

api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)
db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
# db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)

now = datetime.now()
# print('Trading')
# Variables for trading
qty = 0 # Qty buy
#
feeBuy = 0.099921 # 0.9%
feeBuy = (feeBuy / 100) # Binance fee when buy
#
feeSell = 0.1 # 1%
feeSell = (feeSell / 100) # Binance fee sell
fee = 0
ticker = []
value = 0
################STRATEGY PARAMS############################
###########################################################
trendParams = pd.read_sql("SELECT * FROM trend",con=db_con)
def trendResul(trend):
    result = 'normaltrend'
    if trend < trendParams['downtrend'][0]:
        result = 'downtrend'
    elif trend > trendParams['uptrend'][0]:
        result = 'uptrend'
    else:
        result = 'normaltrend'  
    return result          

marginSell = 0
ForceSell = 0
marginBuy = 0
StopLoss = 0
############################################################
############################################################
############################################################
############################################################
#
nextOps = []
vltrend = []
vlmb = []
vlms = []
vlfs = []
vlsl = []
vlparam = []
sellFlag = 0

# Def get next ops
def getNextOps():
    df = pd.read_sql('SELECT * FROM trader',con=db_con)
    return df 

#
def getTicker():
    url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1d"
    r = requests.get(url)
    df = pd.DataFrame(r.json()) 
    return df

# Def insert last data ops
def act_trader_nextOps(data):
    sql = ''' INSERT INTO trader(qty,nextOpsVal,nextOps,sellFlag,counterBuy,ops,close_time,trend,updatedAt,price)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = db_con.cursor()
    cur.execute(sql, data)
    db_con.commit()

# Def insert last data ops
def update_trader_nextOps(data):
    sql = "update trader set nextOpsVal = ?, trend = ?, updatedAt = ?"
    cur = db_con.cursor()
    cur.execute(sql, data)
    db_con.commit()    

# Def insert last data ops
def act_trader_history(data):
    sql = ''' INSERT INTO trader_history(qty,nextOpsVal,nextOps,sellFlag,ops,price,margin,close_time,trend)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = db_con.cursor()
    cur.execute(sql, data)
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

# Def get trend periods
def getTrendPeriods():
    df = pd.read_sql('SELECT * FROM trend',con=db_con)
    return df    
    
operations = getNextOps()

while True:
    # get ticker
    eth = getTicker()
    periods = getTrendPeriods()
    # Enable o dibale bot
    signal = pd.read_sql('SELECT * FROM t_signal',con=db_con)
    # operations values
    operations = getNextOps()
    if signal['status'][0] == 0:
        print('Bot is down') 
    elif operations['close_time'].values != eth[0][499]:
        # print('Calculando')
        # Fisrt buy
        if operations['counterBuy'][0] == 0:
            #print('First Buy')
            ticker = []
            params = pd.read_sql("SELECT * FROM parameters where trend= 'normaltrend'",con=db_con)
            marginSell = float(params['margingsell'][0]) #%
            marginSell = marginSell / 100 + 1 # Earning from each sell
            ForceSell = float(params['forcesell'][0] / 100) # %
            #
            #
            marginBuy = float(params['margingbuy'][0]) #%
            marginBuy = marginBuy / 100 + 1 # Earning from each buy
            StopLoss = float(params['stoploss'][0] / 100) # %  
            #
            invest = float(client.get_asset_balance(asset='USDT')['free']) #400 # Initial value
            fee = (invest / float(eth[4][499])) * feeBuy
            qty = round(((invest / float(eth[4][499])) - fee) - 0.0001,4)
            nextOps = round(float(eth[4][499]) * marginSell,2)
            sellFlag = 1
            data = (qty,nextOps,'sell',sellFlag,1,'firstbuy',str(eth[0][499]),'normaltrend',now.strftime("%d/%m/%Y %H:%M:%S"),round(float(eth[4][499]),2))
            dataHist = (qty,nextOps,'sell',sellFlag,'buy',round(float(eth[4][499]),2),float(marginBuy),str(eth[0][499]),'normaltrend')
            client.order_market_buy(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('First Buy')
            time.sleep(3)
            #print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # Sell    
        elif float(eth[4][499]) >= float(operations['nextOpsVal'][0]) and operations['sellFlag'][0] == 1:
            #print('Sell')
            ticker = []
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(eth[4][val])
                ticker.append(value)
            params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
            marginSell = float(params['margingsell'][0]) #%
            marginSell = marginSell / 100 + 1 # Earning from each sell
            ForceSell = float(params['forcesell'][0] / 100) # %
            #
            #
            marginBuy = float(params['margingbuy'][0]) #%
            marginBuy = marginBuy / 100 + 1 # Earning from each buy
            StopLoss = float(params['stoploss'][0] / 100) # %   
            #
            #
            balance_eth = float(client.get_asset_balance(asset='ETH')['free'])
            fee = (balance_eth * feeSell)
            qty = round(((balance_eth * float(eth[4][499])) - fee) /  float(eth[4][499]) - 0.0001 ,4)# Sell amount
            nextOps = round(qty / ((qty / float(eth[4][499]) * marginBuy)),2) # Next buy
            # print(nextOps)
            sellFlag = 0
            data = (float(qty),float(nextOps),'buy',sellFlag,1,'sell',str(eth[0][499]),trendResul(trend.trend(ticker)),now.strftime("%d/%m/%Y %H:%M:%S"),round(float(eth[4][499]),2))
            dataHist = (float(qty),float(nextOps),'buy',sellFlag,'sell',round(float(eth[4][499]),2),float(marginSell),str(eth[0][499]),trendResul(trend.trend(ticker)))
            client.order_market_sell(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Sell')
            time.sleep(3)
            #print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # force sell     
        elif float(eth[4][499]) <=  (float(operations['nextOpsVal'][0]) - ((float(operations['nextOpsVal'][0]) * ForceSell))) and operations['sellFlag'][0] == 1:
            #print('Force Sell')
            ticker = []
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(eth[4][val])
                ticker.append(value)
            params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
            marginSell = float(params['margingsell'][0]) #%
            marginSell = marginSell / 100 + 1 # Earning from each sell
            ForceSell = float(params['forcesell'][0] / 100) # %
            #
            #
            marginBuy = float(params['margingbuy'][0]) #%
            marginBuy = marginBuy / 100 + 1 # Earning from each buy
            StopLoss = float(params['stoploss'][0] / 100) # %   
            #
            #
            balance_eth = float(client.get_asset_balance(asset='ETH')['free'])
            fee = (balance_eth * feeSell)
            qty = round(((balance_eth * float(eth[4][499])) - fee) /  float(eth[4][499]) - 0.0001 ,4)# Sell amount
            nextOps = round(qty / ((qty / float(eth[4][499]) * marginBuy)),2) # Next buy
            # print(round(qty,4))
            sellFlag = 0
            data = (float(qty),float(nextOps),'buy',sellFlag,1,'forceSell',str(eth[0][499]),trendResul(trend.trend(ticker)),now.strftime("%d/%m/%Y %H:%M:%S"),round(float(eth[4][499]),2))
            dataHist = (float(qty),float(nextOps),'buy',sellFlag,'forceSell',round(float(eth[4][499]),2),float(marginSell),str(eth[0][499]),trendResul(trend.trend(ticker)))
            client.order_market_sell(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Force Sell')
            time.sleep(3)
            #print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # Buy     
        elif float(eth[4][499]) <= float(operations['nextOpsVal'][0]) and operations['sellFlag'][0] == 0:
            #print('Buy')
            ticker = []
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(eth[4][val])
                ticker.append(value)
            params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
            marginSell = float(params['margingsell'][0]) #%
            marginSell = marginSell / 100 + 1 # Earning from each sell
            ForceSell = float(params['forcesell'][0] / 100) # %
            #
            #
            marginBuy = float(params['margingbuy'][0]) #%
            marginBuy = marginBuy / 100 + 1 # Earning from each buy
            StopLoss = float(params['stoploss'][0] / 100) # %   
            #
            #
            balance_usdt = float(client.get_asset_balance(asset='USDT')['free'])
            fee = (balance_usdt / float(eth[4][499])) * feeBuy
            qty = round(((balance_usdt / float(eth[4][499])) - fee) - 0.0001,4) # Buy amount
            nextOps = round(float(eth[4][499]) * marginSell,2)
            sellFlag = 1
            data = (float(qty),float(nextOps), 'sell',sellFlag,1,'buy',str(eth[0][499]),trendResul(trend.trend(ticker)),now.strftime("%d/%m/%Y %H:%M:%S"),round(float(eth[4][499]),2))
            dataHist = (float(qty),float(nextOps),'sell',sellFlag,'buy',round(float(eth[4][499]),2),float(marginBuy),str(eth[0][499]),trendResul(trend.trend(ticker)))
            client.order_market_buy(symbol="ETHUSDT", quantity=round(qty,4))
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Buy')
            time.sleep(3)
            #print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        elif float(eth[4][499]) >=  (float(operations['nextOpsVal'][0]) + ((float(operations['nextOpsVal'][0]) * StopLoss))) and operations['sellFlag'][0] == 0:   
            #print('Stop Loss')
            ticker = [] 
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(eth[4][val])
                ticker.append(value)
            params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
            marginSell = float(params['margingsell'][0]) #%
            marginSell = marginSell / 100 + 1 # Earning from each sell
            ForceSell = float(params['forcesell'][0] / 100) # %
            #
            #
            marginBuy = float(params['margingbuy'][0]) #%
            marginBuy = marginBuy / 100 + 1 # Earning from each buy
            StopLoss = float(params['stoploss'][0] / 100) # %   
            #
            #     
            balance_usdt = float(client.get_asset_balance(asset='USDT')['free'])
            fee = (balance_usdt / float(eth[4][499])) * feeBuy
            qty = ((balance_usdt / float(eth[4][499])) - fee) - 0.0001 # Buy amount
            nextOps = float(eth[4][499]) * marginSell
            sellFlag = 1
            data = (float(qty),float(nextOps),'sell',sellFlag,1,'stopLoss',str(eth[0][499]),trendResul(trend.trend(ticker)),now.strftime("%d/%m/%Y %H:%M:%S"),round(float(eth[4][499]),2)) 
            dataHist = (float(qty),float(nextOps),'sell',sellFlag,'stopLoss',round(float(eth[4][499]),2),float(marginBuy),str(eth[0][499]),trendResul(trend.trend(ticker))) 
            client.order_market_buy(symbol="ETHUSDT", quantity=round(qty,4))
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Stop Loss')
            time.sleep(3)
            #print('Done...')   
            fee = 0
            qty = 0
            nextOps = 0
    else:
        #print('Wait candle close 1d')
        update_trader_close_time(eth[0][499])
        #Change strategy if the trend changes before next ops is true
        ticker = []
        operations = getNextOps()
        vsellFlag = operations['sellFlag'][0]
        vqty = operations['qty'][0]
        vtrend = operations['trend'][0]
        vnextOps = 0
        vticker = operations['price'][0]
        vOps = operations['nextOps'][0]
        #print(sellFlag)
        #print(qty)
        #print(vtrend)
        # print(trendParams['trend'][0])
        #
        for i in reversed(range(int(trendParams['trend'][0]))):
            val = 499 - i
            value = float(eth[4][val])
            ticker.append(value)   
        #print(ticker)
        #print(trendResul(trend.trend(ticker))) 
        #print(trend.trend(ticker)) 
        params = pd.read_sql("SELECT * FROM parameters where trend= '" + trendResul(trend.trend(ticker)) + "'",con=db_con)
        marginSell = float(params['margingsell'][0]) #%
        marginSell = marginSell / 100 + 1 # Earning from each sell
        ForceSell = float(params['forcesell'][0] / 100) # %
        #
        #
        marginBuy = float(params['margingbuy'][0]) #%
        marginBuy = marginBuy / 100 + 1 # Earning from each buy
        StopLoss = float(params['stoploss'][0] / 100) # % 
        if vsellFlag == 1:    
            vnextOps = round(vticker * marginSell,2) 
        else:              
            vnextOps = round(vqty / ((vqty / vticker * marginBuy)),2) # Next buy 
        #print(trendResul(trend.trend(ticker)) )       
        if vtrend != trendResul(trend.trend(ticker)):
           data = (float(vnextOps),trendResul(trend.trend(ticker)),now.strftime("%d/%m/%Y %H:%M:%S"))
           #print('Updating')
           update_trader_nextOps(data)        
    time.sleep(20)