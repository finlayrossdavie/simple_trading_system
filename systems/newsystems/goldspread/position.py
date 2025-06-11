class Position:
    def __init__(self, direction, gld_units, gdx_units, entry_price_gld, entry_price_gdx, entry_date):
        self.gld_units = gld_units
        self.gdx_units = gdx_units
        self.entry_price_gld = entry_price_gld
        self.entry_price_gdx = entry_price_gdx
        self.direction = direction
        self.entry_date = entry_date
        self.exit_date = None
        self.pnl = 0.0
        self.open = True

    def calculate_value(self, current_price_gld, current_price_gdx):
        value_gld = current_price_gld * self.gld_units
        value_gdx = current_price_gdx * self.gdx_units

        if self.direction == -1:
            return value_gdx - value_gld  # Short spread: GDX - GLD
        else:
            return value_gld - value_gdx
    
        
    
    def calculate_pnl(self,current_price_gld, current_price_gdx):  
        if self.direction == -1:   #short spread
            pnl_gld = (self.entry_price_gld - current_price_gld) * self.gld_units
            pnl_gdx = (current_price_gdx - self.entry_price_gdx) * self.gdx_units
            self.pnl = pnl_gld + pnl_gdx
        else:                #long spread 
            pnl_gld = (current_price_gld - self.entry_price_gld) * self.gld_units
            pnl_gdx = (self.entry_price_gdx - current_price_gdx) * self.gdx_units
            self.pnl = pnl_gld + pnl_gdx
            
        return self.pnl
    
    def calculate_final_return(self):
        if self.pnl != 0.0:
            final_return = self.pnl / (self.entry_price_gld * self.gld_units + self.entry_price_gdx * self.gdx_units)
            return final_return
        else:
            return 0.0
    def close_position(self, date):
        self.open = False
        self.exit_date = date

    def get_pnl(self):
        return self.pnl