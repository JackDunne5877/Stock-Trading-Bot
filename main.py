from Portfolio.MeanVarianceOptimizationPortfolioConstructionModel import MeanVarianceOptimizationPortfolioConstructionModel
from TechnologyUniverseModule import TechnologyUniverseModule
import pandas as pd
from training_model2 import training_model

class FundamentalMLalgo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 7, 1)  # Set Start Date
        self.SetEndDate(2020, 7, 1) #set End Date
        self.SetCash(1000)  # Set Strategy Cash

        self.AddUniverse(self.MyCoarseFilterFunction, self.MyFineFundamentalFunction)
        
        self.SetPortfolioConstruction(MeanVarianceOptimizationPortfolioConstructionModel())
        
        self.SetRiskManagement(TrailingStopRiskManagementModel(0.03))
        
        #add S&P500 benchmark
        self.AddEquity("SPY", Resolution.Daily)
        self.SetBenchmark("SPY")
        
        train_model = training_model(ViewUniverse())
    
    def ViewUniverse(self):
        for universe in self.UniverseManager.Values:
            if universe is UserDefinedUniverse:
                continue
            symbols = universe.Members.Keys
            symbol_list = []
            
            for symbol in symbols:
                symbol_list.append(symbol)
        return symbol_list
        
        
    def MyCoarseFilterFunction(self, coarse):
        sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
        filtered = [ x.Symbol for x in sortedByDollarVolume 
                  if x.Price > 10 and x.DollarVolume > 10000000 ]
        return filtered[:500]

    def MyFineFundamentalFunction(self, fine):
        pass

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        '''
        use prediction model created in training_model to examine stock universe and make trades based on model.
        '''