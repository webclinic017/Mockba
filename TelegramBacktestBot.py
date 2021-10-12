from os import defpath
import telebot
import apis as api
import requests
from telebot import types
import sqlite3
import pandas as pd
from binance.client import Client
import backtradereth2
import getHistorical
import trend as tr

# Telegram Bot
API_TOKEN = '2096372558:AAFZtSi_8wHrfEQjJatdnYhDtEgkm8TaipM'
db_con = sqlite3.connect('/var/lib/system/storage/mockbabacktest.db', check_same_thread=False)
# db_con = sqlite3.connect('storage/mockbabacktest.db', check_same_thread=False)

# Def get next ops
def getUser():
    df = pd.read_sql('SELECT * FROM t_login',con=db_con)
    return df


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
   url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=5m"
   r = requests.get(url)
   df = pd.DataFrame(r.json()) 
   return df 

bot = telebot.TeleBot(API_TOKEN)
final_result = []
gyear = ""
gmonth = ""
gdata = ""
user = getUser()
########################################################################################################
###############################Operaciones para manejar en el Bot#######################################
########################################################################################################
# only used for console output now

# def listener(messages):
 #   """
 #   When new messages arrive TeleBot will call this function.
 #   """
#    for m in messages:
#        if m.content_type == 'text':
#            # print the sent message to the console
#            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

#    bot.set_update_listener(listener)  # register listener            


# Comando inicio
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    nom = m.chat.first_name
    bot.send_message(cid,
                    "Welcome to Mockba, with this bot you can, backtest, load hitorical data, change parameter for backtest, parameters for trend, list trend, list parameters and check real time trend " + str(nom))
    command_help(m)


@bot.message_handler(commands=['list'])
def command_help(m):
    cid = m.chat.id
    help_text = "Available options."
    markup = types.ReplyKeyboardMarkup()
    iteme = types.KeyboardButton('/backtest')
    itemf = types.KeyboardButton('/trend')
    itemh = types.KeyboardButton('/params')
    itemi = types.KeyboardButton('/trendtime')
    itemj = types.KeyboardButton('/gethistorical')
    itema = types.KeyboardButton('/listparams')
    itemb = types.KeyboardButton('/listtrend')
    itemd = types.KeyboardButton('/list')
    markup.row(iteme)
    markup.row(itemh)
    markup.row(itemi)
    markup.row(itemf)
    markup.row(itemj)
    markup.row(itema)
    markup.row(itemb)
    markup.row(itemd)
    bot.send_message(cid, help_text, reply_markup=markup) 


@bot.message_handler(commands=['listparams'])
def listparams(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        df = pd.read_sql('SELECT * FROM parameters order by id',con=db_con)

        for i in df.index:
            bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nMargingSell: *" + str(df['margingsell'][i]) + "\n*MargingBuy: *" + str(df['margingbuy'][i]) + "\n*ForceSell: *" + str(df['forcesell'][i]) + "\n*StopLoss: *" + str(df['stoploss'][i]) , parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')     

@bot.message_handler(commands=['listtrend'])
def listtrend(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        df = pd.read_sql('SELECT * FROM trend order by id',con=db_con)
        for i in df.index:
            bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nDowntrend: *" + str(df['downtrend'][i]) + "\n*Uptrend: *" + str(df['uptrend'][i]), parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')    
        

@bot.message_handler(commands=['backtest'])
def params(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    bot.send_message(cid, 'Put your params, init date, end data and ticker, @ separated, example 2021-09-01@2021-10-31@ETHUSDT', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, backtestActions)    


def backtestActions(m):
    cid = m.chat.id
    valor = m.text
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        bot.send_message(cid, 'Backtesting, take some time....')
        backtradereth2.backtest(valor)
        bot.send_message(cid, 'Backtest ready, now you can download the excel file !!', parse_mode='Markdown')
        file = open(valor.split('@')[2]+'-strategy.xlsx','rb')
        print(file)
        bot.send_document(cid,file)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

@bot.message_handler(commands=['params'])
def params(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    bot.send_message(cid, 'Put your params, it will update params for trend(normaltrend,uptrend and downtrend), margingsell, margingbuy, forcesell, and stoploss. @ Separated. Example: normaltrend@0.3@0.3@99999999@99999999', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, paramsActions)

def paramsActions(m):
    cid = m.chat.id
    valor = m.text
    global gdata
    gdata = (valor.split('@')[0],valor.split('@')[1],valor.split('@')[2],valor.split('@')[3],valor.split('@')[4])
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        paramsAction(gdata)
        bot.send_message(cid, 'Params has changed...done !!', parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')

@bot.message_handler(commands=['gethistorical'])
def historical(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    bot.send_message(cid, 'Put your params, ticker and time (1m,5m,1h,2h,1d), @ separated, example ETHUSDT@5m', parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, gethistorical)

def gethistorical(m):
    cid = m.chat.id
    valor = m.text
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        bot.send_message(cid, 'Getting historical data, take some time...', parse_mode='Markdown')
        getHistorical.get_all_binance(valor.split('@')[0], valor.split('@')[1], save=True)
        data = pd.read_csv (valor.split('@')[0]+'-'+valor.split('@')[1]+'-data.csv') 
        df = pd.DataFrame(data)
        df.to_sql('historical_' + valor.split('@')[0], if_exists="replace",
             con=db_con, index=True)
        bot.send_message(cid, 'Done !!', parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')        


@bot.message_handler(commands=['trendtime'])
def trendtime(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    bot.send_message(cid, 'Put your time and integer time (2,3,4,5,6,7,8,9,10,etc), downtrend and uptrend @ separated, example 6@-4@6 , it will update trendtime function', parse_mode='Markdown', reply_markup=markup)                        
    bot.register_next_step_handler_by_chat_id(cid, trendtimeActions)

def trendtimeActions(m):
    cid = m.chat.id
    valor = m.text
    global gdata
    gdata = (valor.split('@')[0],valor.split('@')[1],valor.split('@')[2])
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        trendTime(gdata)
        bot.send_message(cid, 'Trend time has changed...done !!', parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown') 

@bot.message_handler(commands=['trend'])
def trend(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        bot.send_message(cid, 'Trend in real time ' + str(tr.trendBot()), parse_mode='Markdown', reply_markup=markup)                        
        bot.register_next_step_handler_by_chat_id(cid, trendtimeActions) 
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')                         

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    global gcodrep
    gcodrep = ""
    markup = types.ReplyKeyboardMarkup()
    iteme = types.KeyboardButton('/list')
    markup.row(iteme)
    bot.send_message(m.chat.id, "Does not understand \"" + m.text + "\"\n , try with \n \n /list" , reply_markup=markup)        

bot.polling()     
