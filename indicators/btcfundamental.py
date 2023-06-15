import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load historical price data
price_data = pd.read_csv('bitcoin_prices.csv')
price_data['Date'] = pd.to_datetime(price_data['Date'])
price_data.set_index('Date', inplace=True)

# Load news sentiment data
news_data = pd.read_csv('bitcoin_news_sentiment.csv')
news_data['Date'] = pd.to_datetime(news_data['Date'])
news_data.set_index('Date', inplace=True)

# Calculate price change percentage
price_data['PriceChange'] = price_data['Close'].pct_change()

# Calculate average sentiment score
analyzer = SentimentIntensityAnalyzer()
news_data['SentimentScore'] = news_data['Headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

# Merge price and sentiment data
merged_data = pd.merge(price_data, news_data, how='left', left_index=True, right_index=True)

# Generate trading signals based on sentiment score
merged_data['Signal'] = 0
merged_data.loc[merged_data['SentimentScore'] > 0.1, 'Signal'] = 1  # Buy signal
merged_data.loc[merged_data['SentimentScore'] < -0.1, 'Signal'] = -1  # Sell signal

# Backtest the signals
merged_data['Return'] = merged_data['PriceChange'] * merged_data['Signal']
merged_data['CumulativeReturn'] = (1 + merged_data['Return']).cumprod()

# Plot the cumulative return
merged_data['CumulativeReturn'].plot(figsize=(10, 6), title='Bitcoin Cumulative Return')

# Print the performance metrics
total_return = merged_data['CumulativeReturn'].iloc[-1] - 1
annualized_return = ((1 + total_return) ** (365 / len(merged_data)) - 1) * 100
print(f'Total return: {total_return:.2%}')
print(f'Annualized return: {annualized_return:.2f}%')
