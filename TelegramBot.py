from os import defpath, error
import telebot
import apis as api
import requests
from telebot import types
import sqlite3
import pandas as pd
from binance.client import Client
import trend as tr


# Telegram Bot
API_TOKEN = ''
api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)
db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)
##db_con = sqlite3.connect('/opt/domgarmining/storage/mockba.db', check_same_thread=False)
# db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)

# Def get next ops
def getUser(token):
    df = pd.read_sql("SELECT * FROM t_login where token = '" + token + "'" ,con=db_con)
    return df

# Def update ops
def enable_bot():
    sql = 'update t_signal set status = 1'
    cur = db_con.cursor()
    cur.execute(sql)
    db_con.commit() 
    db_con.close

# Def update ops
def disable_bot():
    sql = 'update t_signal set status = 0'
    cur = db_con.cursor()
    cur.execute(sql)
    db_con.commit()  
    db_con.close

# Def update ops
def restart_bot():
    sql = "insert into trader values (0,0,0,0,0,0,0,'normaltrend','0','0')"
    cur = db_con.cursor()
    cur.execute(sql)
    db_con.commit()  
    db_con.close  

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
final_result = []
gyear = ""
gmonth = ""
gdata = ""
########################################################################################################
###############################Operaciones para manejar en el Bot#######################################
########################################################################################################
# only used for console output now
'''    
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

    bot.set_update_listener(listener)  # register listener            
'''

# Comando inicio
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    nom = m.chat.first_name
    bot.send_message(cid,
                    "Welcome to Mockba " + str(cid))
    command_help(m)


@bot.message_handler(commands=['list'])
def command_help(m):
    cid = m.chat.id
    help_text = "Available options."
    markup = types.ReplyKeyboardMarkup()
    itema = types.KeyboardButton('/tradehistory')
    itemb = types.KeyboardButton('/enablebot')
    itemc = types.KeyboardButton('/disablebot')
    iteme = types.KeyboardButton('/trader')
    itemj = types.KeyboardButton('/listtrendmarket')
    itemk = types.KeyboardButton('/listparams')
    iteml = types.KeyboardButton('/listtrendparams')
    itemf = types.KeyboardButton('/botstatus')
    itemg = types.KeyboardButton('/resetbot')
    itemh = types.KeyboardButton('/params')
    itemi = types.KeyboardButton('/trendtime')
    itemd = types.KeyboardButton('/list')
    markup.row(itema)
    markup.row(iteme)
    markup.row(itemb)
    markup.row(itemj)
    markup.row(itemk)
    markup.row(iteml)
    markup.row(itemc)
    markup.row(itemg)
    markup.row(itemh)
    markup.row(itemi)
    markup.row(itemf)
    markup.row(itemd)
    bot.send_message(cid, help_text, reply_markup=markup) 




@bot.message_handler(commands=['listparams'])
def listparams(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    # print(cid)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        df = pd.read_sql('SELECT * FROM parameters order by id',con=db_con)

        for i in df.index:
            bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nMargingSell: *" + str(df['margingsell'][i]) + "\n*MargingBuy: *" + str(df['margingbuy'][i]) + "\n*ForceSell: *" + str(df['forcesell'][i]) + "\n*StopLoss: *" + str(df['stoploss'][i]) , parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')     

@bot.message_handler(commands=['listtrendparams'])
def listtrend(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        df = pd.read_sql('SELECT * FROM trend order by id',con=db_con)
        for i in df.index:
            bot.send_message(cid, "*Trend: *" + str(df['trend'][i]) + "*\nDowntrend: *" + str(df['downtrend'][i]) + "\n*Uptrend: *" + str(df['uptrend'][i]), parse_mode='Markdown')
        bot.send_message(cid, 'Done', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')        


@bot.message_handler(commands=['listtrendmarket'])
def trend(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        trendParams = pd.read_sql("SELECT * FROM trend",con=db_con)
        bot.send_message(cid, 'Trend in real time ' + str(tr.trendBot(trendParams['trend'][0])), parse_mode='Markdown', reply_markup=markup)                    
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown') 
        
@bot.message_handler(commands=['enablebot'])
def actautobot(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if int(user['token'].values) == cid:
        enable_bot()
        bot.send_message(cid, "Bot enabled....", parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(commands=['disablebot'])
def dautobot(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        disable_bot()
        bot.send_message(cid, "Bot disabled....", parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown') 

@bot.message_handler(commands=['tradehistory'])
def years(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('2022')
    item2 = types.KeyboardButton('2023')
    item3 = types.KeyboardButton('2024')
    item4 = types.KeyboardButton('2025')
    item5 = types.KeyboardButton('2026')
    itemb = types.KeyboardButton('/list')
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)
    markup.row(item5)
    markup.row(itemb)
    bot.send_message(cid, "Select year:", parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, months)

def months(m):
    cid = m.chat.id
    valor = m.text
    global gyear
    gyear = valor
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('01')
    item2 = types.KeyboardButton('02')
    item3 = types.KeyboardButton('03')
    item4 = types.KeyboardButton('04')
    item5 = types.KeyboardButton('05')
    item6 = types.KeyboardButton('06')
    item7 = types.KeyboardButton('07')
    item8 = types.KeyboardButton('08')
    item9 = types.KeyboardButton('09')
    item10 = types.KeyboardButton('10')
    item11 = types.KeyboardButton('11')
    item12 = types.KeyboardButton('12')
    itemb = types.KeyboardButton('/list')
    markup.row(item1, item2, item3, item4)
    markup.row(item5, item6, item7, item8)
    markup.row(item9, item10, item11, item12)
    markup.row(itemb)
    bot.send_message(cid, "Select month:", parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(cid, trade)                

def trade(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        query  = "select qty, nextOpsVal, nextOps, sellFlag, ops, price, margin, STRFTIME('%d/%m/%Y %H:%M',datetime(close_time/1000, 'unixepoch')) close_time, trend from trader_history"
        query += " where STRFTIME('%Y',datetime(close_time/1000, 'unixepoch')) = '" + gyear + "'"
        query += " and STRFTIME('%m',datetime(close_time/1000, 'unixepoch')) = '" + m.text + "'"
        df = pd.read_sql(query,con=db_con)
        bot.send_message(cid, 'Generating file......')
        df.to_csv("History-" + gyear + '-' + m.text + '.csv',  index=False)
        file = open("History-" + gyear + '-' + m.text + '.csv')
        print(file)
        bot.send_document(cid,file)
        # for i in df.index:
         #   bot.send_message(cid, 'Close time: ' +  str(df['close_time'][i]) + "\n Next Ops: " + str(df['nextOps'][i]) + " \n Op: " + str(df['ops'][i]) + " \n Qty: " + str(df['qty'][i]), parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')

@bot.message_handler(commands=['trader'])
def trader(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    params = pd.read_sql('SELECT * FROM parameters where trend = (select trend from trader)',con=db_con)
    balance_usdt = float(client.get_asset_balance(asset='USDT')['free'])
    balance_eth = float(client.get_asset_balance(asset='ETH')['free'])
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        query  = "select * from trader"
        df = pd.read_sql(query,con=db_con)
        eth = getTicker()
        for i in df.index:
            balanceEth = "{:2,.4f}".format(balance_eth)
            balanceUsdt = "{:2,.4f}".format(balance_usdt)
            bot.send_message(cid, 'Qty: ' +  str(df['qty'][i]) 
            + "\n Next Ops Value: " + str(df['nextOpsVal'][i]) 
            + "\n Next Ops: " + str(df['nextOps'][i]) 
            + " \n sellFlag: " + str(df['sellFlag'][i]) 
            + " \n Ops: "      + str(df['ops'][i]) 
            + " \n Trend: " + df['trend'][0] 
            + " \n Margin Sell: " + str(params['margingsell'][0]) + " %" 
            + " \n Margin buy: " + str(params['margingbuy'][0]) + " %"
            + " \n ForceSell: " + str(params['forcesell'][0]) + " % "
            + " \n StopLoss: " + str(params['stoploss'][0]) + " % "
            + " \n UpdatedAt: " + str(df['updatedAt'][0]) + ""
            + " \n Ticker: " + str(eth[4][499]) 
            + " \n\n Balance ETH: " + balanceEth + " \n Balance USDT: " 
            + str(balanceUsdt), parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')
    balance_usdt = 0
    balance_eth = 0 
    balanceUsdt = 0
    balanceEth = 0   

@bot.message_handler(commands=['botstatus'])
def botstatus(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        query  = "select case when status = '1' then 'Bot enabled' else 'Bot disabled' end status from t_signal"
        df = pd.read_sql(query,con=db_con)
        for i in df.index:
            bot.send_message(cid, 'Status: ' +  str(df['status'][i]), parse_mode='Markdown')
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown')  

@bot.message_handler(commands=['resetbot'])
def resetbot(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        restart_bot()
        bot.send_message(cid, 'All operations start from cero...done !!', parse_mode='Markdown')
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
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        paramsAction(gdata)
        bot.send_message(cid, 'Params has changed...done !!', parse_mode='Markdown')
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
    user = getUser(str(cid))
    if  int(user['token'].values) == cid:
        trendTime(gdata)
        bot.send_message(cid, 'Trend time has changed...done !!', parse_mode='Markdown')
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
