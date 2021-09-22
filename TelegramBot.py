from os import defpath
import telebot
import requests
from telebot import types
import sqlite3
import pandas as pd

# Telegram Bot
API_TOKEN = '1042444870:AAHEuYUbs2YJrGDUEfd1ZjvomJafqCStMKM'
db_con = sqlite3.connect('/var/lib/system/storage/mockba.db', check_same_thread=False)

# Def get next ops
def getUser():
    df = pd.read_sql('SELECT * FROM t_login',con=db_con)
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
    sql = 'insert into trader values (0,0,0,0,0,0,0,0)'
    cur = db_con.cursor()
    cur.execute(sql)
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
user = getUser()
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
                    "Welcome to Mockba " + str(nom))
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
    itemf = types.KeyboardButton('/botstatus')
    itemg = types.KeyboardButton('/resetbot')
    itemd = types.KeyboardButton('/list')
    markup.row(itema)
    markup.row(iteme)
    markup.row(itemf)
    markup.row(itemb)
    markup.row(itemc)
    markup.row(itemg)
    markup.row(itemd)
    bot.send_message(cid, help_text, reply_markup=markup) 


@bot.message_handler(commands=['enablebot'])
def actautobot(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
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
    if  int(user['token'].values) == cid:
        disable_bot()
        bot.send_message(cid, "Bot disabled....", parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup) 

@bot.message_handler(commands=['tradehistory'])
def years(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('2021')
    item2 = types.KeyboardButton('2022')
    item3 = types.KeyboardButton('2023')
    item4 = types.KeyboardButton('2024')
    item5 = types.KeyboardButton('2025')
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
    if  int(user['token'].values) == cid:
        query  = "select qty, nextOps, ops, STRFTIME('%d/%m/%Y %H:%M',datetime(close_time/1000, 'unixepoch')) close_time from trader_history"
        query += " where STRFTIME('%Y',datetime(close_time/1000, 'unixepoch')) = '" + gyear + "'"
        query += " and STRFTIME('%m',datetime(close_time/1000, 'unixepoch')) = '" + m.text + "'"
        df = pd.read_sql(query,con=db_con)
        bot.send_message(cid, 'Tranding history')
        for i in df.index:
            bot.send_message(cid, 'Close time: ' +  str(df['close_time'][i]) + "\n Next Ops: " + str(round(df['nextOps'][i],8)) + " \n Op: " + str(df['ops'][i]) + " \n Qty: " + str(round(df['qty'][i],8)), parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['trader'])
def trader(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        query  = "select * from trader"
        df = pd.read_sql(query,con=db_con)
        eth = getTicker()
        for i in df.index:
            bot.send_message(cid, 'Qty: ' +  str(round(df['qty'][i],8)) + "\n Next Ops: " + str(round(df['nextOps'][i],8)) + " \n sellFlag: " + str(df['sellFlag'][i]) + " \n counterStopLoss: " + str(df['counterStopLoss'][i]) 
            + " of 288 (24 hours) \n counterForceSell: " + str(df['counterForceSell'][i]) + " of 1152 (96 hours) \n counterBuy: " 
            + str(df['counterBuy'][i]) + " \n Ops: " 
            + str(df['ops'][i]) + " \n Margin Sell 35 %" + " \n Margin buy 3 % \n Ticker: " + str(eth[4][499]), parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['botstatus'])
def trader(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        query  = "select case when status = '1' then 'Bot enabled' else 'Bot disabled' end status from t_signal"
        df = pd.read_sql(query,con=db_con)
        for i in df.index:
            bot.send_message(cid, 'Status: ' +  str(df['status'][i]), parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)  

@bot.message_handler(commands=['resetbot'])
def trader(m):
    cid = m.chat.id
    global gyear
    markup = types.ReplyKeyboardMarkup()
    itemd = types.KeyboardButton('/list')
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        restart_bot()
        bot.send_message(cid, 'All operations start from cero...done !!', parse_mode='Markdown', reply_markup=markup)
    else:    
        bot.send_message(cid, "User not autorized", parse_mode='Markdown', reply_markup=markup)                  


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
