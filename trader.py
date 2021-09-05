from binance.client import Client
import pandas as pd
import json
import apis as api
from  decimal import *
import openbizview

api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)
print('Cargando trading')
# An input is requested and stored in a variable
# coin = input ("Seleccione la moneda que desea ver el saldo: ")
# balance = client.get_asset_balance('ETHUSDT')
# print(balance)

# Cálculo para operaciones de compra/venta con Binance
# Se debe calcular porcentajes de compra (En cryptomoneda) que es el 0.1%
# Se debe calcular el porcentaje de venta (en dolar) 
# Esto aplica para el caso de ETHUSDT
# Realmente es porcentaje de compra y venta relacionado al par al que se hace trading
# Se realiza una compra a un precio establecido y se proyecta el precio de venta para
# Obtener un porcentaje por operación mínimo aceptado (0.09%) por operación
# Para ello se proyecta el precio utilizando keras analizeHistorical para evaluar el posible
# precio en los próximos 15 minutos en periodos de 5 minutos, si el valor resultante de la lista
# se encuentra cerca del valor que se desea para una ultilidad; se realiza la compra/venta. 
# Las operaciones se hacen por LIMIT seleccionando el 100% (por los momentos), cuando se cumpla la condición
# , comenzará el ciclo nuevautilidadc
# A futuro se va a convertir en una clase, cuando queramos trabajar con otros pares, es la misma metodologia
SYMBOL = 'ETHUSDT'
################################################################################
##########Cálculo de operaciones de compra venta para estimar utilidad##########
################################################################################
# Operaciones porcentuales
utilidad_transaccion = round(Decimal(1.05),3)
reflejado_porcentaje = utilidad_transaccion - 1

asset_balance_coin = client.get_asset_balance(asset='ETH')['free']
#
porcentaje_compra = round(Decimal(0.90),2)
ultimov_coin = round(Decimal(asset_balance_coin),8) * Decimal(porcentaje_compra)
asset_price = 0
cantidadv_dolar = 0
cantidadv_coin = 0
porcentaje_comisionv_binance = 0
comisionv_binance = 0
comisionv_binance_coin = 0
cantidadc_dolar = 0
cantidadc_coin = 0
precioc = 0
porcentaje_comisionc_binance = 0
comisionc_binance = 0
totalc = 0
utilidadc = 0
asset_price = 0
preciov_coin = 0
util_real_menos_comision_binance = 0
diferencial_cumplimiento = 0
ordenes = 0
total = 0
precio = 0
#
open_orders = client.get_open_orders(symbol='ETHUSDT')


# Siempre y cuando exista monto disponible
if len(open_orders) == 0:

    # Operaciones de venta
    asset_price = client.get_symbol_ticker(symbol=SYMBOL)['price']
    # Se toma el index y el valor de la columna price, convertido en float
    #df = pd.DataFrame(asset_price, index=[0])
    cantidadv_dolar = round(Decimal(asset_price) * Decimal(ultimov_coin),4)

    cantidadv_coin = Decimal(ultimov_coin) 
    porcentaje_comisionv_binance = Decimal(0.1) # 1%
    comisionv_binance = round(Decimal(cantidadv_dolar * (porcentaje_comisionv_binance)/100),9)
    comisionv_binance_coin = comisionv_binance / Decimal(asset_price)
    venta_coin_menos_comision = ultimov_coin -comisionv_binance_coin

    # Operaciones de compra
    cantidadc_dolar = round(Decimal(cantidadv_dolar - comisionv_binance),4)
    cantidadc_coin = round(Decimal(ultimov_coin) * Decimal(utilidad_transaccion),6)
    precioc = round(Decimal(cantidadc_dolar / cantidadc_coin),2)
    porcentaje_comisionc_binance = Decimal(0.099921) # 0.9%
    comisionc_binance = round(Decimal(cantidadc_coin * (porcentaje_comisionc_binance / 100)),9)
    totalc = round(Decimal(cantidadc_coin - comisionc_binance),6)
    utilidadc = Decimal(totalc) - Decimal(ultimov_coin)

    # Operaciones de venta
    #
    asset_price = client.get_symbol_ticker(symbol=SYMBOL)['price']
    # Se toma el index y el valor de la columna price, convertido en float
    # df = pd.DataFrame(asset_price, index=[0])
    preciov_coin = round(Decimal(asset_price),2)
    #

    # Utilidad
    util_real_menos_comision_binance = round((Decimal(totalc) / Decimal(ultimov_coin))-1,6)
    diferencial_cumplimiento = round(Decimal(totalc) - Decimal(ultimov_coin),6)

def load():
    print('reload')
    global open_orders, asset_price, asset_balance_coin
    open_orders = client.get_open_orders(symbol='ETHUSDT')
    asset_price = client.get_symbol_ticker(symbol=SYMBOL)['price']
    asset_balance_coin = client.get_asset_balance(asset='ETH')['free']

# api_key = api.Api().api_key
# api_secret = api.Api().api_secret
# client = Client(api_key, api_secret)
# SYMBOL = 'BTCUSDT'

# print(client.get_symbol_ticker(symbol=SYMBOL)['price'])