from binance.client import Client
import apis as api

api_key = api.Api().api_key
api_secret = api.Api().api_secret
client = Client(api_key, api_secret)


# Place order market price 100%
def order_market_sell(psymbol, pquantity): 
   client.order_market_sell(symbol=psymbol, quantity=pquantity)

# Buy Btc
def order_limit_buy(psymbol, pquantity, pprice):
    client.order_limit_buy(timeInForce=client.TIME_IN_FORCE_GTC, symbol=psymbol, quantity=pquantity, price=pprice)   

#import trader as tr
#print(round(tr.trader.venta_coin_menos_comision,6))
#print('Vende market')
#order_market_sell(float(round(tr.trader.venta_coin_menos_comision,6)))
#time.sleep(5)
#print('Compra limit')
#order_limit_buy(float(tr.trader.precioc), float(tr.trader.totalc))
#print(tr.trader.totalc)
#order_market_sell(float(0.007408))
#order_limit_buy(float(11413.67), float(0.007423))
# asset_balance_coin = client.get_asset_balance(asset='BTC')['free']
# print(asset_balance_coin)