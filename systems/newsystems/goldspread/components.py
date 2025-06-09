from position import Position
import numpy as np

class Portfolio:
    def __init__(self, prices, config):
        self.positions = []
        self.capitial = config.initial_capital
        self.running_pnl = 0.0
        self.prices = prices
        self.current_position = None
        self.configuration = config

    def position_size(self, current_price_gld, current_price_gdx,hedge_ratio):
        effective_unit_cost = current_price_gld + (hedge_ratio * current_price_gdx)
        gld_units = self.capitial // effective_unit_cost
        gdx_units = gld_units * hedge_ratio

        return int(gld_units), int(gdx_units)
        
    def open_position(self, direction ,gld_units, gdx_units, entry_price_gld, entry_price_gdx, date):
        if self.current_position is not None and self.current_position.open:
            raise Exception("Cannot open a new position while another is open.")
        self.current_position = Position(direction, gld_units, gdx_units, entry_price_gld, entry_price_gdx, date)
        self.positions.append(self.current_position)

    def close_position(self, current_price_gld, current_price_gdx, date):
        pnl = self.current_position.calculate_pnl(current_price_gld, current_price_gdx)
        self.running_pnl += pnl
        self.capitial += pnl
        self.current_position.close_position(date)
        self.current_position = None

    def get_average_holding(self):
        holding_periods = [(x.exit_date - x.entry_date).days for x in self.positions if isinstance(x, Position) and x.exit_date is not None]
        average_holding_period = np.mean(holding_periods) if holding_periods else 0
        return average_holding_period
    
    def calcualte_sharpe_ratio(self):
        returns = []
        holding_periods_days = []
        for pos in self.positions:
            if pos.exit_date is not None:
                current_return = pos.calculate_final_return()
                holding_period_days = (pos.exit_date - pos.entry_date).days
                holding_periods_days.append(holding_period_days)
                returns.append(current_return)

        if len(returns) == 0:
            return 0
        
        adjusted_risk_free_rates = [(1 + self.configuration.risk_free_rate)**(period / 365.0) - 1 for period in holding_periods_days]
        excess_returns = np.array(returns) - np.array(adjusted_risk_free_rates)

        sharpe_ratio_per_trade = np.mean(excess_returns) / np.std(excess_returns)
  
        total_years = (self.prices.index[-1] - self.prices.index[0]).days / 365.0
        trades_per_year = len(returns) / total_years
        
        annualized_sharpe_ratio = sharpe_ratio_per_trade * np.sqrt(trades_per_year)

        return annualized_sharpe_ratio  
    
    def backtest(self, start_date="2009-07-27", end_date="2025-06-05"):   #indexes 800 and n

        if start_date not in self.prices.index or end_date not in self.prices.index:
            raise ValueError("Start date or end date not found in prices")
        
        start = self.prices.index.get_loc(start_date)
        end = self.prices.index.get_loc(end_date)

        if start >= end:
            raise ValueError("Start date must be before end date")

        for i in range(start, end):
        
            current_price_gld = self.prices[self.configuration.asset1].iloc[i]
            current_price_gdx = self.prices[self.configuration.asset2].iloc[i]
            z_score = self.prices['z_score'].iloc[i]
            hedge_ratio = self.prices['hedge_ratio'].iloc[i]
            date = self.prices.index[i]

            signal = goldspread_rule(z_score, self.configuration.entry_threshold, self.configuration.exit_threshold)

            if signal == -1:  # Short GLD, Long GDX
                if self.current_position is None or not self.current_position.open:
                    gld_units, gdx_units = self.position_size(current_price_gld, current_price_gdx, hedge_ratio)
                    self.open_position(-1, gld_units, gdx_units, current_price_gld, current_price_gdx, date)
            
            elif signal == 1 :  # Long GLD, Short GD
                if self.current_position is None or not self.current_position.open:
                    gld_units, gdx_units = self.position_size(current_price_gld, current_price_gdx, hedge_ratio)
                    self.open_position(1, gld_units, gdx_units, current_price_gld, current_price_gdx, date)

            elif signal == 0:  # Exit position
                if self.current_position is not None and self.current_position.open:
                    self.close_position(current_price_gld, current_price_gdx, date)


def goldspread_rule(z_score, entry_threshold, exit_threshold): #0.2 and 0.3
    if z_score > entry_threshold:
        return -1 # Short GLD, Long GDX
    elif z_score < -entry_threshold:
        return  1 # Long GLD, Short GDX
    elif z_score < exit_threshold:
        return 0 # exit position
    else:
        return -2 # hold position