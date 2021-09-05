import pandas as pd
import postgrescon as pg
import trader as tr 
import orders
from  decimal import *
import time
import sendmail
import importlib

starttime = time.time()

# The automatic bot
# Execute the condition if it is available founds
# Condition: signal, the value of futuretrade is in the predited value
# The predicted value y goin down and is equal or lower from the future trade value
# If it is not value of prediction, wait for the next prediction process to begin again the process
# print(str(tr.totalc))

# Conexión a base de datosa
postgre_con = pg.Postgres().postgre_con
signal_bot = pd.read_sql("SELECT auto FROM public.signal_bot where id = 2",con=postgre_con)
auto = bool(signal_bot['auto'].values)


if len(tr.open_orders) > 0:
  print('Hay orden ETHUSDT montada, no va a ejecutar')
elif auto:
  print('Calculando')

  # sendmail.initops()
  # Execute IA
  print('Ejecutar IA')
  time.sleep( 1 )
  #import analizeHistoricalEth
  #analizeHistoricalEth.analize()
  # Read analized results
  print('Leer resultados')
  data = pd.read_sql("SELECT cast(cast(close_time as timestamp) at time zone 'utc' at time zone 'america/caracas' as text) as close_time, close_pred close_pred FROM public.predict_eth_udst",con=postgre_con)
  close_list = data['close_pred'].values
  print('Analizar trading')
  precioc = tr.precioc
  print(close_list)
  print('Precio compra: ' + str(precioc))
  # Compare list values 30% accurate for signal
  preditec_list = list(filter(lambda x: (x <= precioc),  close_list))  
  predicted_percentaje = round((len(preditec_list) / len(close_list))*100)
  print('Porcentaje del análisis')
  print(predicted_percentaje)  
  if predicted_percentaje > 30:
      # Executing order market sell, limit buy
      print("Montando orden de venta/compra....." + str(float(round(tr.venta_coin_menos_comision,8))))
      orders.order_market_sell("ETHUSDT",float(round(tr.venta_coin_menos_comision,4)))
      time.sleep(25)
      orders.order_limit_buy("ETHUSDT",round(float(tr.totalc),4), round(float(tr.precioc),2))
      print('Compra :' + str(tr.totalc))
      print('Orden montada')
      sendmail.enviarcorreo()
      time.sleep( 1 )
  else:
      print('Sin predicción, volver al calcular, precio compra: ' + str(tr.precioc))
      time.sleep( 1 )
else:
  print('Bot apagado')     