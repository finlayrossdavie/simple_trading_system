from config import Config
from components import Portfolio
from position import Position
import utils
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

prices = utils.get_prices('GLD', 'GDX')
portfolios = []
thresholds = [(0.2, 0.1), (0.4, 0.2),
              (0.8,0.4), (1.3, 0.7), (2,1)
]

plt.figure(figsize=(12, 7))

for i, (entry, exit) in enumerate(thresholds):

    config = Config(entry_threshold=entry, exit_threshold=exit, asset1='GLD', asset2='GDX', initial_capital=100000)
    portfolio = Portfolio(prices, config)
    # portfolio.backtest('2014-05-23', '2019-05-23') #just testing a recent pre-covid 5 year, leave empty to backtest the full dataset
    portfolio.backtest('2019-05-23', '2025-05-23') #just testing a recent pre-covid 5 year, leave empty to backtest the full dataset

    pnl = [(x.get_pnl()) for x in portfolio.positions if isinstance(x, Position)]
    close_dates = [x.exit_date for x in portfolio.positions if isinstance(x, Position)]
    portfolios.append(portfolio)   
    cum_pnl = np.cumsum(pnl)

    plt.plot(close_dates, cum_pnl, label=f'Entry={entry}, Exit={exit}')


plt.legend()
plt.title('Trade PnL for 5 Different Threshold Configurations')
plt.xlabel('Date')
plt.ylabel('Trade PnL')
plt.show()

plt.figure(figsize=(12, 7))

portfolio = portfolios[0]  # Use the first portfolio for z-score plotting


plt.plot(portfolio.prices.index, portfolio.prices['z_score'], label=f'Entry={portfolio.configuration.entry_threshold}, Exit={portfolio.configuration.exit_threshold}')
plt.axhline(y=portfolio.configuration.entry_threshold, color='r', linestyle='--', label='Entry Threshold')
plt.axhline(y=portfolio.configuration.exit_threshold, color='g', linestyle='--', label='Exit Threshold')
plt.axhline(y=-portfolio.configuration.exit_threshold, color='b', linestyle='--', label='Negative Exit Threshold')
plt.axhline(y=-portfolio.configuration.entry_threshold, color='orange', linestyle='--', label='Negative Entry Threshold')

plt.show()

plt.figure(figsize=(12, 7))

for portfolio in portfolios:
    plt.plot(portfolio.daily_captial, label=f'Entry={portfolio.configuration.entry_threshold}, Exit={portfolio.configuration.exit_threshold}')
plt.legend()
plt.title('Portfolio Capital Over Time for Different Threshold Configurations')
plt.xlabel('Days')
plt.ylabel('Capital (£)')
plt.show()


results = []
for portfolio in portfolios:
    results.append({
        "Entry Threshold": portfolio.configuration.entry_threshold,
        "Exit Threshold": portfolio.configuration.exit_threshold,
        "Average Holding Period (days)": round(portfolio.get_average_holding(), 2),
        "Final Capital (£)": round(portfolio.capital, 2),
        "Sharpe Ratio": round(portfolio.calculate_sharpe_ratio(), 2),
        "Total Positions": len(portfolio.positions),
        "Max-Drawdown": round(portfolio.calculate_max_drawdown(), 2),
    })

# Create and display DataFrame
results_df = pd.DataFrame(results)
print(results_df)


