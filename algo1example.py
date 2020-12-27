import numpy as np

class DynamicOptimizedCoil(QCAlgorithm):

    """
    Example of a simple trading algorithm to detect price breakouts. The algorithm determines relative price high based on a previous
    period. The size of this period is determined by the volatility of the stock - if volatility is high, then the period will look
    further into the past to determine a relative high, and will be a more recent period if volatility is low. If the price rises
    above this previous high, then the algorithm will trigger a buy. A stop loss will be generated based on the price movement beyond
    the previous high, so a significant price breakout will result in a higher stoploss. 
    """

    def Initialize(self):
        self.SetCash(1000) #sets our initial amount of capital to be used for backtesting
        self.SetStartDate(2017,9,1) #sets start date to September 1, 2017
        self.SetEndDate(2020,9,1) #sets end date to September 1, 2020
        
        #symbol of the stock that we are examining, in this case is SPY S&P 500 Index tracker
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        #determines # of days we are looking back at for price highs, as well as variation due to volatility (+/- 10 days)
        self.lookback = 20
        self.ceiling, self.floor = 30, 10
        
        #indicates how close the inital stop loss will be to the security's price (allows for 2% loss)
        self.initialStopRisk = 0.98
        self.trailingStopRisk = 0.9
        
        #dictates to call Every market open method every trading day
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), \
                        self.TimeRules.AfterMarketOpen(self.symbol, 20), \
                        Action(self.EveryMarketOpen))


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        
        #plots a price chart for the security we are examining
        self.Plot("Data Chart", self.symbol, self.Securities[self.symbol].Close)
        
     
    #method that contains trading algorithm    
    def EveryMarketOpen(self):
        
        #determine the length of lookback window based on volatility
        close = self.History(self.symbol, 31, Resolution.Daily)["close"]
        todayvol = np.std(close[1:31])
        yesterdayvol = np.std(close[0:30])
        deltavol = (todayvol - yesterdayvol) / todayvol
        self.lookback = round(self.lookback * (1 + deltavol))
        
        #check if lookback length is within previously defined upper and lower limits: if it isn't, make sure it is
        #otherwise, do nothing
        if self.lookback > self.ceiling:
            self.lookback = self.ceiling
        elif self.lookback < self.floor:
            self.lookback = self.floor
        
        #check to see if a price breakout is happening
        self.high = self.History(self.symbol, self.lookback, Resolution.Daily)["high"]
        
        #check that we aren't currently invested
        if not self.Securities[self.symbol].Invested and \
                self.Securities[self.symbol].Close >= max(self.high[:-1]):
            self.SetHoldings(self.symbol, 1)
            self.breakoutlvl = max(self.high[:-1])
            self.highestPrice = self.breakoutlvl
            
        #create trading stop loss
        if self.Securities[self.symbol].Invested:
            if not self.Transactions.GetOpenOrders(self.symbol):
                self.stopMarketTicket = self.StopMarketOrder(self.symbol, \
                                        - self.Portfolio[self.symbol].Quantity, \
                                        self.initialStopRisk * self.breakoutlvl)
            
            #update stop loss with price movement during a breakout period (don't want it to move below initial stop loss price)                            
            if self.Securities[self.symbol].Close > self.highestPrice and \
                    self.initialStopRisk * self.breakoutlvl < self.Securities[self.symbol].Close * self.trailingStopRisk:
                self.highestPrice = self.Securities[self.symbol].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.Securities[self.symbol].Close * self.trailingStopRisk
                self.stopMarketTicket.Update(updateFields)
                
                self.Debug(updateFields.StopPrice)
            
            self.Plot("Data Chart", "Stop Price", self.stopMarketTicket.Get(OrderField.StopPrice))