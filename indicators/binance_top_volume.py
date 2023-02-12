import requests

# Make a GET request to the Binance API
response = requests.get("https://api.binance.com/api/v3/ticker/24hr")

# Check the status code of the response to make sure it's successful
if response.status_code == 200:
    # Retrieve the list of dictionaries from the response
    data = response.json()

    # Filter the list of dictionaries to exclude pairs starting with "BUSD" or "USDT" and ending with "BUSD"
    filtered_data = [d for d in data if not (d['symbol'].startswith("BUSD") or d['symbol'].startswith("USDT")) and d['symbol'].endswith("BUSD") or d['symbol'].endswith("USDT")]

    # Sort the filtered data by the volume in descending order
    sorted_data = sorted(filtered_data, key=lambda x: x['quoteVolume'], reverse=True)

    # Print the top 10 pairs with the highest volume
    print("Top volume of pairs ending in USDT or BUSD \n")
    for i, d in enumerate(sorted_data[:10]):
        print(f"{i + 1}. {d['symbol']}: {d['quoteVolume']}")
else:
    # If the request fails, print an error message
    print("Failed to retrieve data from Binance API")
