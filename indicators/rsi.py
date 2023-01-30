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


# This code first loads the crypto data into a dataframe using pandas
# , then it calculate the difference in price between consecutive days
# , then it create a new dataframe to hold the RSI values
# , then it set the gain and loss variables to the difference in price
# , after that it set the window for the rolling average
# , then it calculates the average gain and loss for the window
# , then it calculates the relative strength, after that it calculates the RSI, finally it print the RSI values.

import pandas as pd
import numpy as np

# Load crypto data into a dataframe
df = pd.read_csv("crypto_data.csv")

# Calculate the difference in price between consecutive days
delta = df["close"].diff()

# Create a new dataframe to hold the RSI values
df["rsi"] = np.nan

# Set the gain and loss variables to the difference in price
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

# Set the window for the rolling average
window = 14

# Calculate the average gain and loss for the window
avg_gain = gain.rolling(window).mean()
avg_loss = loss.rolling(window).mean()

# Calculate the relative strength
rs = avg_gain / avg_loss

# Calculate the RSI
df["rsi"] = 100 - (100 / (1 + rs))

# Print the RSI values
print(df["rsi"])

# This code will calculate the RSI for a dataset of historical crypto prices.
# Make sure to adjust the file path and the window size to match your needs.

import pandas as pd
import numpy as np

# Get historical data for a specific cryptocurrency
df = pd.read_csv('crypto_data.csv')

# Create a new column to hold the difference between the close price and the previous close price
df['delta'] = df['close'] - df['close'].shift(1)

# Create new columns to hold the gain and loss values
df['gain'] = np.where(df['delta'] > 0, df['delta'], 0)
df['loss'] = np.where(df['delta'] < 0, abs(df['delta']), 0)

# Create new columns to hold the average gain and average loss values
avg_gain = df['gain'].rolling(window=14).mean()
avg_loss = df['loss'].rolling(window=14).mean()

# Create a new column for the relative strength
df['RS'] = avg_gain / avg_loss

# Calculate the relative strength index
df['RSI'] = 100 - (100 / (1 + df['RS']))

# Print the RSI values
print(df['RSI'])
