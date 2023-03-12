import pandas as pd
import talib

# Load historical price data
df = pd.read_csv('historical_prices.csv', parse_dates=['timestamp'], index_col='timestamp')

# Calculate Moving Average (MA) and Relative Strength Index (RSI)
ma = talib.SMA(df['close'], timeperiod=20)
rsi = talib.RSI(df['close'], timeperiod=14)

# Define a function to determine the trading signal
def get_signal(row):
    if row['close'] < (1 - 0.1) * row['ma'] and row['rsi'] < 35:
        return 'buy'
    elif row['close'] > (1 + 0.1) * row['ma'] and row['rsi'] > 50:
        return 'sell'
    else:
        return 'hold'

# Apply the trading signal function to each row of the DataFrame
df['signal'] = df.apply(get_signal, axis=1)

# Backtest the trading strategy
df['returns'] = df['close'].pct_change()
df['strategy_returns'] = df['returns'] * df['signal'].shift(1)
backtest_results = df['strategy_returns'].cumsum()
