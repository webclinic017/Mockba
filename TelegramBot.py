from os import defpath
import telebot
from telebot import types
import sqlite3
import pandas as pd

# Telegram Bot
API_TOKEN = '1042444870:AAHEuYUbs2YJrGDUEfd1ZjvomJafqCStMKM'
db_con = sqlite3.connect('storage/mockba.db', check_same_thread=False)

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
    itemd = types.KeyboardButton('/list')
    markup.row(itema)
    markup.row(itemb)
    markup.row(itemc)
    markup.row(itemd)
    bot.send_message(cid, help_text, reply_markup=markup) 


@bot.message_handler(commands=['enablebot'])
def actautobot(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardMarkup()
    itema = types.KeyboardButton('/tradehistory')
    itemb = types.KeyboardButton('/enablebot')
    itemc = types.KeyboardButton('/disablebot')
    itemd = types.KeyboardButton('/list')
    markup.row(itema)
    markup.row(itemb)
    markup.row(itemc)
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
    itema = types.KeyboardButton('/tradehistory')
    itemb = types.KeyboardButton('/enablebot')
    itemc = types.KeyboardButton('/disablebot')
    itemd = types.KeyboardButton('/list')
    markup.row(itema)
    markup.row(itemb)
    markup.row(itemc)
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
    itema = types.KeyboardButton('/tradehistory')
    itemb = types.KeyboardButton('/enablebot')
    itemc = types.KeyboardButton('/disablebot')
    itemd = types.KeyboardButton('/list')
    markup.row(itema)
    markup.row(itemb)
    markup.row(itemc)
    markup.row(itemd)
    if  int(user['token'].values) == cid:
        query  = "select qty, nextOps, ops, STRFTIME('%d/%m/%Y %H:%M',datetime(close_time/1000, 'unixepoch')) close_time from trader_history"
        query += " where STRFTIME('%Y',datetime(close_time/1000, 'unixepoch')) = '" + gyear + "'"
        query += " and STRFTIME('%m',datetime(close_time/1000, 'unixepoch')) = '" + m.text + "'"
        df = pd.read_sql(query,con=db_con)
        bot.send_message(cid, 'Tranding history')
        for i in df.index:
            bot.send_message(cid, 'Close time: ' +  str(df['close_time'][i]) + "\n Next Ops: " + str(df['nextOps'][i]) + " \n Op: " + str(df['ops'][i]) + " \n Qty: " + str(df['qty'][i]), parse_mode='Markdown', reply_markup=markup)
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
