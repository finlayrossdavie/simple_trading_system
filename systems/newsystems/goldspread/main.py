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

entry = 1.3 
exit = 0.2


fig = plt.figure(figsize=(15, 12))
gs = plt.GridSpec(3, 2, height_ratios=[1, 0.7, 1.1], width_ratios=[1.3, 1])


config = Config(entry_threshold=entry, exit_threshold=exit, asset1='GLD', asset2='GDX', initial_capital=100000)
portfolio = Portfolio(prices, config)
portfolio.backtest('2019-05-23', '2025-05-23') #just testing a recent pre-covid 5 year, leave empty to backtest the full dataset

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(portfolio.daily_capital.index, portfolio.daily_capital.values, label='Capital (£)', color='blue')
ax1.set_title('Portfolio Capital Over Time')
ax1.set_xlabel('Days')
ax1.set_ylabel('Capital (£)')
ax1.grid(True)


max_drawdown = portfolio.calculate_max_drawdown()

ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
ax2.fill_between(portfolio.daily_drawdown.index, -portfolio.daily_drawdown.values, 0, color='red', alpha=0.4)
ax2.set_title("Drawdown (%)")
ax2.set_ylabel("Drawdown")
ax2.grid(True)



monthly_returns = portfolio.calculate_monthly_returns()
monthly_returns_df = monthly_returns.to_frame(name='return')
monthly_returns_df['Year'] = monthly_returns_df.index.year
monthly_returns_df['Month'] = monthly_returns_df.index.month

heatmap_data = monthly_returns_df.pivot(index='Year', columns='Month', values='return')
heatmap_data = heatmap_data.reindex(columns=range(1, 13))

# Plot heatmap in the third row of the GridSpec
ax3 = fig.add_subplot(gs[2, 0])
c = ax3.imshow(heatmap_data, aspect='auto', cmap='RdYlGn', vmin=-0.2, vmax=0.2)

# Set axis labels for heatmap
ax3.set_xticks(np.arange(12))
ax3.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax3.set_yticks(np.arange(len(heatmap_data.index)))
ax3.set_yticklabels(heatmap_data.index)

# Annotate cells with return values
for i in range(len(heatmap_data.index)):
    for j in range(12):
        val = heatmap_data.iloc[i, j]
        if not np.isnan(val):
            ax3.text(j, i, f"{val:.1%}", ha='center', va='center', color='black', fontsize=8)

ax3.set_title("Portfolio Monthly Returns Heatmap")
ax3.set_xlabel("Month")
ax3.set_ylabel("Year")
fig.colorbar(c, ax=ax3, label="Monthly Return")
ax3.grid(False)

yearly_returns = portfolio.calculate_yearly_returns()

ax4 = fig.add_subplot(gs[0, 1])
ax4.bar(yearly_returns.index.year, yearly_returns.values, color='dodgerblue')
ax4.set_title("Yearly Returns (%)")
ax4.set_ylabel("Return")
ax4.grid(True, axis='y')


ax5 = fig.add_subplot(gs[1:, 1])
ax5.axis("off")
summary_stats = {
    "Total Return": f"{(portfolio.daily_capital.iloc[-1]/portfolio.daily_capital.iloc[0])*100:.1f}%",
    "Sharpe Ratio": f"{portfolio.calculate_sharpe_ratio():.2f}",
    "Max Drawdown": f"{-max_drawdown*100:.2f}%",
    "Average Holding Period ": f"{portfolio.get_average_holding():.2f} days",
    "Total Number of Positions": len(portfolio.positions),
    "Final Capital (£)": round(portfolio.capital, 2),
    "Winning Trades ": f"{portfolio.calculate_winning_trades() * 100:.2f}%",
    "Best Month": f"{monthly_returns.max()*100:.2f}%",
    "Worst Month": f"{monthly_returns.min()*100:.2f}%"
}
table_data = [[k, v] for k, v in summary_stats.items()]
table = ax5.table(cellText=table_data, colLabels=["Metric", "Value"], loc="center")
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
ax5.set_title("Performance Summary", pad=20)


plt.tight_layout()
plt.show()


