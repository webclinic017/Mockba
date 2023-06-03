import os
from dotenv import load_dotenv
import sys
import pandas as pd
import numpy as np
from math import floor
import psycopg2
from decimal import *
#import trend as trend
from indicators import trend
from datetime import datetime
# loading the .env file
load_dotenv()
# access the environment variables
PATH_OPERATIONS = os.getenv("PATH_OPERATIONS")
# Add the path to the system path
sys.path.append(PATH_OPERATIONS)
import operations
db_con = operations.db_con
#GetHistorical
from database import getHistorical

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")

# Def params
def check_params(env, token, pair, timeframe):
    """
    Function to check multiple conditions.
    Parameters:
    env : The enviroment backtest or main.
    token: The user token.
    pair: The pair, ex LUNCBUSD.
    timeframe: Thetimeframe.
    rsi: The rsi value.
    Returns:
    bool: True if all conditions are satisfied, False otherwise.
    """
    global gmessage
    ##First check ma
    ma = pd.read_sql(f"SELECT * FROM {env}.indicators where token = '{token}' and timeframe = '{timeframe}'and pair = '{pair}' and indicator = 'MA'", con=db_con)
    ##Check rsi
    rsi = pd.read_sql(f"SELECT * FROM {env}.indicators where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}' and indicator = 'RSI'", con=db_con)
    ##Check param
    param = pd.read_sql(f"SELECT * FROM {env}.parameters where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}'", con=db_con)
    ##Check table
    check_table_exists = f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{pair}_{timeframe}_{token}';"
    table_exists = pd.read_sql(check_table_exists, db_con).iloc[0, 0] > 0
    if ma.empty:
       return True
    elif rsi.empty:
        return True
    elif param.empty:
        return True 
    elif table_exists:
        return False      
    else:
        return False  

def getMessageGetHistorical():
    return getHistorical.message        

def backtest(values, env, token, timeframe, pair):

    #Fill historical allways before run the process
    getHistorical.get_all_binance(pair, timeframe, token, save=True)
    
    # Retrieving historical data from database
    def get_historical_data():
        table = pair + "_" + timeframe + '_' + str(token)
        f = "'" + values.split('|')[0] + "'"
        t = "'" + values.split('|')[1] + "'"
        query = f"select timestamp close_time"
        query += f" , cast(close as float) as close, close_time as ct"
        query += f'  from public."{table}"'
        query += f"  where timestamp >= {f}"
        query += f"  and timestamp <=  {t}"
        query += f" order by 1"
        #print(query)
        df = pd.read_sql(query, con=db_con, index_col='close_time')
        # df.to_excel("data.xlsx")
        return df

    df = get_historical_data()
    ticker = []
    value = 0
    # Variables for backtest
    position = []
    action = []  # Take action
    invest = float(values.split('|')[2])  # Initial value
    qty = []  # Qty buy
    counterbuy = 0  # Counter how many ops buy
    counterSell = 0  # Counter how manu ops sell
    counterStopLoss = 0  # Counter to stop when to loose
    counterTakeProfit = 0  # Taking profit
    #
    feeBuy = 0.099921  # 0.9%
    feeBuy = round((feeBuy / 100), 9)  # Binance fee when buy
    #
    feeSell = 0.1  # 1%
    feeSell = round((feeSell / 100), 9)  # Binance fee sell
    fee = 0
    # get ma value
    maval = pd.read_sql(
        f"SELECT * FROM {env}.indicators where token = '{token}' and timeframe = '{timeframe}'and pair = '{pair}' and indicator = 'MA'", con=db_con)
    # get rsi value
    rsival = pd.read_sql(
        f"SELECT * FROM {env}.indicators where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}' and indicator = 'RSI'", con=db_con)
    # asigning values
    ma_period = maval['value'][0].astype(int)
    rsi_period = rsival['value'][0].astype(int)
    # # Calculate moving average and RSI
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df = df.dropna(subset=['close'])
    df['ma'] = df['close'].rolling(ma_period).mean()
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    ################ STRATEGY PARAMS############################
    ###########################################################
    trendParams = pd.read_sql(
        f"SELECT * FROM {env}.trend where token = '{token}' and timeframe = '{timeframe}' and pair = '{pair}'", con=db_con)

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
    marginBuy = 0
    StopLoss = 0
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
    vlma = []
    vlrsi = []
    sellflag = 0

    # Def check_conditionsSell
    def check_conditionsSell(close, nextopsval, sellflag, ma, rsi):
        """
        Function to check multiple conditions.

        Parameters:
        close (float): The close value.
        nextopsval (float): The nextopsval value.
        sellflag (int): The sellflag value.
        ma (float): The ma value.
        rsi (float): The rsi value.

        Returns:
        bool: True if all conditions are satisfied, False otherwise.
        """
        return (close >= nextopsval) & (sellflag == 1) & (close < ma) & (rsi < 59)

    # Def check_conditionsBuy
    def check_conditionsBuy(close, nextopsval, sellflag, ma, rsi):
        """
        Function to check multiple conditions.

        Parameters:
        close (float): The close value.
        nextopsval (float): The nextopsval value.
        sellflag (int): The sellflag value.
        ma (float): The ma value.
        rsi (float): The rsi value.

        Returns:
        bool: True if all conditions are satisfied, False otherwise.
        """
        return (close <= nextopsval) and (sellflag == 0) and (close > ma) and (rsi > 59) 
           

    # Def get next ops
    def getNextOps():
        df = pd.read_sql(
            f"SELECT * FROM {env}.trader where token = '{token}' and pair = '{pair}' and timeframe ='{timeframe}'", con=db_con)
        return df


    # Def insert last data ops
    def act_trader_nextOps(data):
        try:
            conn = psycopg2.connect(host=host, database=database, user=user, password=password)
            cursor = conn.cursor()
            # insert data into the database
            sql = f"INSERT INTO {env}.trader(qty,nextopsval,nextOps,sellflag,counterbuy,ops,close_time,trend,token,pair,timeframe) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, data)
            # commit the transaction
            conn.commit()
        except psycopg2.Error as e:
            print("Error:", e)
        finally:
            # close the cursor and connection
            cursor.close()
            if conn is not None:
               conn.close()     

    print("Backtesting in progress, this take time...")
    # Firstly, we are defining a function named ‘get_macd’ 
    # that takes the stock’s price (‘prices’), length of the slow EMA (‘slow’), length 
    # of the fast EMA (‘fast’), and the period of the Signal line (‘smooth’).
    def get_macd(price, slow, fast, smooth):
        exp1 = price.ewm(span = fast, adjust = False).mean()
        exp2 = price.ewm(span = slow, adjust = False).mean()
        macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
        signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
        hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
        frames =  [macd, signal, hist]
        df = pd.concat(frames, join = 'inner', axis = 1)
        #print(df)
        # df.to_excel("get_macd.xlsx")
        return df    

    macd = get_macd(df['close'], 26, 12, 9)
    # # First, we are defining a function named 
    # # implement_macd_strategy which takes the stock prices (‘data’), and MACD 
    # # data (‘data’) as parameters
    # # Inside the function, we are creating three empty lists (buy_price, sell_price, 
    # # and macd_signal) in which the values will be appended while creating the 
    # # trading strategy.
    def implement_macd_strategy(prices, data):    
        buy_price = []
        sell_price = []
        macd_signal = []
        signal = 0

        for i in range(len(data)):
            if data['macd'][i] > data['signal'][i]:
                if signal != 1:
                    buy_price.append(prices[i])
                    sell_price.append(np.nan)
                    signal = 1
                    macd_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)
            elif data['macd'][i] < data['signal'][i]:
                if signal != -1:
                    buy_price.append(np.nan)
                    sell_price.append(prices[i])
                    signal = -1
                    macd_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
                
        return buy_price, sell_price, macd_signal
                
    buy_price, sell_price, macd_signal = implement_macd_strategy(df['close'], macd)


    for i in range(len(macd_signal)):
        if macd_signal[i] > 1:
            position.append(0)
            action.append('')
            qty.append(0)
            nextOps.append(0)
            vltrend.append(0)
            vlmb.append(0)
            vlms.append(0)
            vlfs.append(0)
            vlsl.append(0)
            vlparam.append(0)
            vlma.append(0)
            vlrsi.append(0)
        else:
            position.append(1)
            action.append('')
            qty.append(0)
            nextOps.append(0)
            vltrend.append(0)
            vlmb.append(0)
            vlms.append(0)
            vlfs.append(0)
            vlsl.append(0)
            vlparam.append(0)
            vlma.append(0)
            vlrsi.append(0)

    for i in range(len(df['close'])):
        operations = getNextOps()
        # Check if the DataFrame is empty
        if operations.empty:
            # print("DataFrame is empty")
            data = (0, 0, 'counterBuy', 0, 0, 0, 0, 0, token, pair, timeframe)
            act_trader_nextOps(data)
        # First signals based on macd
        if operations['counterbuy'][0] == 0:
            params = pd.read_sql(
                f"SELECT * FROM {env}.parameters where trend= 'normaltrend' and token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
            marginSell = float(params['margingsell'].values)  # %
            marginSell = marginSell / 100 + 1  # Earning from each sell
            #
            #
            marginBuy = float(params['margingbuy'].values)  # %
            marginBuy = marginBuy / 100 + 1  # Earning from each buy
            StopLoss = float(params['stoploss'].values / 100)  # %
            position[i] = 1
            action[i] = 'firstbuy'
            counterbuy = i
            fee = (invest / df['close'][i]) * feeBuy
            qty[i] = (invest / df['close'][i]) - fee
            vlms[i] = marginSell
            nextOps[i] = df['close'][i] * marginSell
            vlma[i] = df['ma'][i]
            vlrsi[i] = df['rsi'][i]
            sellflag = 1
            counterTakeProfit = 1
            data = (qty[i], nextOps[i], 'sell', sellflag, 1, 'firstbuy', str('444444444'), 'normaltrend', token, pair, timeframe)
            act_trader_nextOps(data)
        # Now implement our margin and sell if signal for rsi and ma
        elif check_conditionsSell(df['close'][i], float(operations['nextopsval'][0]), operations['sellflag'][0], df['ma'][i], df['rsi'][i]):
            # print(i)
            for x in reversed(range(trendParams['trend'][0])):
                # last six periods (5 minutes each, total 30 minutes)
                val = i - x
                value = float(df['close'][val])
                ticker.append(value)
            trendquery = trendResul(trend.trend(ticker))    
            params = pd.read_sql(f"SELECT * FROM {env}.parameters where trend= '{trendquery}' and token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
            marginSell = float(params['margingsell'].values)  # %
            marginSell = marginSell / 100 + 1  # Earning from each sell
            #
            #
            marginBuy = float(params['margingbuy'].values)  # %
            marginBuy = marginBuy / 100 + 1  # Earning from each buy
            StopLoss = float(params['stoploss'].values / 100)  # %
            # print(trendResul(trend.trend(ticker)))
            # print(i)
            # print(ticker)
            vltrend[i] = trend.trend(ticker)
            vlparam[i] = trendResul(trend.trend(ticker))

            vlmb[i] = marginBuy
            vlsl[i] = StopLoss
            vlma[i] = df['ma'][i]
            vlrsi[i] = df['rsi'][i]
            counterSell = i
            fee = (
                ((invest / df['close'][i - (i - counterbuy)]) * df['close'][i])) * feeSell
            qty[i] = (qty[i - (i - counterbuy)] *
                      df['close'][i]) - fee  # Sell amount
            action[i] = 'mySell'
            nextOps[i] = qty[i] / \
                ((qty[i] / df['close'][i]) * marginBuy)  # Next buy
            sellflag = 0
            counterStopLoss = 1
            data = (float(qty[i]), float(nextOps[i]), 'buy', sellflag, 1, 'sell', str(
                '444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
            act_trader_nextOps(data)
            ticker = []
            # print(take_profit)
        # Force sell
        elif (df['close'][i] <= (float(operations['nextopsval'][0]) - ((float(operations['nextopsval'][0]) * StopLoss)))) & (operations['sellflag'][0] == 1):
            for x in reversed(range(trendParams['trend'][0])):
                # last six periods (5 minutes each, total 30 minutes)
                val = i - x
                value = float(df['close'][val])
                ticker.append(value)
            # trend.trend(ticker)
            trendquery = trendResul(trend.trend(ticker))    
            params = pd.read_sql(f"SELECT * FROM {env}.parameters where trend= '{trendquery}' and token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
           
            marginSell = float(params['margingsell'].values)  # %
            marginSell = marginSell / 100 + 1  # Earning from each sell
            #
            #
            marginBuy = float(params['margingbuy'].values)  # %
            marginBuy = marginBuy / 100 + 1  # Earning from each buy
            StopLoss = float(params['stoploss'].values / 100)  # %
            vltrend[i] = trend.trend(ticker)
            vlparam[i] = trendResul(trend.trend(ticker))
            vlmb[i] = marginBuy
            vlsl[i] = StopLoss
            vlma[i] = df['ma'][i]
            vlrsi[i] = df['rsi'][i]
            fee = (
                ((invest / df['close'][i - (i - counterbuy)]) * df['close'][i])) * feeSell
            qty[i] = (qty[i - (i - counterbuy)] *
                      df['close'][i]) - fee  # Sell amount
            nextOps[i] = qty[i] / \
                ((qty[i] / df['close'][i]) * marginBuy)  # Next buy
            sellflag = 0
            counterStopLoss = 1
            action[i] = 'stopLoss'
            counterSell = i
            data = (float(qty[i]), float(nextOps[i]), 'buy', sellflag, 1, 'stopLoss', str(
                '444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
            act_trader_nextOps(data)
            ticker = []
        # Now find the next value for sell or apply stop loss
        elif check_conditionsBuy(df['close'][i], float(operations['nextopsval'][0]), operations['sellflag'][0], df['ma'][i], df['rsi'][i]):
            for x in reversed(range(trendParams['trend'][0])):
                # last six periods (5 minutes each, total 30 minutes)
                val = i - x
                value = float(df['close'][val])
                ticker.append(value)
            # trend.trend(ticker)
            trendquery = trendResul(trend.trend(ticker))    
            params = pd.read_sql(f"SELECT * FROM {env}.parameters where trend= '{trendquery}' and token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
          
            marginSell = float(params['margingsell'].values)  # %
            marginSell = marginSell / 100 + 1  # Earning from each sell
            #
            #
            marginBuy = float(params['margingbuy'].values)  # %
            marginBuy = marginBuy / 100 + 1  # Earning from each buy
            StopLoss = float(params['stoploss'].values / 100)  # %
            vltrend[i] = trend.trend(ticker)
            vlparam[i] = trendResul(trend.trend(ticker))
            vlms[i] = marginSell
            vlsl[i] = StopLoss
            vlma[i] = df['ma'][i]
            vlrsi[i] = df['rsi'][i]
            counterbuy = i
            fee = (qty[i - (i - counterSell)] / df['close'][i]) * feeBuy
            qty[i] = (qty[i - (i - counterSell)] /
                      df['close'][i]) - fee  # Buy amount
            nextOps[i] = df['close'][i] * marginSell
            action[i] = 'myBuy'
            sellflag = 1
            counterTakeProfit = 1
            data = (float(qty[i]), float(nextOps[i]), 'sell', sellflag, 1, 'buy', str(
                '444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
            act_trader_nextOps(data)
            ticker = []
        # Stop Loss after
        elif (df['close'][i] >= (float(operations['nextopsval'][0]) + ((float(operations['nextopsval'][0]) * StopLoss)))) & (operations['sellflag'][0] == 0):
            for x in reversed(range(trendParams['trend'][0])):
                # last six periods (5 minutes each, total 30 minutes)
                val = i - x
                value = float(df['close'][val])
                ticker.append(value)
            # trend.trend(ticker)
            trendquery = trendResul(trend.trend(ticker))    
            params = pd.read_sql(f"SELECT * FROM {env}.parameters where trend= '{trendquery}' and token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
       
            marginSell = float(params['margingsell'].values)  # %
            marginSell = marginSell / 100 + 1  # Earning from each sell
            #
            #
            marginBuy = float(params['margingbuy'].values)  # %
            marginBuy = marginBuy / 100 + 1  # Earning from each buy
            StopLoss = float(params['stoploss'].values / 100)  # %
            vltrend[i] = trend.trend(ticker)
            vlparam[i] = trendResul(trend.trend(ticker))
            vlms[i] = marginSell
            vlsl[i] = StopLoss
            vlma[i] = df['ma'][i]
            vlrsi[i] = df['rsi'][i]
            # print(counterStopLoss)
            action[i] = 'stopLoss'
            counterbuy = i
            fee = (qty[i - (i - counterSell)] / df['close'][i]) * feeBuy
            qty[i] = (qty[i - (i - counterSell)] /
                      df['close'][i]) - fee  # Buy amount
            nextOps[i] = (df['close'][i] * marginSell)
            sellflag = 1
            counterTakeProfit = 1
            data = (float(qty[i]), float(nextOps[i]), 'sell', sellflag, 1, 'stopLoss', str(
                '444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
            act_trader_nextOps(data)
            ticker = []
        elif macd_signal[i] == -1:
            position[i] = 0
            action[i] = ''
            counterStopLoss = counterStopLoss + 1
            counterTakeProfit = counterTakeProfit + 1
        else:
            position[i] = position[i-1]
            counterStopLoss = counterStopLoss + 1
            counterTakeProfit = counterTakeProfit + 1
            vsellflag = operations['sellflag'][0]
            vqty = operations['qty'][0]
            vtrend = operations['trend'][0]
            vnextOps = 0
            vticker = operations['nextopsval'][0]

            for x in reversed(range(trendParams['trend'][0])):
                # last six periods (5 minutes each, total 30 minutes)
                val = i - x
                value = float(df['close'][val])
                ticker.append(value)
            # trend.trend(ticker)
            trendquery = trendResul(trend.trend(ticker))    
            params = pd.read_sql(f"SELECT * FROM {env}.parameters where trend= '{trendquery}' and token = '{token}' and pair = '{pair}' and timeframe = '{timeframe}'", con=db_con)
      
            marginSell = float(params['margingsell'].values)  # %
            marginSell = marginSell / 100 + 1  # Earning from each sell
            #
            #
            marginBuy = float(params['margingbuy'].values)  # %
            marginBuy = marginBuy / 100 + 1  # Earning from each buy
            StopLoss = float(params['stoploss'].values / 100)  # %
            vltrend[i] = trend.trend(ticker)
            vlparam[i] = trendResul(trend.trend(ticker))
            if vsellflag == 1:
                vnextOps = round(vticker * marginSell, 2)
            else:
                vnextOps = round(
                    vqty / ((vqty / vticker * marginBuy)), 2)  # Next buy
            if vtrend != trendResul(trend.trend(ticker)):
                # conditional depending on flags y trend is uptrend and sellflag + 1
                if vsellflag == 1 and trendResul(trend.trend(ticker)) == 'uptrend':
                    data = (float(vqty), float(vnextOps), 'ActTrend' + '-' + trendResul(trend.trend(ticker)), int(sellflag),
                            1, 'ActTrend' + '-' + trendResul(trend.trend(ticker)), str('444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
                    act_trader_nextOps(data)
                elif trendResul(trend.trend(ticker)) == 'downtrend':
                    data = (float(vqty), float(vnextOps), 'ActTrend' + '-' + trendResul(trend.trend(ticker)), int(sellflag),
                            1, 'ActTrend' + '-' + trendResul(trend.trend(ticker)), str('444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
                    act_trader_nextOps(data)
                elif trendResul(trend.trend(ticker)) == 'normaltrend':
                    data = (float(vqty), float(vnextOps), 'ActTrend' + '-' + trendResul(trend.trend(ticker)), int(sellflag),
                            1, 'ActTrend' + '-' + trendResul(trend.trend(ticker)), str('444444444'), trendResul(trend.trend(ticker)), token, pair, timeframe)
                    act_trader_nextOps(data)
            ticker = []
    data = (0, 0, 'counterBuy', 0, 0, 0, 0, 0, token, pair, timeframe)
    act_trader_nextOps(data)
    # macd = df_macd['macd']
    # signal = df_macd['signal']
    close_price = df['close']
    macd_signal = pd.DataFrame(macd_signal).rename(
        columns={0: 'macd_signal'}).set_index(df.index)
    position = pd.DataFrame(position).rename(
        columns={0: 'macd_position'}).set_index(df.index)
    action = pd.DataFrame(action).rename(
        columns={0: 'op_action'}).set_index(df.index)
    qty = pd.DataFrame(qty).rename(columns={0: 'qty'}).set_index(df.index)
    nextOps = pd.DataFrame(nextOps).rename(
        columns={0: 'nextOps'}).set_index(df.index)
    vltrend = pd.DataFrame(vltrend).rename(
        columns={0: 'vltrend'}).set_index(df.index)
    vlmb = pd.DataFrame(vlmb).rename(columns={0: 'MBuy'}).set_index(df.index)
    vlms = pd.DataFrame(vlms).rename(columns={0: 'MSell'}).set_index(df.index)
    vlfs = pd.DataFrame(vlfs).rename(columns={0: 'FSell'}).set_index(df.index)
    vlsl = pd.DataFrame(vlsl).rename(columns={0: 'SLoss'}).set_index(df.index)
    vlma = pd.DataFrame(vlma).rename(columns={0: 'Ma'}).set_index(df.index)
    vlrsi = pd.DataFrame(vlrsi).rename(columns={0: 'Rsi'}).set_index(df.index)
    vlparam = pd.DataFrame(vlparam).rename(
        columns={0: 'vlparam'}).set_index(df.index)
    # frames = [close_price, macd, signal, macd_signal, position, action, qty, nextOps]
    frames = [close_price, action, qty, nextOps,
              vltrend, vlmb, vlms, vlfs, vlsl, vlparam, vlma, vlrsi]
    strategy = pd.concat(frames, join='inner', axis=1)

    #print("The strategy")
    # strategy = strategy[strategy['op_action'] != '0']
    # print(strategy)
    strategy.to_excel(pair + "_" + timeframe + '_' + str(token) + "-strategy.xlsx")

    #print("End")


# start = datetime.now()
# pair = 'LUNCBUSD'
# token = '556159355'
# timeframe = '5m'
# env = 'backtest'
# if check_params(env, token, pair, timeframe):
#    print('No data for this selection, check you have parameter, ma, rsi and historical data for ' + pair + ' of ' + timeframe)
# else:   
#    backtest('2023-05-01|2023-05-02|100',env, token, timeframe, pair)
# print('Tiempo de ejecución  ' + str(datetime.now() - start))
