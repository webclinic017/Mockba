import telebot
import requests
from telebot import types
import sqlite3
import pandas as pd
from binance.client import Client
import indicators.trend as tr
from datetime import datetime
import database.operations as operations
import database.getHistorical as gh


# Telegram Botte voy a 
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

# Def update ops
def paramsAction(data):
    sql = 'insert into parameters (trend, margingsell, margingbuy, forcesell, stoploss) values (?,?,?,?,?)'
    cur = db_con.cursor()
    cur.execute(sql, data)
    db_con.commit()  
    db_con.close 

# Def update ops
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
    item1 = types.KeyboardButton('/Add-Token')
    item2 = types.KeyboardButton('/Delete-Token')
    item3 = types.KeyboardButton('/List-Token')
    item4 = types.KeyboardButton('/Historical')
    item5 = types.KeyboardButton('/backtest')
    item6 = types.KeyboardButton('/Listtrendmarket')
    item7 = types.KeyboardButton('/params')
    item8 = types.KeyboardButton('/trendtime')
    item9 = types.KeyboardButton('/Listparams')
    item10 = types.KeyboardButton('/Listtrendparams')
    item11 = types.KeyboardButton('/List')
    item12 = types.KeyboardButton('/Start')
    markup.row(item1, item2)
    markup.row(item3, item4)
    markup.row(item5, item6)
    markup.row(item7, item8)
    markup.row(item9, item10)
    markup.row(item11, item12)
    bot.send_message(cid, help_text, reply_markup=markup) 


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

@bot.message_handler(commands=['Historical'])
def historical(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemc = types.KeyboardButton('Cancel')
    markup.row(itemc)
    bot.send_message(cid, 'Select your pair in Upper Case, example ETHUBUSD', parse_mode='Markdown', reply_markup=markup)
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
         gh.get_all_binance(gpair, valor, save=True)
         bot.send_message(cid, 'Done !!', parse_mode='Markdown', reply_markup=markup)
       else:    
         bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup) 

##########Add token

@bot.message_handler(commands=['Add-Token'])
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
       item1 = types.KeyboardButton('/Add-Token')
       item = types.KeyboardButton('/List')
       markup.row(item)
       markup.row(item1)
       if int(user['token'].values) == cid:
         addTokenDb(gdata)
         bot.send_message(cid, 'Token added : ' + valor.upper(), parse_mode='Markdown', reply_markup=markup) if gcount == 1 else bot.send_message(cid, 'Error inserting pair: ' + valor.upper() + ', already exists, try again with other value...', parse_mode='Markdown', reply_markup=markup)
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

# @bot.message_handler(commands=['listtrendmarket'])
# def trend(m):
#     cid = m.chat.id
#     markup = types.ReplyKeyboardMarkup()
#     itemd = types.KeyboardButton('/List')
#     markup.row(itemd)
#     if  int(user['token'].values) == cid:
#         trendParams = pd.read_sql("SELECT * FROM trend",con=db_con)
#         bot.send_message(cid, 'Trend in real time ' + str(tr.trendBot(trendParams['trend'][0])), parse_mode='Markdown', reply_markup=markup)                        
#     else:    
#         bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

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
