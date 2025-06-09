import numpy as np
import pandas as pd
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import os

base_dir = os.getcwd()

prices = None

def initialize_prices(asset1, asset2):

    asset1_path = os.path.join(base_dir, "data", "futures", "adjusted_prices_csv", f"{asset1}.csv")
    asset2_path = os.path.join(base_dir, "data", "futures", "adjusted_prices_csv", f"{asset2}.csv")

    if not os.path.exists(asset1_path) or not os.path.exists(asset2_path):
        raise FileNotFoundError("data files not found. Please check the paths.")
    
    a1 = pd.read_csv(asset1_path)    
    a2 = pd.read_csv(asset2_path)


    a1 = a1[['Date', 'Adj Close']]
    a2 = a2[['Date', 'Adj Close']]

    global prices

    a2.dropna(inplace=True)
    a1.dropna(inplace=True)
    a1['Date'] = pd.to_datetime(a1['Date'])
    a2['Date'] = pd.to_datetime(a2['Date'])
    prices = pd.merge(a1, a2, on='Date', how='inner')
    prices.rename(columns={'Adj Close_x': asset1, 'Adj Close_y': asset2}, inplace=True)
    prices.sort_values(by='Date', inplace=True)

    model = RollingOLS(prices[asset1], sm.add_constant(prices[asset2]), window=200)
    results = model.fit()
    prices['hedge_ratio'] = results.params[asset2]
    prices['spread'] = prices[asset1] - prices['hedge_ratio'] * prices[asset2]
    prices['spread_mean'] = prices['spread'].rolling(200).mean()
    prices['spread_std'] = prices['spread'].rolling(200).std()
    prices['z_score'] = (prices['spread'] - prices['spread_mean']) / prices['spread_std']
    
    
    prices.set_index('Date', inplace=True)


def get_prices(asset1, asset2):
    global prices

    if prices is None:
        print("Initializing prices...")
        initialize_prices(asset1, asset2)

    return prices


