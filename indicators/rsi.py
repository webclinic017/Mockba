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