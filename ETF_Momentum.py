# Import the necessary libraries 

import yfinance as yf
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

# Define the list of ETFs to analyse
Tickers = ['XLK','XLF','XLE','XLV','XLI','XLY','XLP','XLU','XLB','XLRE','XLC']
Prices = yf.download(Tickers, start='2019-01-01', auto_adjust=True)['Close']
Prices = Prices.dropna()

# Calculate the daily returns for each ETF
Returns = Prices.pct_change()


# Build the Signal for each ETF based on the 20 day lookback period and adjusting for Skip-1 convention 
Lookback = 21

Signal = Prices.shift(1)/Prices.shift(Lookback) - 1

# Rank the ETFs based on the Signal, with the highest Signal getting the highest rank (11 being the best)
Rank = Signal.rank(axis=1, ascending=True, na_option='keep')

# Now assign weighted postions based on the ranks, with the top 3 ranked ETFs getting a weight of 1/3 each and the rest getting a weight of 0
Weights = pd.DataFrame(np.where(Rank >=9, 1/3, np.where(Rank <=3, -1/3,0)), index=Rank.index, columns=Rank.columns)

#Make adjustment for weekly rebalacing taking the first day from the weekly data, then reindex for the begining week weightings then forward fill for the remaining days of the week
Weekly_Weights = Weights.resample('W').first().reindex(Weights.index, method='ffill')

# Make adjustment for executing trades at the close of the next day and returns only realised at end of T+2 
Forward_Returns = Returns.shift(-2)

#Calculate the strategy returns by multiplying the weights with the forward returns and summing across all ETFs for each day
Strategy_Returns = (Weekly_Weights * Forward_Returns).sum(axis=1)

#Now Calculate the Performance metrics for the stredgy 

# Annualized Sharpe Ratio (Return over volitlity, assuming 252 trading days in a year)
Sharpe = Strategy_Returns.mean() / Strategy_Returns.std() * np.sqrt(252) 

#Annualised Return 
Annualized_Return = Strategy_Returns.mean()*252

# Maximum Drawdodwn 
Cumulative_Returns = (1 + Strategy_Returns).cumprod()
Rolling_Max = Cumulative_Returns.cummax()
Drawdown = (Cumulative_Returns - Rolling_Max) / Rolling_Max
Max_Drawdown = Drawdown.min()


# Print the performance metrics
print(f"Annualised Return: {Annualized_Return:.2%}")
print(f"Sharpe Ratio:      {Sharpe:.2f}")
print(f"Max Drawdown:      {Max_Drawdown:.2%}")


# Plot the cumulative returns of the strategy
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot( Cumulative_Returns.index, Cumulative_Returns.values, label='Strategy', color='blue')
ax1.set_title('Cumulative Return of the Strategy - Cross Sectional Momentum')
ax1.set_ylabel('Cumulative Return')
ax1.legend()
ax1.grid(True)

ax2.plot(Drawdown.index, Drawdown.values, label='Drawdown', color='red')
ax2.set_title('Drawdown of the Strategy - Cross Sectional Momentum')
ax2.set_ylabel('Drawdown %')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('ETF_Momentum_Strategy_Performance.png')
plt.show()

# Seperate to In and Out of Sample Returns for further analysis

Returns_For_Analysis = Strategy_Returns[Strategy_Returns != 0]
In_Sample = Returns_For_Analysis[:'2022-12-31']
Out_Sample = Returns_For_Analysis['2023-01-01':]

Sharpe_In = In_Sample.mean() / In_Sample.std() * np.sqrt(252)
Sharpe_Out = Out_Sample.mean() / Out_Sample.std() * np.sqrt(252)

Annualized_Return_In = In_Sample.mean()*252
Annualized_Return_Out = Out_Sample.mean()*252

Cumulative_Returns_In = (1 + In_Sample).cumprod()
Rolling_Max_In = Cumulative_Returns_In.cummax()
Drawdown_In = (Cumulative_Returns_In - Rolling_Max_In) / Rolling_Max_In
Max_Drawdown_In = Drawdown_In.min()

Cumulative_Returns_Out = (1 + Out_Sample).cumprod()
Rolling_Max_Out = Cumulative_Returns_Out.cummax()
Drawdown_Out = (Cumulative_Returns_Out - Rolling_Max_Out) / Rolling_Max_Out
Max_Drawdown_Out = Drawdown_Out.min()

print(f"In Sample Annualised Return: {Annualized_Return_In:.2%}")
print(f"In Sample Sharpe Ratio:      {Sharpe_In:.2f}")
print(f"In Sample Max Drawdown:      {Max_Drawdown_In:.2%}")
print(f"Out of Sample Annualised Return: {Annualized_Return_Out:.2%}")
print(f"Out of Sample Sharpe Ratio:      {Sharpe_Out:.2f}")
print(f"Out of Sample Max Drawdown:      {Max_Drawdown_Out:.2%}")
