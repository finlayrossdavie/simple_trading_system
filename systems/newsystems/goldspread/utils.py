import numpy as np
import pandas as pd
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import os

base_dir = os.getcwd()
gdx_path = os.path.join(base_dir, "data", "futures", "adjusted_prices_csv", "GDX.csv")
gld_path = os.path.join(base_dir, "data", "futures", "adjusted_prices_csv", "GLD.csv")


prices = []

def initialize_prices():
    if not os.path.exists(gdx_path) or not os.path.exists(gld_path):
        raise FileNotFoundError("GDX or GLD data files not found. Please check the paths.")
    
    gdx = pd.read_csv(gdx_path)
    gld = pd.read_csv(gld_path)

    gdx = gdx[['Date', 'Adj Close']]
    gld = gld[['Date', 'Adj Close']]

    global prices

    gdx.dropna(inplace=True)
    gld.dropna(inplace=True)
    gld['Date'] = pd.to_datetime(gld['Date'])
    gdx['Date'] = pd.to_datetime(gdx['Date'])
    prices = pd.merge(gld, gdx, on='Date', how='inner')
    prices.rename(columns={'Adj Close_x': 'GLD', 'Adj Close_y': 'GDX'}, inplace=True)
    prices.sort_values(by='Date', inplace=True)

    model = RollingOLS(prices['GLD'], sm.add_constant(prices['GDX']), window=200)
    results = model.fit()
    prices['hedge_ratio'] = results.params['GDX']
    prices['spread'] = prices['GLD'] - prices['hedge_ratio'] * prices['GDX']
    prices['spread_mean'] = prices['spread'].rolling(200).mean()
    prices['spread_std'] = prices['spread'].rolling(200).std()
    prices['z_score'] = (prices['spread'] - prices['spread_mean']) / prices['spread_std']

def get_prices():
    if not prices:
        print("Initializing prices...")
        initialize_prices()
    return prices


