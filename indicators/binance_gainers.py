import requests
import json

# Binance API URL
url = "https://api.binance.com/api/v3/ticker/24hr"

# Send the request to the API
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Convert the response to JSON
    data = json.loads(response.text)
    
    # Get the list of gainers
    gainers = []
    for coin in data:
        if ( not (coin['symbol'].startswith("BUSD") or coin['symbol'].startswith("USDT")) and coin['symbol'].endswith("BUSD") or coin['symbol'].endswith("USDT")) and float(coin['priceChangePercent']) > 15:
            gainers.append(coin)
        
    # Sort the gainers by percentage change
    gainers.sort(key=lambda x: float(x['priceChangePercent']), reverse=True)
    
    # Print the gainers
    print("Top gainers of pairs ending in USDT or BUSD \n")
    for coin in gainers:
        print(f"Symbol: {coin['symbol']} Price Change: {coin['priceChangePercent']}%")
else:
    # Print an error message
    print("Failed to retrieve market data")
