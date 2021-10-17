from binance.client import Client
import apis as api
import sqlite3
import pandas as pd
import requests
import time
import sendmail as sm
import trend as trend

api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)
db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
# db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)

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
#
nextOps = 0
sellFlag = 0
#

#
def getTicker():
   url = "https://api.binance.com/api/v3/ticker/24hr"
   r = requests.get(url)
   df = pd.DataFrame(r.json()) 
   
   if r.status_code == 200:
      df[(df.symbol == 'ETHUSDT')].filter(["lastPrice"]).values[0][0]   
   return df[(df.symbol == 'ETHUSDT')].filter(["lastPrice"]).values[0][0]

def getTrending():
    url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=5m"
    r = requests.get(url)
    df = pd.DataFrame(r.json()) 
    return df   

# Def insert last data ops
def act_trader_nextOps(data):
    sql = ''' INSERT INTO trader(qty,nextOpsVal,nextOps,sellFlag,counterBuy,ops,close_time,trend)
              VALUES(?,?,?,?,?,?,?,?) '''
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
    trending = getTrending()
    # Enable o dibale bot
    signal = pd.read_sql('SELECT * FROM t_signal',con=db_con)
    # operations values
    operations = getNextOps()
    if signal['status'][0] == 0:
        print('Bot is down') 
    else:
        # print('Calculando')
        # Fisrt buy
        if operations['counterBuy'][0] == 0:
            print('First Buy')
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
            fee = (invest / float(eth)) * feeBuy
            qty = round(((invest / float(eth)) - fee) - 0.0001,4)
            nextOps = round(float(eth) * marginSell,2)
            sellFlag = 1
            data = (qty,nextOps,'sell',sellFlag,1,'firstbuy',str(trending[0][499]),'normaltrend')
            dataHist = (qty,nextOps,'sell',sellFlag,'buy',round(float(eth),2),float(marginBuy),str(trending[0][499]),'normaltrend')
            client.order_market_buy(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('First Buy')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # Sell    
        elif float(eth) >= float(operations['nextOpsVal'][0]) and operations['sellFlag'][0] == 1:
            print('Sell')
            ticker = []
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(trending[4][val])
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
            qty = round(((balance_eth * float(eth)) - fee) /  float(eth) - 0.0001 ,4)# Sell amount
            nextOps = round(qty / ((qty / float(eth) * marginBuy)),2) # Next buy
            # print(nextOps)
            sellFlag = 0
            data = (float(qty),float(nextOps),'buy',sellFlag,1,'sell',str(trending[0][499]),trendResul(trend.trend(ticker)))
            dataHist = (float(qty),float(nextOps),'buy',sellFlag,'sell',round(float(eth),2),float(marginSell),str(trending[0][499]),trendResul(trend.trend(ticker)))
            client.order_market_sell(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Sell')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # force sell     
        elif float(eth) <=  (float(operations['nextOpsVal'][0]) - ((float(operations['nextOpsVal'][0]) * ForceSell))) and operations['sellFlag'][0] == 1:
            print('Force Sell')
            ticker = []
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(trending[4][val])
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
            qty = round(((balance_eth * float(eth)) - fee) /  float(eth) - 0.0001 ,4)# Sell amount
            nextOps = round(qty / ((qty / float(eth) * marginBuy)),2) # Next buy
            # print(round(qty,4))
            sellFlag = 0
            data = (float(qty),float(nextOps),'buy',sellFlag,1,'forceSell',str(trending[0][499]),trendResul(trend.trend(ticker)))
            dataHist = (float(qty),float(nextOps),'buy',sellFlag,'forceSell',round(float(eth),2),float(marginSell),str(trending[0][499]),trendResul(trend.trend(ticker)))
            client.order_market_sell(symbol="ETHUSDT", quantity=qty)
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Force Sell')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        # Buy     
        elif float(eth) <= float(operations['nextOpsVal'][0]) and operations['sellFlag'][0] == 0:
            print('Buy')
            ticker = []
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(trending[4][val])
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
            fee = (balance_usdt / float(eth)) * feeBuy
            qty = round(((balance_usdt / float(eth)) - fee) - 0.0001,4) # Buy amount
            nextOps = round(float(eth) * marginSell,2)
            sellFlag = 1
            data = (float(qty),float(nextOps), 'sell',sellFlag,1,'buy',str(trending[0][499]),trendResul(trend.trend(ticker)))
            dataHist = (float(qty),float(nextOps),'sell',sellFlag,'buy',round(float(eth),2),float(marginBuy),str(trending[0][499]),trendResul(trend.trend(ticker)))
            client.order_market_buy(symbol="ETHUSDT", quantity=round(qty,4))
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Buy')
            time.sleep(3)
            print('Done...')
            fee = 0
            qty = 0
            nextOps = 0
        elif float(eth) >=  (float(operations['nextOpsVal'][0]) + ((float(operations['nextOpsVal'][0]) * StopLoss))) and operations['sellFlag'][0] == 0:   
            print('Stop Loss')
            ticker = [] 
            for i in reversed(range(trendParams['trend'][0])):
                val = 499 - i
                value = float(trending[4][val])
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
            fee = (balance_usdt / float(eth)) * feeBuy
            qty = ((balance_usdt / float(eth)) - fee) - 0.0001 # Buy amount
            nextOps = float(eth) * marginSell
            sellFlag = 1
            data = (float(qty),float(nextOps),'sell',sellFlag,1,'stopLoss',str(trending[0][499]),trendResul(trend.trend(ticker))) 
            dataHist = (float(qty),float(nextOps),'sell',sellFlag,'stopLoss',round(float(eth),2),float(marginBuy),str(trending[0][499]),trendResul(trend.trend(ticker))) 
            client.order_market_buy(symbol="ETHUSDT", quantity=round(qty,4))
            act_trader_nextOps(data)
            act_trader_history(dataHist)
            sm.sendMail('Stop Loss')
            time.sleep(3)
            print('Done...')   
            fee = 0
            qty = 0
            nextOps = 0
        else:
            update_trader_close_time(eth)
            #Change strategy if the trend changes before next ops is true
            ticker = []
            operations = getNextOps()
            vsellFlag = operations['sellFlag'][0]
            vqty = operations['qty'][0]
            vtrend = operations['trend'][0]
            vnextOps = 0
            vticker = operations['nextOpsVal'][0]
            #print(sellFlag)
            #print(qty)
            #print(vtrend)
            # print(trendParams['trend'][0])
            #
            for i in reversed(range(int(trendParams['trend'][0]))):
                val = 499 - i
                value = float(trending[4][val])
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
            if vsellFlag == 1:    
               vnextOps = round(vticker * marginSell,2) 
            else:              
               vnextOps = round(vqty / ((vqty / vticker * marginBuy)),2) # Next buy 
            #print(trendResul(trend.trend(ticker)) )       
            if vtrend != trendResul(trend.trend(ticker)):
               # conditional depending on flags y trend is uptrend and sellflag + 1
               if vsellFlag == 1 and trendResul(trend.trend(ticker)) == 'uptrend':
                  data = (float(vqty),float(vnextOps),'ActTrend' + '-' + trendResul(trend.trend(ticker)),int(sellFlag),1,'ActTrend' + '-' + trendResul(trend.trend(ticker)),str(trending[0][499]),trendResul(trend.trend(ticker)))
                  act_trader_nextOps(data)
               elif  trendResul(trend.trend(ticker)) == 'downtrend':  
                  data = (float(vqty),float(vnextOps),'ActTrend' + '-' + trendResul(trend.trend(ticker)),int(sellFlag),1,'ActTrend' + '-' + trendResul(trend.trend(ticker)),str(trending[0][499]),trendResul(trend.trend(ticker)))
                  act_trader_nextOps(data)
               elif  trendResul(trend.trend(ticker)) == 'normaltrend':  
                  data = (float(vqty),float(vnextOps),'ActTrend' + '-' + trendResul(trend.trend(ticker)),int(sellFlag),1,'ActTrend' + '-' + trendResul(trend.trend(ticker)),str(trending[0][499]),trendResul(trend.trend(ticker)))
                  act_trader_nextOps(data)   
               # print('ActTrend...........' + str(nextOps))      
    time.sleep(20)    
