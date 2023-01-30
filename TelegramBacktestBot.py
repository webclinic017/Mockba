import telebot
import requests
from telebot import types
import sqlite3
import pandas as pd
from binance.client import Client
from indicators import trend as tr
from datetime import datetime
from database import getHistorical
from database import operations

# Telegram Bot
API_TOKEN = '2096372558:AAFZtSi_8wHrfEQjJatdnYhDtEgkm8TaipM'
db_con = operations.db_con

# Global
final_result = []
gyear = ""
gmonth = ""
gdata = ""
gframe = ""
gpair = ""
gcount = 0

# Def get next ops
def getUser(token):
    df = pd.read_sql("SELECT * FROM t_login where token = " + str(token) ,con=db_con)
    return df

# Def addtoken
def addTokenDb(data):
    sql = "insert into t_pair (pair, token) values (?,?)"
    global gcount
    try:
        cur = db_con.cursor()
        cur.execute(sql, data)
        gcount = cur.rowcount
        db_con.commit()  
        db_con.close
    except sqlite3.OperationalError:
        gcount = 0  
    except sqlite3.IntegrityError:
        gcount = 0

# Def deletetoken
def deleteTokenDb(data):
    sql = "delete from t_pair where id = ? and token = ?"
    global gcount
    try:
        cur = db_con.cursor()
        cur.execute(sql, data)
        gcount = cur.rowcount
        db_con.commit()  
        db_con.close
    except sqlite3.OperationalError:
        gcount = 0  
    except sqlite3.IntegrityError:
        gcount = 0

# Def paramsAction
def paramsAction(data):
    sql = 'insert into parameters (trend, margingsell, margingbuy, forcesell, stoploss) values (?,?,?,?,?)'
    cur = db_con.cursor()
    cur.execute(sql, data)
    db_con.commit()  
    db_con.close 

# Def trendTime
def trendTime(data):
    sql = 'insert into trend (trend,downtrend,uptrend) values (?,?,?)'
    cur = db_con.cursor()
    cur.execute(sql, data)
    db_con.commit()  
    db_con.close              

def getTicker():
   url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1d"
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
@bot.message_handler(commands=['Start'])
def command_start(m):
    cid = m.chat.id
    nom = m.chat.first_name
    bot.send_message(cid,
                    "Welcome to Mockba " + str(nom) + '-' + str(cid) + ", with this bot you can, backtest, load hitorical data, change parameter for backtest, parameters for trend, list trend, list parameters and check real time trend " + str(nom))
    command_help(m)


@bot.message_handler(commands=['List'])
def command_help(m):
    cid = m.chat.id
    help_text = "Available options."
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('/Tokens')
    item2 = types.KeyboardButton('/Historical')
    item3 = types.KeyboardButton('/Listing')
    item4 = types.KeyboardButton('/backtest')
    item5 = types.KeyboardButton('/params')
    item6 = types.KeyboardButton('/trendtime')
    item7 = types.KeyboardButton('/List')
    item8 = types.KeyboardButton('/Start')
    markup.row(item1, item2)
    markup.row(item3, item4)
    markup.row(item5, item6)
    markup.row(item7, item8)
    bot.send_message(cid, help_text, reply_markup=markup) 

@bot.message_handler(commands=['Tokens'])
def command_tokens(m):
    cid = m.chat.id
    help_text = "Available options."
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('/AddToken')
    item2 = types.KeyboardButton('/DeleteToken')
    item3 = types.KeyboardButton('/List')
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    bot.send_message(cid, help_text, reply_markup=markup)

@bot.message_handler(commands=['Listing'])
def command_tokens(m):
    cid = m.chat.id
    help_text = "Available options."
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('/ListToken')
    item2 = types.KeyboardButton('/Listtrendmarket')
    item3 = types.KeyboardButton('/Listparams')
    item4 = types.KeyboardButton('/Listtrendparams')
    item5 = types.KeyboardButton('/List')
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)
    markup.row(item5)
    bot.send_message(cid, help_text, reply_markup=markup)     

####################################################################################################
####################################################################################################
####################################################################################################    

# @bot.message_handler(commands=['listparams'])
# def listparams(m):
#     cid = m.chat.id
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     if  int(user['token'].values) == cid:
#         df = pd.read_sql('SELECT * FROM parameters order by id',con=db_con)

#         for i in df.index:
#             bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nMargingSell: *" + str(df['margingsell'][i]) + "\n*MargingBuy: *" + str(df['margingbuy'][i]) + "\n*ForceSell: *" + str(df['forcesell'][i]) + "\n*StopLoss: *" + str(df['stoploss'][i]) , parse_mode='Markdown')
#         bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
#     else:    
#         bot.send_message(cid, "User not autorized", parse_mode='Markdown')     

# @bot.message_handler(commands=['listtrendparams'])
# def listtrend(m):
#     cid = m.chat.id
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     if  int(user['token'].values) == cid:
#         df = pd.read_sql('SELECT * FROM trend order by id',con=db_con)
#         for i in df.index:
#             bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nDowntrend: *" + str(df['downtrend'][i]) + "\n*Uptrend: *" + str(df['uptrend'][i]), parse_mode='Markdown')
#         bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
#     else:    
#         bot.send_message(cid, "User not autorized", parse_mode='Markdown')    
        

# @bot.message_handler(commands=['backtest'])
# def params(m):
#     cid = m.chat.id
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     bot.send_message(cid, 'Put your params, init date, end data, ticker and invest, @ separated, example 2021-09-01@2021-10-31@ETHUSDT1d@400', parse_mode='Markdown', reply_markup=markup)
#     bot.register_next_step_handler_by_chat_id(cid, backtestActions)    


# def backtestActions(m):
#     cid = m.chat.id
#     valor = m.text
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     if  int(user['token'].values) == cid:
#         start = datetime.now()
#         bot.send_message(cid, 'Backtesting, this can take some time....')
#         backtradereth2.backtest(valor)  
#         bot.send_message(cid, 'Execution time  ' + str(datetime.now() - start))
#         bot.send_message(cid, 'Backtest ready, now you can download the excel file !!', parse_mode='Markdown')
#         file = open(valor.split('@')[2]+'-strategy.xlsx','rb')
#         print(file)
#         bot.send_document(cid,file)
#     else:    
#         bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

# @bot.message_handler(commands=['params'])
# def params(m):
#     cid = m.chat.id
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     bot.send_message(cid, 'Put your params, it will update params for trend(normaltrend,uptrend and downtrend), margingsell, margingbuy, forcesell, and stoploss. @ Separated. Example: normaltrend@0.3@0.3@99999999@99999999', parse_mode='Markdown', reply_markup=markup)
#     bot.register_next_step_handler_by_chat_id(cid, paramsActions)

# def paramsActions(m):
#     cid = m.chat.id
#     valor = m.text
#     global gdata
#     gdata = (valor.split('@')[0],valor.split('@')[1],valor.split('@')[2],valor.split('@')[3],valor.split('@')[4])
#     ##markup = types.ReplyKeyboardMarkup()
#     ##itemd = types.KeyboardButton('/List')
#     ##markup.row(itemd)
#     if  int(user['token'].values) == cid:
#         paramsAction(gdata)
#         bot.send_message(cid, 'Params has changed...done !!', parse_mode='Markdown')
#     else:    
#         bot.send_message(cid, "User not autorized", parse_mode='Markdown')

########## Historical

@bot.message_handler(commands=['Historical'])
def historical(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    df = pd.read_sql("SELECT * FROM t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    bot.send_message(cid, 'Select the token you want to get the historical data', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, timeframe)

def timeframe(m):
    cid = m.chat.id
    global gpair
    gpair = m.text.upper()
    if gpair == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/Start')
       item1 = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       markup = types.ReplyKeyboardMarkup()
       item1 = types.KeyboardButton('1m')
       item2 = types.KeyboardButton('5m')
       item3 = types.KeyboardButton('1h')
       item4 = types.KeyboardButton('2h')
       item5 = types.KeyboardButton('4h')
       item6 = types.KeyboardButton('1d')
       item = types.KeyboardButton('/List')
       itemc = types.KeyboardButton('Cancel')
       markup.row(item1, item2, item3)
       markup.row(item4, item5, item6)
       markup.row(item)
       markup.row(itemc)
       bot.send_message(cid, 'Select your timeframe', parse_mode='Markdown', reply_markup=markup)   
       bot.register_next_step_handler_by_chat_id(cid, gethistorical)

def gethistorical(m):
    cid = m.chat.id
    valor = m.text
    if valor == 'Cancel':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/Start')
       item1 = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       user = getUser(cid)
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/List')
       markup.row(item)
       if int(user['token'].values) == cid:
         bot.send_message(cid, 'Getting historical data of ' +  valor + ', this can take some time, be pacient...')
         getHistorical.api_telegram = str(user['token'].values)
         getHistorical.get_all_binance(gpair, valor, save=True)
         bot.send_message(cid, 'Done !!', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup) 

##########Add token

@bot.message_handler(commands=['AddToken'])
def addToken(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemc = types.KeyboardButton('Cancel')
    markup.row(itemc)
    bot.send_message(cid, 'Add your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, addTokenActions)

def addTokenActions(m):
    cid = m.chat.id
    valor = m.text
    global gdata, gcount
    gdata = (valor.upper(),str(cid))
    if valor == 'Cancel':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/Start')
       item1 = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       user = getUser(cid)
       markup = types.ReplyKeyboardMarkup()
       item1 = types.KeyboardButton('/AddToken')
       item2 = types.KeyboardButton('/ListToken')
       item = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       markup.row(item2)
       if int(user['token'].values) == cid:
         addTokenDb(gdata)
         bot.send_message(cid, 'Token added : ' + valor.upper(), parse_mode='Markdown', reply_markup=markup) if gcount == 1 else bot.send_message(cid, 'Error inserting pair: ' + valor.upper() + ', already exists, try again with other value...', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)                 

##########ListToken

@bot.message_handler(commands=['ListToken'])
def listtokens(m):
    cid = m.chat.id
    user = getUser(cid)
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/List')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        df = pd.read_sql("SELECT * FROM t_pair where token = '" + str(cid) + "' order by id",con=db_con)
        # print("SELECT * FROM t_pair where token = '" + str(cid) + "' order by id")
        for i in df.index:
            bot.send_message(cid, "*Pair: *" + str(df['pair'][i]) , parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')  

##########Delete token

@bot.message_handler(commands=['DeleteToken'])
def deleteoken(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    df = pd.read_sql("SELECT * FROM t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['id'][i]) + ' - ' + str(df['pair'][i]))
        markup.row(itemc)
    bot.send_message(cid, 'Select the token you want remove', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, deleteokenActions)

def deleteokenActions(m):
    cid = m.chat.id
    valor = m.text
    global gdata, gcount
    gdata = (valor.split(" - ")[0],str(cid))
    if valor == 'Cancel':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/Start')
       item1 = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       user = getUser(cid)
       markup = types.ReplyKeyboardMarkup()
       item1 = types.KeyboardButton('/AddToken')
       item2 = types.KeyboardButton('/ListToken')
       item = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       markup.row(item2)
       if int(user['token'].values) == cid:
         deleteTokenDb(gdata)
         bot.send_message(cid, 'Token deleted : ' + valor.upper(), parse_mode='Markdown', reply_markup=markup) if gcount == 1 else bot.send_message(cid, 'Error deleting pair: ' + valor.upper() + ', value does not exists, try again with other value...', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)          

# @bot.message_handler(commands=['trendtime'])
# def trendtime(m):
#     cid = m.chat.id
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     bot.send_message(cid, 'Put your time and integer time (2,3,4,5,6,7,8,9,10,etc), downtrend and uptrend @ separated, example 6@-4@6 , it will update trendtime function', parse_mode='Markdown', reply_markup=markup)                        
#     bot.register_next_step_handler_by_chat_id(cid, trendtimeActions)

# def trendtimeActions(m):
#     cid = m.chat.id
#     valor = m.text
#     global gdata
#     gdata = (valor.split('@')[0],valor.split('@')[1],valor.split('@')[2])
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     if  int(user['token'].values) == cid:
#         trendTime(gdata)
#         bot.send_message(cid, 'Trend time has changed...done !!', parse_mode='Markdown')
#     else:    
#         bot.send_message(cid, "User not autorized", parse_mode='Markdown') 

##########List trend
@bot.message_handler(commands=['Listtrendmarket'])
def historical(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    df = pd.read_sql("SELECT * FROM t_pair where token = '" + str(cid) + "' order by id",con=db_con)
    for i in df.index:
        itemc = types.KeyboardButton(str(df['pair'][i]))
        markup.row(itemc)
    bot.send_message(cid, 'Select the token you want to get the trend data', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, timeframeTrend)

def timeframeTrend(m):
    cid = m.chat.id
    global gpair
    gpair = m.text.upper()
    if gpair == 'CANCEL':
       markup = types.ReplyKeyboardMarkup()
       item = types.KeyboardButton('/Start')
       item1 = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       bot.send_message(cid, 'Select your option', parse_mode='Markdown', reply_markup=markup)
    else:   
       markup = types.ReplyKeyboardMarkup()
       item1 = types.KeyboardButton('1m')
       item2 = types.KeyboardButton('5m')
       item3 = types.KeyboardButton('1h')
       item4 = types.KeyboardButton('2h')
       item5 = types.KeyboardButton('4h')
       item6 = types.KeyboardButton('1d')
       item = types.KeyboardButton('/List')
       itemc = types.KeyboardButton('Cancel')
       markup.row(item1, item2, item3)
       markup.row(item4, item5, item6)
       markup.row(item)
       markup.row(itemc)
       bot.send_message(cid, 'Select your timeframe', parse_mode='Markdown', reply_markup=markup)   
       bot.register_next_step_handler_by_chat_id(cid, trend)

def trend(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/List')
    markup.row(itemd)
    valor = m.text
    user = getUser(cid)
    if  int(user['token'].values) == cid:
        trendParams = pd.read_sql("SELECT * FROM trend where token = '" + str(cid) + "' and pair ='" + valor + "'",con=db_con)
        a = trendParams.index.size
        print(gpair, valor)
        bot.send_message(cid, 'Trend in real time ' + str(tr.trendBot(trendParams['trend'][0],gpair, valor)) if a != 0 else 'No records found', parse_mode='Markdown', reply_markup=markup)                        
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    global gcodrep
    gcodrep = ""
    markup = types.ReplyKeyboardMarkup()
    iteme = types.KeyboardButton('/List')
    markup.row(iteme)
    bot.send_message(m.chat.id, "Does not understand \"" + m.text + "\"\n , try with \n \n /List" , reply_markup=markup)        

bot.polling()     
