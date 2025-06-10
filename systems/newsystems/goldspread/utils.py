import numpy as np
import pandas as pd
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import os
from pykalman import KalmanFilter

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


    kf = KalmanFilter(
        transition_matrices = [1],           # r_t = r_{t-1} + noise where r_t is the hedge ratio
        observation_matrices = prices[asset2].values.reshape(-1, 1, 1),  # y_t = x_t * r_t + noise
        transition_covariance = 1e-4,#3e-3,        # process noise Q, how quickly the hedge ratio can change. this will give standard deviation of r about 0.3 over 30 days
                                                    # I plotted the spread to see when there were persisting signals. I feel like it's still too easily varying.
        observation_covariance = 2,       # measurement noise R, it's quite large but because we don't have normalised prices
        initial_state_mean = 2, # initial hedge ratio - I just chose this but we should fit with ols or otherwise
        initial_state_covariance = 1 # moderate uncertainty - try changing this to see affect
    )
    state_means, state_covariances = kf.filter(prices[asset1].values)
    prices['hedge_ratio']= state_means.flatten()
    prices['hedge_ratio_std'] = np.sqrt(state_covariances.flatten())
    prices['spread'] = prices[asset1] - prices['hedge_ratio'] * prices[asset2]
    halflife = 100

    prices['spread_mean'] = prices['spread'].ewm(halflife=halflife).mean()
    prices['spread_std'] = prices['spread'].ewm(halflife=halflife).std()

    prices['z_score'] = (prices['spread'] - prices['spread_mean']) / prices['spread_std']
    # model = RollingOLS(prices[asset1], sm.add_constant(prices[asset2]), window=100)
    # results = model.fit()
    # prices['hedge_ratio'] = results.params[asset2]
    # prices['spread'] = prices[asset1] - prices['hedge_ratio'] * prices[asset2]
    # prices['spread_mean'] = prices['spread'].rolling(100).mean()
    # prices['spread_std'] = prices['spread'].rolling(100).std()
    # prices['z_score'] = (prices['spread'] - prices['spread_mean']) / prices['spread_std']
    
    prices.set_index('Date', inplace=True)


def get_prices(asset1, asset2):
    global prices

    if prices is None:
        print("Initializing prices...")
        initialize_prices(asset1, asset2)

    return prices


