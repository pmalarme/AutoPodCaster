# filename: ytd_gain_comparison.py

import yfinance as yf
from datetime import datetime

# Get the current date
current_date = datetime.now().strftime('%Y-%m-%d')
print(f"Current Date: {current_date}")

# Define the stock tickers
stocks = ['META', 'TSLA']

# Get the stock data
data = yf.download(stocks, start='2023-01-01', end=current_date)

# Get the opening prices at the beginning of the year and the latest closing prices
start_prices = data['Open'].iloc[0]
end_prices = data['Close'].iloc[-1]

# Calculate the YTD gain
ytd_gain = ((end_prices - start_prices) / start_prices) * 100

# Print the YTD gain for each stock
for stock in stocks:
    print(f"YTD Gain for {stock}: {ytd_gain[stock]:.2f}%")