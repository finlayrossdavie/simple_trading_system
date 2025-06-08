from config import Config
from components import Portfolio
from position import Position
import utils
import matplotlib.pyplot as plt
import pandas as pd

prices = utils.get_prices('GLD', 'GDX')
portfolios = []
thresholds = [(0.15, 0.25), (0.2, 0.3), (0.25, 0.35),
    (0.35, 0.45), (0.55, 0.65)
]

plt.figure(figsize=(12, 7))

for i, (entry, exit) in enumerate(thresholds):
    config = Config(entry_threshold=entry, exit_threshold=exit, asset1='GLD', asset2='GDX', initial_capital=100000)
    portfolio = Portfolio(prices, config)
    portfolio.backtest()
    pnl = [x.get_pnl() for x in portfolio.positions if isinstance(x, Position)]
    portfolios.append(portfolio)   
    plt.plot(prices['Date'][800:800+len(pnl)], pnl, label=f'Entry={entry}, Exit={exit}')


plt.legend()
plt.title('Trade PnL for 5 Different Threshold Configurations')
plt.xlabel('Date')
plt.ylabel('Trade PnL')
plt.show()

results = []
for portfolio in portfolios:
    results.append({
        "Entry Threshold": portfolio.configuration.entry_threshold,
        "Exit Threshold": portfolio.configuration.exit_threshold,
        "Average Holding Period (days)": round(portfolio.get_average_holding(), 2),
        "Final Capital (£)": round(portfolio.capitial, 2),
        "Sharpe Ratio": round(portfolio.calcualte_sharpe_ratio(), 2)
    })

# Create and display DataFrame
results_df = pd.DataFrame(results)
print(results_df)
