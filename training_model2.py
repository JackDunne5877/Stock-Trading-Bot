import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression 
from sklearn.linear_model import LogisticRegression 
from sklearn.ensemble import RandomForestRegressor 

class training_model():
    
    def __init__(self, stock_universe):
        #create universe of stocks with fundamental data 
        self.stock_universe = stock_universe
        stock_df = pd.DataFrame()
        for x in stock_universe:
            stock_df.Add(x)
        Debug(stock_df)

    def MyCoarseFilterFunction(self, coarse):
         sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
         filtered = [ x.Symbol for x in sortedByDollarVolume 
                      if x.Price > 10 and x.DollarVolume > 10000000 ]
         return filtered[:500]

    def MyFineFundamentalFunction(self, fine):
         pass
    
    
    
#create training and test sets from dataframe 
#train_set, test_set = train_test_split(stock_df, test_size=0.25, random_state=380) 

""" 
create a stock universe of stocks: possibly random to ensure good prediction outcomes: or industry specific, 
which would then only make trades within a specific industry for each stock in universe: assemble into dataframe 
fundamental values for each stock generate the outcome variable based on date of income statement 
"""