import os
from dotenv import load_dotenv
import telebot
import requests
import json
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd
from binance.client import Client
from indicators import trend as tr
from datetime import datetime
from database import getHistorical
from database import operations
import psycopg2
import webbrowser
import backtradernew as backtrader
#loading trader
#import tradernew

# loading the .env file
load_dotenv()

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")

# Telegram Bot
API_TOKEN = '1042444870:AAHEuYUbs2YJrGDUEfd1ZjvomJafqCStMKM'
db_con = operations.db_con

# Global
final_result = []
gyear = ""
gmonth = ""
gdata = ""
gframe = ""
gpair = ""
gcount = 0
gnext = ""
gp1 = "0"
gp2 = "0"
gp3 = "0"
gp4 = "0"
gp5 = "0"
gavailable = "100"
genv = ""

def getEnv(m):
    cid = m.chat.id
    global genv
    df = pd.read_sql("SELECT env FROM public.t_setenv where token = '" + str(cid) + "'",con=db_con)
    a = df.index.size
    genv = df['env'][0] if a != 0 else ""


# Def get next ops
def getUser(token, env):
    df = pd.read_sql("SELECT * FROM " + env + ".t_login where token = " + str(token) ,con=db_con)
    return df

# Def addtoken
def addTokenDb(data, env):
    global gcount
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into " + env + ".t_pair (pair, token) values (%s, %s)"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()  

# Def copytrade
def copyTrade(data, env):
    global gcount
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"select * from {env}.copy_params(%s, %s, %s)"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()                 

# Def deletetoken
def deleteTokenDb(data, env):
    global gcount
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "delete from " + env + ".t_pair where id = %s and token = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 

# Def paramsAction
def paramsAction(data, env):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into " + env + ".parameters (trend, margingsell, margingbuy, stoploss, token, pair, timeframe, percentage_of_available) values (%s,%s,%s,%s,%s,%s,%s,%s)"
        # print(data, env)
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 

# Def trendTime
def trendTime(data, env):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into " + env + ".trend (trend,token,pair,timeframe,tolerance) values (%s,%s,%s,%s,%s)"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 

# Def indicators, MA and RSI
def add_indicators(data, env):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into " + env + ".indicators (indicator,value,token,timeframe,pair) values (%s,%s,%s,%s,%s)"
        print(data)
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()    

# Def trendTime
def env(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into public.t_setenv (env, token) values (%s, %s)"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 

# Def trendTime
def stopstartbot(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into main.t_bot_status set status = %s where token = %s and pair = %s and timeframe = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()                                             

def getTicker(pair, interval):
   url = "https://api.binance.com/api/v3/klines?symbol="+pair+"E&interval="+interval
   r = requests.get(url)
   df = pd.DataFrame(r.json()) 
   return df 

bot = telebot.TeleBot(API_TOKEN)
########################################################################################################
###############################Operaciones para manejar en el Bot#######################################
########################################################################################################
# only used for console output now
def listener(messages):
   """
   When new messages arrive TeleBot will call this function.
   """
   for m in messages:
       if m.content_type == 'text':
           # print the sent message to the console
           print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

   bot.set_update_listener(listener)  # register listener            


# Comando inicio
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    nom = m.chat.first_name
    bot.send_message(cid,
                    "Welcome to Mockba " + str(nom) + '-' + str(cid) + ", with this bot you can, backtest, load hitorical data, change parameter for backtest, parameters for trend, list trend, list parameters and check real time trend " + str(nom))
    command_list(m)

def clear_message_text(message):
    # edit the message text with an empty string
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='')

@bot.message_handler(commands=['list'])
def command_list(m):
    getEnv(m)
    cid = m.chat.id
    global genv
    help_text = "Available options."
    # Define the buttons
    button1 = InlineKeyboardButton("Set Enviroment (Backtest or Main)", callback_data="SetEnv")
    button2 = InlineKeyboardButton("Start/Stop Bot-Token-Timeframe", callback_data="SetBotStatus")
    button3 = InlineKeyboardButton("Tokens Menu", callback_data="TokensMenu")
    button4 = InlineKeyboardButton("Historical", callback_data="Historical")
    button5 = InlineKeyboardButton("List Menu", callback_data="ListMenu")
    button6 = InlineKeyboardButton("Params Menu", callback_data="ParamsMenu")
    button7 = InlineKeyboardButton("Run Backtest", callback_data="Backtest")
    button8 = InlineKeyboardButton("List", callback_data="List")
    button9 = InlineKeyboardButton("Start", callback_data="Start")

    # Create a nested list of buttons
    if genv == 'backtest':
     buttons = [[button1], [button2], [button3, button4, button5], [button6, button7, button8], [button9]]
    else:
     buttons = [[button1], [button2], [button3, button5], [button6, button8], [button9]]
      

    # Order the buttons in the second row
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)             
    bot.send_message(cid, help_text, reply_markup=reply_markup)


# Callback_Handler
# This code creates a dictionary called options that maps the call.data to the corresponding function. 
# The get() method is used to retrieve the function based on the call.data. If the function exists
# , it is called passing the call.message as argument. 
# This approach avoids the need to use if statements to check the value of call.data for each possible option.
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    # Define the mapping between call.data and functions
    options = {
        'TokensMenu': tokens,
        'AddToken': addToken,
        'DeleteToken': deleteToken,
        'List' : command_list,
        'Historical': historical,
        'ListMenu': listMenu,
        'ListTokens': listTokens,
        'Listtrendmarket': listtrendmarket,
        'Listparams': listparams,
        'ListIndicators': listindicators,
        'Listtrendparams': listtrend,
        'ListBinanceGainers': listBinanceGainers,
        'ListBinanceTopVolume': listBinanceTopVolume,
        'ListBotStatus': listBotStatus,
        'ListEnv': listEnv,
        'ParamsMenu': paramsmenu,
        'SetParams': addparams,
        'SetTrendtime': settrendtime,
        'SetRSIValue': setrsivalue,
        'SetMAValue': setmavalue,
        'SetEnv': setenv,
        'tradingView': tradingView,
        'Backtest': backtest, 
        'CopyBacktestToReal': CopyBacktestToReal,
        'SetBotStatus': SetBotStatus
    }
    # Get the function based on the call.data
    func = options.get(call.data)

    # Call the function if it exists
    if func:
        func(call.message)    
    
def paramsmenu(m):
    cid = m.chat.id
    help_text = "Available options."
    # Define the buttons
    button1 = InlineKeyboardButton("Set Params", callback_data="SetParams")
    button2 = InlineKeyboardButton("Set Trendtime", callback_data="SetTrendtime")
    button3 = InlineKeyboardButton("Set RSIValue", callback_data="SetRSIValue")
    button4 = InlineKeyboardButton("Set MAValue", callback_data="SetMAValue")
    button5 = InlineKeyboardButton("Copy Backtest To Main", callback_data="CopyBacktestToReal")
    button6 = InlineKeyboardButton("<< Back to List", callback_data="List")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4], [button5], [button6]]

    # Order the buttons in the second row
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons) 
    bot.send_message(cid, help_text, reply_markup=reply_markup)        

#@bot.message_handler(commands=['TokensMenu'])
def tokens(m):
    cid = m.chat.id
    help_text = "Available options."
    # Define the buttons
    button1 = InlineKeyboardButton("Add Token", callback_data="AddToken")
    button2 = InlineKeyboardButton("Delete Token", callback_data="DeleteToken")
    button3 = InlineKeyboardButton("<< Back to List", callback_data="List")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3]]

    # Order the buttons in the second row
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)

def listMenu(m):
    cid = m.chat.id
    help_text = "Available options."
    # Define the buttons
    button1 = InlineKeyboardButton("List tokens", callback_data="ListTokens")
    button2 = InlineKeyboardButton("List trend market", callback_data="Listtrendmarket")
    button3 = InlineKeyboardButton("List Params", callback_data="Listparams")
    button4 = InlineKeyboardButton("List Indicators", callback_data="ListIndicators")
    button5 = InlineKeyboardButton("List Trend Params", callback_data="Listtrendparams")
    button6 = InlineKeyboardButton("List Binance Gainers", callback_data="ListBinanceGainers")
    button7 = InlineKeyboardButton("List Binance Top Volume", callback_data="ListBinanceTopVolume")
    button8 = InlineKeyboardButton("List Bot Status (Token-Timeframe)", callback_data="ListBotStatus")
    button9 = InlineKeyboardButton("List Enviroment (Backtest, Main)", callback_data="ListEnv")
    # button10 = InlineKeyboardButton("List Chart TradingView", callback_data="tradingView")
    button11 = InlineKeyboardButton("<< Back to list", callback_data="List")

    # Create a nested list of buttons
    buttons = [[button1], [button2], [button3], [button4], [button5], [button6], [button7], [button8], [button9]]

    # Order the buttons in the second row
    buttons[1].sort(key=lambda btn: btn.text)

    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)    
    bot.send_message(cid, help_text, reply_markup=reply_markup)  

# global
def timeframe(m):
    cid = m.chat.id
    global gpair, gnext, gdata, gcount
    gpair = m.text.upper()
    valor = m.text
    gdata = (valor.upper(),str(cid))
    if gpair == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
       item1 = types.KeyboardButton('1m')
       item2 = types.KeyboardButton('5m')
       item3 = types.KeyboardButton('15m')
       item4 = types.KeyboardButton('1h')
       item5 = types.KeyboardButton('2h')
       item6 = types.KeyboardButton('4h')
       item7 = types.KeyboardButton('1d')
       item = types.KeyboardButton('/list')
       itemc = types.KeyboardButton('CANCEL')
       markup.row(item1, item2, item3)
       markup.row(item4, item5, item6)
       markup.row(item7)
       markup.row(item)
       markup.row(itemc)
       bot.send_message(cid, 'Select your timeframe', parse_mode='Markdown', reply_markup=markup,)   
       bot.register_next_step_handler_by_chat_id(cid, gnext)       

####################################################################################################
#########################Listparams#################################################################
####################################################################################################    

def listparams(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to get the params data', parse_mode='Markdown', reply_markup=markup)
    gnext = params
    bot.register_next_step_handler_by_chat_id(cid, timeframe)
  

def params(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    global gpair, genv
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    user = getUser(cid, genv)
    if  int(user['token'].values) == cid:
        df = pd.read_sql("SELECT * FROM " + genv + ".parameters where token = '" + str(cid) + "' and pair ='" + gpair + "' and timeframe ='" + valor + "' order by id",con=db_con)
        a = df.index.size
        bot.send_message(cid, "You selected " + gpair + " " + valor + " timeframe") 
        for i in df.index:
            bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nmargingsell: *" + str(df['margingsell'][i]) + "\n*margingbuy: *" + str(df['margingbuy'][i]) + "\n*StopLoss: *" + str(df['stoploss'][i]) +  "\n*Available: *" + str(df['percentage_of_available'][i]) if a != 0 else 'No records found' , parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)    
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')    

####################################################################################################
#########################ListIndicators#################################################################
####################################################################################################    
def listindicators(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to get the params data', parse_mode='Markdown', reply_markup=markup)
    gnext = indicators
    bot.register_next_step_handler_by_chat_id(cid, timeframe)
  

def indicators(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    global genv
    user = getUser(cid, genv)
    if  int(user['token'].values) == cid:
        bot.send_message(cid, "*You selected: *" + gpair + " for a timeframe of: " + valor, parse_mode='Markdown')
        df = pd.read_sql("SELECT * FROM " + genv + ".indicators where token = '" + str(cid) + "' and pair ='" + gpair + "' and timeframe ='" + valor + "' order by indicators",con=db_con)
        a = df.index.size
        for i in df.index:
            bot.send_message(cid, "*Indicator: *" + str(df['indicator'][i]) + "*\nValue: *" + str(df['value'][i]) if a != 0 else 'No records found' , parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)   
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')          

##############List trend Params #################################################################

def listtrend(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to get the trend params data', parse_mode='Markdown', reply_markup=markup)
    gnext = listtrendparams
    bot.register_next_step_handler_by_chat_id(cid, timeframe)
 

def listtrendparams(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    global gpair, gframe, genv
    user = getUser(cid, genv)
    if  int(user['token'].values) == cid:
        df = pd.read_sql("SELECT * FROM " + genv + ".trend where token = '" + str(cid) + "' and pair ='" + gpair + "' and timeframe ='" + valor + "' order by id",con=db_con)
        a = df.index.size
        bot.send_message(cid, "*You selected: *" + gpair + " for a timeframe of: " + gframe, parse_mode='Markdown')
        for i in df.index:
            bot.send_message(cid, "Trend: " + str(df['trend'][i]) if a != 0 else 'No records found', parse_mode='Markdown')
            bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)        
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')    

##############List trend Params #################################################################

##############ListBinanceGainers #################################################################
def listBinanceGainers(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext
    # Send the request to the API
    bot.send_message(cid,"-----Fetching from Binance-----")
    response = requests.get(operations.binance_url)
    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response to JSON
        data = json.loads(response.text)
    
        # Get the list of gainers
        gainers = []
        for coin in data:
            if ( not (coin['symbol'].startswith("BUSD") or coin['symbol'].startswith("USDT")) and coin['symbol'].endswith("BUSD") or coin['symbol'].endswith("USDT")) and float(coin['priceChangePercent']) > 15:
                gainers.append(coin)
        
        # Sort the gainers by percentage change
        gainers.sort(key=lambda x: float(x['priceChangePercent']), reverse=True)
    
        # Print the gainers
        bot.send_message(cid, "Top gainers of pairs ending in USDT or BUSD \n")
        for coin in gainers:
            bot.send_message(cid, f"Symbol: {coin['symbol']} Price Change: {format(float(coin['priceChangePercent']),',.2f')}%  Price: {format(float(coin['lastPrice']),',.2f')}", parse_mode='Markdown', reply_markup=markup)
        bot.send_message(cid, 'Done')    
    else:
        # Print an error message
        print("Failed to retrieve market data")
        bot.send_message(cid, "Failed to retrieve market data", parse_mode='Markdown', reply_markup=markup)
##############ListBinanceGainers #################################################################

##############ListBinanceTopVolume #################################################################
def listBinanceTopVolume(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext
    # Send the request to the API
    bot.send_message(cid,"-----Fetching from Binance-----")
    response = requests.get(operations.binance_url)
    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the list of dictionaries from the response
        data = response.json()

        # Filter the list of dictionaries to exclude pairs starting with "BUSD" or "USDT" and ending with "BUSD"
        filtered_data = [d for d in data if not (d['symbol'].startswith("BUSD") or d['symbol'].startswith("USDT")) and d['symbol'].endswith("BUSD") or d['symbol'].endswith("USDT")]

        # Sort the filtered data by the volume in descending order
        sorted_data = sorted(filtered_data, key=lambda x: x['quoteVolume'], reverse=True)

        # Print the top 10 pairs with the highest volume
        bot.send_message(cid,"Top volume of pairs ending in USDT or BUSD \n")
        for i, d in enumerate(sorted_data[:10]):
            bot.send_message(cid,f"{i + 1}. {d['symbol']}: {format(float(d['quoteVolume']),',.2f')}")
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)    
    else:
        # If the request fails, print an error message
        bot.send_message(cid,"Failed to retrieve data from Binance API")
##############ListBinanceGainers #################################################################

##############ListBotStatus #################################################################
def listBotStatus(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    global gpair, gframe
    user = getUser(cid, genv)
    if  int(user['token'].values) == cid:
        df = pd.read_sql("SELECT env FROM maiin.t_bot_status where token = '" + str(cid) + "'",con=db_con)
        a = df.index.size
        for i in df.index:
            bot.send_message(cid, "*Bot status for: *" + str(df['token'][i]) + ' - ' + str(df['pair'][i]) + ' is (0 - up, 1 - down) ' + str(df['status'][i]) if a != 0 else 'No records found', parse_mode='Markdown')
            bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)        
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')
##############ListBotStatus #################################################################

##############ListEnv #################################################################
def listEnv(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    global gpair, gframe
    user = getUser(cid, genv)
    if  int(user['token'].values) == cid:
        df = pd.read_sql("SELECT env FROM public.t_setenv where token = '" + str(cid) + "'",con=db_con)
        a = df.index.size
        for i in df.index:
            bot.send_message(cid, "*Enviroment: *" + str(df['env'][i]) if a != 0 else 'No records found', parse_mode='Markdown')
            bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)        
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')
##############ListEnv #################################################################

##############Trading View #################################################################

def tradingView(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv, gframe
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to print in Trading View', parse_mode='Markdown', reply_markup=markup)
    gnext = printChart
    bot.register_next_step_handler_by_chat_id(cid, timeframe)
 
def printChart(m):
    # get env
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    global gpair, genv
    user = getUser(cid, genv)
    if gpair == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
        if  int(user['token'].values) == cid:
            symbol = 'BINANCE:'+gpair
            chart_url = f'https://www.tradingview.com/chart/?symbol={symbol}'
            webbrowser.open_new_tab(chart_url)     
        else:    
            bot.send_message(cid, "User not autorized", parse_mode='Markdown')   
        
##############Backtest #################################################################
def backtest(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv, gframe
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)
    bot.send_message(cid, 'Add your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
    gnext = paramsdate
    bot.register_next_step_handler_by_chat_id(cid, timeframe)


def paramsdate(m):
    #get env
    cid = m.chat.id
    global gnext, genv, gframe
    gframe = m.text
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)
    bot.send_message(cid, 'Add your date an initial capital, ex, 2023-05-01|2023-05-02|100 user (|) as separator', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, backtestActions)    


def backtestActions(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global genv, gpair, gframe
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(cid, genv)
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
        if  int(user['token'].values) == int(cid):
            start = datetime.now()
            bot.send_message(cid, 'Backtesting in progress, this take time...')
            if backtrader.check_params(genv, cid, gpair, gframe):
               bot.send_message(cid,'No data for this selection, check you have parameter, ma, rsi and historical data for ' + str(gpair) + ' of ' + str(gframe))
            else:  
               backtrader.backtest(valor, genv, cid, gframe, gpair) 
               bot.send_message(cid, 'Execution time  ' + str(datetime.now() - start))
               bot.send_message(cid, 'Backtest ready, now you can download the excel file !!', parse_mode='Markdown')
               file = open(str(gpair) + '_' + str(gframe) + '_' + str(cid) +'.xlsx','rb')
               bot.send_document(cid,file)
        else:    
            bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

##############CopyBacktest #################################################################
def CopyBacktestToReal(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv, gframe
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)
    bot.send_message(cid, 'Add your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
    gnext = copytimeframe
    bot.register_next_step_handler_by_chat_id(cid, timeframe)


def copytimeframe(m):
    #get env
    cid = m.chat.id
    global gnext, genv, gframe
    gframe = m.text
    markup = types.ReplyKeyboardMarkup()
    itema = types.KeyboardButton('Yes, proceed')
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itema)
    markup.row(itemd)
    bot.send_message(cid, 'This operation will stop your bot, copy and replace all the params related, indicators, trend, params for your Pair and timeframe selected, do you want to proceed?', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, executecopy)    


def executecopy(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, genv, gpair, gframe
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    gdata = (cid,gpair,gframe)
    user = getUser(cid, genv)
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
        if  int(user['token'].values) == int(cid):
            copyTrade(gdata, genv)
            bot.send_message(cid, "Copy done...", parse_mode='Markdown', reply_markup=markup)
        else:    
            bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)  

##############setBotStatus #################################################################
def SetBotStatus(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv, gframe
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)
    bot.send_message(cid, 'Add your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
    gnext = statusBot
    bot.register_next_step_handler_by_chat_id(cid, timeframe)


def statusBot(m):
    #get env
    cid = m.chat.id
    global gnext, genv, gframe
    gframe = m.text
    markup = types.ReplyKeyboardMarkup()
    itema = types.KeyboardButton('Start')
    itemb = types.KeyboardButton('Stop')
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itema)
    markup.row(itemb)
    markup.row(itemd)
    bot.send_message(cid, 'This operation will stop or start your bot for the pair and time frame selected', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, startStopBot)    

def startStopBot(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, genv, gpair, gframe
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    gdata = (0 if valor == 'Start' else '1', cid,gpair,gframe)
    user = getUser(cid, genv)
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)  
    else:   
        if  int(user['token'].values) == int(cid):
            startStopBot(gdata)
            bot.send_message(cid, "Done...", parse_mode='Markdown', reply_markup=markup)
        else:    
            bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)                   
            
###############Set params #########################################
###################################################################

def addparams(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)
    bot.send_message(cid, 'Add your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
    gnext = set_params
    bot.register_next_step_handler_by_chat_id(cid, timeframe)

def set_params(m):
    cid = m.chat.id
    global gframe
    markup = types.ReplyKeyboardMarkup()
    normaltrend = types.KeyboardButton('Normaltrend')
    uptrend = types.KeyboardButton('Uptrend')
    downtrend = types.KeyboardButton('Downtrend')
    itemc = types.KeyboardButton('CANCEL')
    gframe = m.text
    markup.row(normaltrend)
    markup.row(uptrend)
    markup.row(downtrend)
    markup.row(itemc)
    bot.send_message(cid, 'Put your params, it will update params for trend(normaltrend,uptrend and downtrend), margingsell, margingbuy stoploss', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, get_p1)

def get_p1(m):
    cid = m.chat.id
    global gp1
    markup = types.ReplyKeyboardMarkup()
    gp1 = m.text
    itemc = types.KeyboardButton('CANCEL')
    markup.row(itemc)
    if gp1 == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else: 
       bot.send_message(cid, 'Put your params to ' + "*" + '**margingsell**' + "*" + " \n\n" + 'Represented by a number, for exmaple 3% would be 3', parse_mode='Markdown', reply_markup=markup)
       bot.register_next_step_handler_by_chat_id(cid, get_p2)

def get_p2(m):
    cid = m.chat.id
    global gp2
    markup = types.ReplyKeyboardMarkup()
    itemc = types.KeyboardButton('CANCEL')
    gp2 = m.text
    markup.row(itemc)
    if gp2 == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else: 
       bot.send_message(cid, 'Put your params to '+ "*" + '**Marginbuy**' + "*" + " \n\n" + 'Represented by a number, for exmaple 3% would be 3', parse_mode='Markdown', reply_markup=markup)
       bot.register_next_step_handler_by_chat_id(cid, get_p4)

def get_p4(m):
    cid = m.chat.id
    global gp4
    markup = types.ReplyKeyboardMarkup()
    itemc = types.KeyboardButton('CANCEL')
    gp4 = m.text
    markup.row(itemc)
    if gp4 == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else: 
       bot.send_message(cid, 'Put your params to '+ "*" + '**Stoploss**' + "*" + " \n\n" + 'Represented by a number, for exmaple 3% would be 3', parse_mode='Markdown', reply_markup=markup)
       bot.register_next_step_handler_by_chat_id(cid, get_p5) 

def get_p5(m):
    cid = m.chat.id
    global gp5
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('25')
    item2 = types.KeyboardButton('30')
    item3 = types.KeyboardButton('33')
    item4 = types.KeyboardButton('50')
    item5 = types.KeyboardButton('75')
    item6 = types.KeyboardButton('100')
    gp5 = m.text
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)
    markup.row(item5)
    markup.row(item6)
    # markup.row(itemc)
    if gp5 == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else: 
       bot.send_message(cid, 'Put your amount you want to trade of your available, no more than 100', parse_mode='Markdown', reply_markup=markup)
       bot.register_next_step_handler_by_chat_id(cid, paramsActions)        
                      

def paramsActions(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gframe, gpair, gp5, genv, gavailable
    user = getUser(cid, genv)
    gavailable = m.text
    gdata = (gp1.lower(), gp2, gp4, gp5,cid,gpair,gframe,gavailable)
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if gavailable == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    if int(gavailable) > 100:  
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'The value can not be greater than 100', parse_mode='Markdown', reply_markup=markup) 
    else: 
       if  int(user['token'].values) == cid:
           paramsAction(gdata, genv)
           bot.send_message(cid, 'Params has changed...done !!', parse_mode='Markdown', reply_markup=markup)
       else:    
           bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)

#####################################################################################################
########## Historical################################################################################
#####################################################################################################
def historical(m):
    # get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to get the historical data', parse_mode='Markdown', reply_markup=markup)
    gnext = gethistorical
    bot.register_next_step_handler_by_chat_id(cid, timeframe)


def gethistorical(m):
    #get env
    getEnv(m)
    global genv
    cid = m.chat.id
    valor = m.text
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       user = getUser(cid, genv)
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       if int(user['token'].values) == cid:
         bot.send_message(cid, 'Getting historical data of ' +  valor + ', this can take some time, be pacient...')
         getHistorical.api_telegram = str(user['token'].values)
         # getHistorical.schema = "backtest"
         getHistorical.get_all_binance(gpair, valor, cid, save=True)
         bot.send_message(cid, 'Done !!', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup) 

##########Add token###############################################################################################
def addToken(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemc = types.KeyboardButton('CANCEL')
    markup.row(itemc)
    bot.send_message(cid, 'Add your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, addTokenActions)

def addTokenActions(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gcount, genv
    gdata = (valor.upper(),str(cid))
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       user = getUser(cid, genv)
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       if int(user['token'].values) == cid:
         addTokenDb(gdata, genv)
         bot.send_message(cid, 'Token added : ' + valor.upper(), parse_mode='Markdown', reply_markup=markup) if gcount == 1 else bot.send_message(cid, 'Error inserting pair: ' + valor.upper() + ', already exists, try again with other value...', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)                 

##########ListToken#####################################################################################################
def listTokens(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    global genv
    user = getUser(cid, genv)
    if  int(user['token'].values) == cid:
        df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
        # print("SELECT * FROM t_pair where token = '" + str(cid) + "' order by id")
        bot.send_message(cid, "List of pairs added:", parse_mode='Markdown')
        for i in df.index:
            bot.send_message(cid, "*Pair: *" + str(df['pair'][i]) , parse_mode='Markdown')

        markup = types.ReplyKeyboardMarkup()
        item = types.KeyboardButton('/list')
        markup.row(item)  
        bot.send_message(cid, "Done..", reply_markup=markup)    
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')  

##########Delete token################################################################################################
def deleteToken(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    global genv
    markup = types.ReplyKeyboardMarkup()
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['id'][i]) + ' - ' + str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want remove', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, deleteokenActions)

def deleteokenActions(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gcount, genv
    gdata = (valor.split(" - ")[0],str(cid))
    if valor == 'Cancel':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       user = getUser(cid, genv)
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       if int(user['token'].values) == cid:
         deleteTokenDb(gdata, genv)
         bot.send_message(cid, 'Token deleted : ' + valor.upper(), parse_mode='Markdown', reply_markup=markup) if gcount == 1 else bot.send_message(cid, 'Error deleting pair: ' + valor.upper() + ', value does not exists, try again with other value...', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)          

##########Trend Time################################################################################################

def settrendtime(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to set the trend', parse_mode='Markdown', reply_markup=markup)
    gnext = trendtime
    bot.register_next_step_handler_by_chat_id(cid, timeframe)

def trendtime(m):
    cid = m.chat.id
    global gnext, gframe
    markup = types.ReplyKeyboardMarkup()
    # itemd = types.KeyboardButton('/list')
    valor = m.text
    gframe = m.text
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:
       gnext = set_params
       bot.send_message(cid, 'Put periods and tolerance for trend. It calculates the N-period moving average (ma) and then determines the trend based on the difference between the last and first values of the moving average with its tolerance, example 5 (ma5), 10 (ma10), 20 (ma20). \n Please add number of periods and tolerance | separated, example 5|0.5', parse_mode='Markdown', reply_markup=markup)                        
       bot.register_next_step_handler_by_chat_id(cid, trendtimeActions)

def trendtimeActions(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gframe, gpair, genv
    user = getUser(cid, genv)
    gdata = (float(valor.split("|")[0]),cid,gpair,gframe, float(valor.split("|")[1])/100)
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        trendTime(gdata, genv)
        bot.send_message(cid, 'Trend time has changed...done !!', parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown') 

##########RSI################################################################################################
def setrsivalue(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to set the RSI', parse_mode='Markdown', reply_markup=markup)
    gnext = rsi
    bot.register_next_step_handler_by_chat_id(cid, timeframe)

def rsi(m):
    cid = m.chat.id
    global gnext, gframe
    markup = types.ReplyKeyboardMarkup()
    # itemd = types.KeyboardButton('/list')
    valor = m.text
    gframe = m.text
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:
       bot.send_message(cid, 'Put your RSI value, eg 14', parse_mode='Markdown', reply_markup=markup)                        
       bot.register_next_step_handler_by_chat_id(cid, setrsi)

def setrsi(m):
    #set env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gframe, gpair, genv
    user = getUser(cid, genv)
    gdata = ("RSI", valor, cid, gframe, gpair)
    # print(gdata)
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        add_indicators(gdata, genv)
        bot.send_message(cid, 'RSI added...done !!', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')

##########MA################################################################################################

def setmavalue(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext, genv
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to set the MA', parse_mode='Markdown', reply_markup=markup)
    gnext = ma
    bot.register_next_step_handler_by_chat_id(cid, timeframe)

def ma(m):
    cid = m.chat.id
    global gnext, gframe
    markup = types.ReplyKeyboardMarkup()
    # itemd = types.KeyboardButton('/list')
    valor = m.text
    gframe = m.text
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:
       bot.send_message(cid, 'Put your MA value, eg 99', parse_mode='Markdown', reply_markup=markup)                        
       bot.register_next_step_handler_by_chat_id(cid, setma)

def setma(m):
    #set env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gframe, gpair, genv
    user = getUser(cid, genv)
    gdata = ("MA", valor, cid, gframe, gpair)
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        # print(gdata)
        add_indicators(gdata, genv)
        bot.send_message(cid, 'MA added...done !!', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)   

##########setenv################################################################################################
def setenv(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    global gnext
    itema = types.KeyboardButton('backtest')
    itemb = types.KeyboardButton('main')
    markup.row(itema)
    markup.row(itemb)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select enviroment (backtest, main)', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, insert_setenv)

def insert_setenv(m):
    #set env
    getEnv(m)
    cid = m.chat.id
    valor = m.text
    global gdata, gframe, gpair, genv
    user = getUser(cid, genv)
    gdata = (valor, cid)
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if valor == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:
       if  int(user['token'].values) == cid:
            env(gdata)
            bot.send_message(cid, f"Enviroment set to {valor}...done !!", parse_mode='Markdown', reply_markup=markup)
       else:    
            bot.send_message(cid, "User not autorized", parse_mode='Markdown')  

             

##########List trend#####################################################################################################

def listtrendmarket(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    global genv
    markup = types.ReplyKeyboardMarkup()
    df = pd.read_sql("SELECT * FROM " + genv + ".t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    itemd = types.KeyboardButton('CANCEL')
    markup.row(itemd)    
    bot.send_message(cid, 'Select the token you want to get the trend data', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, timeframeTrend)

def timeframeTrend(m):
    cid = m.chat.id
    global gpair
    gpair = m.text.upper()

    if gpair == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/list')
       markup.row(item)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       markup = types.ReplyKeyboardMarkup()
       item1 = types.KeyboardButton('1m')
       item2 = types.KeyboardButton('5m')
       item3 = types.KeyboardButton('1h')
       item4 = types.KeyboardButton('2h')
       item5 = types.KeyboardButton('4h')
       item6 = types.KeyboardButton('1d')
       item = types.KeyboardButton('/list')
       itemc = types.KeyboardButton('Cancel')
       markup.row(item1, item2, item3)
       markup.row(item4, item5, item6)
       markup.row(item)
       markup.row(itemc)
       bot.send_message(cid, 'Select your timeframe', parse_mode='Markdown', reply_markup=markup)   
       bot.register_next_step_handler_by_chat_id(cid, trend)

def trend(m):
    #get env
    getEnv(m)
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    valor = m.text
    global gpair, genv
    user = getUser(cid, genv)
    
    if  int(user['token'].values) == cid:
        trendParams = pd.read_sql("SELECT * FROM " + genv + ".trend where token = '" + str(cid) + "' and pair ='" + gpair + "' and timeframe ='" + valor + "'",con=db_con)
        a = trendParams.index.size
        market_prices = tr.trendBot(500, gpair, valor)
        bot.send_message(cid, "You selected " + gpair + " " + valor + " timeframe") 
        bot.send_message(cid, 'Trend in real time is : ' + str(tr.calculate_trend(market_prices, int(trendParams['trend'][0]), int(trendParams['tolerance'][0]))) if a != 0 else 'No records found', parse_mode='Markdown', reply_markup=markup)    
        bot.send_message(cid, "Done..")                     
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    markup = types.ReplyKeyboardMarkup()
    iteme = types.KeyboardButton('/list')
    markup.row(iteme)
    bot.send_message(m.chat.id, "Does not understand \"" + m.text + "\"\n , try with \n \n /list" , reply_markup=markup)        

bot.polling()     
