# In this example, the moving average is calculated with a window size of 20
# , which means that the average of the current value and the nineteen previous values is calculated. 
# The window size can be adjusted to your liking

import pandas as pd
import numpy as np
import datetime as dt

# Fetching the data from the crypto exchange 
#(you can use your own data or any other way to get the data)

data = pd.read_csv('crypto_data.csv')

#Convert the date to datetime
data['date'] = pd.to_datetime(data['date'])

#Set date as index
data = data.set_index('date')

#Calculate the moving average with a window size of 20
data['moving_average'] = data['close'].rolling(window=20).mean()

#Print the data
print(data)


import pandas as pd
import numpy as np

# Load historical data into a DataFrame
data = pd.read_csv("data.csv")

# Calculate the SMA with a specified window
sma = data["close"].rolling(window=50).mean()

# Calculate the RSI
delta = data["close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))

# Create a "signal" column that is 1 when the RSI is above 70 and the current SMA is above the previous SMA, and -1 when the RSI is below 30 and the current SMA is below the previous SMA
data["signal"] = np.where((rsi > 70) & (sma > sma.shift(1)), 1, np.where((rsi < 30) & (sma < sma.shift(1)), -1, 0))

# Create a "position" column that is 1 when the signal is 1, and -1 when the signal is -1
data["position"] = np.where(data["signal"] == 1, 1, np.where(data["signal"] == -1, -1, 0))

# Calculate the daily returns of the strategy
data["return"] = data["close"] * data["position"].shift(1) - data["close"]

