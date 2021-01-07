from CboeVixAlphaModel import CboeVixAlphaModel

'''
Initial Algo: create two pointers that examine historical prices 14 days apart, 
if the later date pointer is higher than the earlier date pointer by a certain threshold, gather the oscillator and
moving average data for the stock at the earlier date pointer. Do this many times to assemble database of hopefully 
accurate predictors for price movement.
-average good and bad oscillator numbers, have a function that computes the difference between these values to make 
predictions. Dynamically update averages with time.
'''

class InitialTradingBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 7, 10)  # Set Start Date
        self.SetEndDate(2020, 8, 1)
        
        #creates symbol variable to track HACK cybersecurity index
        self.symbol = self.AddEquity("HACK", Resolution.Daily)
        
        #alpha models to identify trends
        self.AddAlpha(CboeVixAlphaModel(self))
        self.AddAlpha(ConstantAlphaModel(InsightType.Price, InsightDirection.Up, timedelta(minutes = 20), 0.025, None))
        
        #calls every market open to run trading algo
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), \
                        self.TimeRules.AfterMarketOpen(self.symbol, 20), \
                        Action(self.EveryMarketOpen))
                        
        


    def Update(self, algorithm, slice):
         # Updates this alpha model with the latest data from the algorithm.
         # This is called each time the algorithm receives data for subscribed securities
         # Generate insights on the securities in the universe.
         #create an insight for HACK
         hackInsight = Insight.Price("HACK", timedelta(weeks = 2), InsightDirection.Up)
         
         return hackInsight


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        #plots a price chart for the security we are examining
        self.Plot("Data Chart", self.symbol, self.Securities[self.symbol].Close)
 
    def EveryMarketOpen(self):
        return
    
#create a function that generates insights (metrics) about daily data for HACK.
#this function assembles data into a data structure that can be regressed to make predictions
