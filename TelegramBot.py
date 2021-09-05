import telebot
from telebot import types
import openbizview
import postgrescon as pg
import psycopg2
import datetime
from  decimal import *
import orders
import time
import pandas as pd
import sendmail
import importlib

# Telegram Bot
API_TOKEN = '1042444870:AAHEuYUbs2YJrGDUEfd1ZjvomJafqCStMKM'

bot = telebot.TeleBot(API_TOKEN)
final_result = []
gcodrep = ""
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
                    "Bienvenido a Mockba " + nom)
    command_help(m)

# Comando listar
@bot.message_handler(commands=['listar'])
def command_help(m):
    cid = m.chat.id
    help_text = "Las siguientes opciones son las disponibles."
    markup = types.ReplyKeyboardMarkup()
    itema = types.KeyboardButton('/EjecutarIA')
    itemd = types.KeyboardButton('/ActivarAutobot')
    iteme = types.KeyboardButton('/DesactivarAutobot')
    itemf = types.KeyboardButton('/listar')
    markup.row(itema)
    markup.row(itemd)
    markup.row(iteme)
    markup.row(itemf)
    bot.send_message(cid, help_text, reply_markup=markup) 

# Comando listar
@bot.message_handler(commands=['symbol'])
def symbol(m):
    cid = m.chat.id
    valor = m.text
    global gcodrep
    if openbizview.login_pass(valor) == 0:
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)
        bot.send_message(cid, "Token inválido", reply_markup=markup)
    else:
        help_text = "Seleccione par."
        markup = types.ReplyKeyboardMarkup()
        itema = types.KeyboardButton('BTCUSDT')
        itemb = types.KeyboardButton('ETHUSDT')
        itemd = types.KeyboardButton('/listar')
        markup.row(itema)
        markup.row(itemb)
        markup.row(itemd)
        bot.send_message(cid, help_text, reply_markup=markup) 
        if  gcodrep == "1":
          bot.register_next_step_handler_by_chat_id(cid, operationsIA)
        elif gcodrep == "4":  
          bot.register_next_step_handler_by_chat_id(cid, operationsAATB)
        else:  
          bot.register_next_step_handler_by_chat_id(cid, operationsDATB)       
             

# Comando ejecutar IA
@bot.message_handler(commands=['EjecutarIA'])
def ia(m):
    cid = m.chat.id
    global gcodrep
    gcodrep = "1"
    bot.send_message(cid, "Ingrese  token:")
    bot.register_next_step_handler_by_chat_id(cid, symbol)


# Comando montar orden
@bot.message_handler(commands=['ActivarAutobot'])
def actautobot(m):
    cid = m.chat.id
    global gcodrep
    gcodrep = "4"
    bot.send_message(cid, "Ingrese  token:")
    bot.register_next_step_handler_by_chat_id(cid, symbol)

# Comando montar orden
@bot.message_handler(commands=['DesactivarAutobot'])
def dautobot(m):
    cid = m.chat.id
    global gcodrep
    gcodrep = "5"
    bot.send_message(cid, "Ingrese  token:")
    bot.register_next_step_handler_by_chat_id(cid, symbol)            

# Calcular IA
def operationsIA(m):
    cid = m.chat.id
    valor = m.text
    global final_result
    if valor == "BTCUSDT":
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)  
        
        bot.send_message(cid, "Operación de IA BTCUSDT en ejecución, espere el resultado, puede tardar un tiempo, ejecutando......")  
        # Ejecita Ia importando objeto
        # import analizeHistorical
        # analizeHistorical.analize()  
        # Al culminar imprimir valores
        con = pg.conection()
        try:
         cur = con.cursor()
         query = "select cast(cast(close_time as timestamp) at time zone 'utc' at time zone 'america/caracas' as text) as close_time, close_pred from predict_btc_udst"
         cur.execute(query)       
         final_result = cur.fetchall()
         cur.close
         con.close    
        except (Exception, psycopg2.DatabaseError) as error:
          print(error)
        finally:
          if con is not None:
            con.close()  # Cerrando conección  
        
        bot.send_message(cid, "Predicción próximos 10 registros de 5 minutos fecha y monto: \n" 
           , parse_mode='Markdown')  

        for row in final_result:
           fecha = row[0]
           monto = round(Decimal(row[1]),2)

           bot.send_message(cid, fecha + '  ---  ' + str(monto), parse_mode='Markdown')   

        #img = open('BTC_validation.png', 'rb')
        #bot.send_photo(cid, img, caption = "Predicción vs actual")

        #img = open('BTC_predictions.png', 'rb')
        #bot.send_photo(cid, img, caption = "Predicción 10 períodos", reply_markup=markup)
        bot.send_message(cid, "Predicción 10 períodos", parse_mode='Markdown')
    else:
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)  

        bot.send_message(cid, "Operación de IA ETHUSDT en ejecución, espere el resultado, puede tardar un tiempo, ejecutando......")  
        # Ejecita Ia importando objeto
        # import analizeHistoricalEth
        # analizeHistoricalEth.analize()  
        # Al culminar imprimir valores
        con = pg.conection()
        try:
         cur = con.cursor()
         query = "select cast(cast(close_time as timestamp) at time zone 'utc' at time zone 'america/caracas' as text) as close_time, close_pred from predict_eth_udst"
         cur.execute(query)       
         final_result = cur.fetchall()
         cur.close
         con.close    
        except (Exception, psycopg2.DatabaseError) as error:
          print(error)
        finally:
          if con is not None:
            con.close()  # Cerrando conección  
        
        bot.send_message(cid, "Predicción próximos 10 registros de 5 minutos fecha y monto: \n" 
           , parse_mode='Markdown')  

        for row in final_result:
           fecha = row[0]
           monto = round(Decimal(row[1]),2)

           bot.send_message(cid, fecha + '  ---  ' + str(monto), parse_mode='Markdown')   

        #img = open('Eth_validation.png', 'rb')
        #bot.send_photo(cid, img, caption = "Predicción vs actual")

        #img = open('Eth_predictions.png', 'rb')
        #bot.send_photo(cid, img, caption = "Predicción 10 períodos", reply_markup=markup) 
        bot.send_message(cid, "Predicción 10 períodos", parse_mode='Markdown')       


# Activar bot
def operationsAATB(m):
    cid = m.chat.id
    valor = m.text
    if valor == "BTCUSDT":
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)
        pg.enable_autobot('1')
        bot.send_message(cid, "Bot BTCUSDT activado", parse_mode='Markdown', reply_markup=markup) 
    else:
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)
        pg.enable_autobot('2')
        bot.send_message(cid, "Bot ETHUSDT activado", parse_mode='Markdown', reply_markup=markup) 

# Desactivar bot
def operationsDATB(m):
    cid = m.chat.id
    valor = m.text
    if valor == "BTCUSDT":
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)
        pg.disable_autobot('1')
        bot.send_message(cid, "Bot BTCUSDT desactivado", parse_mode='Markdown', reply_markup=markup) 
    else:
        markup = types.ReplyKeyboardMarkup()
        itemd = types.KeyboardButton('/listar')
        markup.row(itemd)
        pg.disable_autobot('2')
        bot.send_message(cid, "Bot ETHUSDT desactivado", parse_mode='Markdown', reply_markup=markup) 

bot.polling()     
