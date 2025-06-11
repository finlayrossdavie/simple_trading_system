class Config:
    def __init__(self, entry_threshold, exit_threshold, asset1, asset2, initial_capital, risk_free_rate=0.00):
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.asset1 = asset1
        self.asset2 = asset2
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate