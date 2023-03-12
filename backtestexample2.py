import pandas as pd
import numpy as np

# Read in the data
df = pd.read_csv('data.csv')
df = df.set_index(pd.DatetimeIndex(df['date']))
df = df.drop(['date'], axis=1)

# Define strategy parameters
ma_period = 50
rsi_period = 14
stop_loss = 0.05
take_profit = 0.1

# Calculate moving average and RSI
df['ma'] = df['close'].rolling(ma_period).mean()
delta = df['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(rsi_period).mean()
avg_loss = loss.rolling(rsi_period).mean()
rs = avg_gain / avg_loss
df['rsi'] = 100 - (100 / (1 + rs))

# Generate buy/sell signals based on strategy
df['buy'] = np.where((df['close'] < df['ma'] * 0.9) & (df['rsi'] < 35), 1, 0)
df['sell'] = np.where((df['close'] > df['ma'] * 1.1) & (df['rsi'] > 50), 1, 0)

# Implement stop-loss and take-profit
position = 0
stop_loss_price = 0
take_profit_price = 0
for i in range(len(df)):
    if df['buy'][i] == 1 and position == 0:
        position = 1
        stop_loss_price = df['close'][i] * (1 - stop_loss)
        take_profit_price = df['close'][i] * (1 + take_profit)
    elif df['sell'][i] == 1 and position == 1:
        position = 0
        stop_loss_price = 0
        take_profit_price = 0
    elif position == 1:
        if df['close'][i] <= stop_loss_price:
            position = 0
            stop_loss_price = 0
            take_profit_price = 0
        elif df['close'][i] >= take_profit_price:
            position = 0
            stop_loss_price = 0
            take_profit_price = 0

# Calculate returns
df['returns'] = np.log(df['close'] / df['close'].shift(1))
df['strategy_returns'] = df['returns'] * df['buy'].shift(1)
total_strategy_returns = df['strategy_returns'].dropna().sum()
total_market_returns = df['returns'].dropna().sum()

# Print results
print('Total market returns:', total_market_returns)
print('Total strategy returns:', total_strategy_returns)
