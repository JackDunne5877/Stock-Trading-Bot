"""
Strategy buys stocks directly after a company's earnings announcement, focusing on stocks
that had a negative trend following an earnings report. Assuming that we pick the right companies, the stock
will hopefully rebound, allowing us to capitalize on the price fluctuation. Focusing on highly liquid and well
known entities. Establish a long position until our trailing stop loss is hit.
"""

class HorizontalDynamicCircuit(QCAlgorithm):
    
    def Initialize(self):
        #set the backtest window for two years (2018 - 2020), and set initial capital
        #to $100000
       self.SetStartDate(2018, 10, 1)
       self.SetEndDate(2020, 10, 1)
       self.SetCash(100000)
       
       #initialize stock universe settings (works on daily data)
       self.UniverseSettings.Resolution = Resolution.Daily

       #initialize our company filters, coarse filter evaluates securities by price, volume, etc. Fine filter
       #leaves us with securities that have a price dip after a recent earnings call
       self.AddUniverse(self.CoarseSelection, self.FineSelection)
       
       #variables to hold potential trades, open positions, and orders
       self.longSymbols = []
       self.entryPrices = {}
       self.highestPrice = {}
       self.stopMarketTicket = {}
       
       #creates bar chart for open positions
       stockPlot = Chart("Positions")
       stockPlot.AddSeries(Series("Longs", SeriesType.Bar, 0))
       self.AddChart(stockPlot)
       
       #creates benchmark as the S&P 500 and adds to chart
       self.AddEquity("SPY", Resolution.Daily)
       self.SetBenchmark("SPY")
       
       #initializes our main trading method, implementing it daily at 10am
       self.Schedule.On(self.DateRules.EveryDay("SPY"), \
                        self.TimeRules.At(10, 00), \
                        self.EveryMarketOpen)
       #parameter that specifies how far the stock price should fall after earnings
       self.entryMove = 0.02
       #how maximum positions we want open at once
       self.maxPositions = 10
       #how many stocks should be in the coarse filter
       self.numOfCourse = 6 * self.maxPositions
       #how many days we want to check after earnings
       self.daysSinceEarnings = 1
       #10 percent trailing stop loss (wide loss allows for price movement)
       self.stopLoss = 0.10
        
    #coarse filter    
    def CoarseSelection(self, coarse):
        #generates data to check earnings date, descending by dollar volume (metric for liquidity)
        selectedByDollarVolume = sorted([x for x in coarse if x.Price > 5 and x.HasFundamentalData],
                                        key = lambda x: x.DollarVolume, reverse = True)
        return [x.Symbol for x in selectedByDollarVolume[:self.numOfCoarse]]
    
    #fine filter    
    def FineSelection(self, fine):
        #determines if a stocks recent earnings caused a big enough negative price movement
        fine = [x for x in fine if self.Time == x.EarningsReports.FileDate + timedelta(days=self.daysSinceEarnings)]
        symbols = [x.Symbol for x in fine]
        pricesAroundEarnings = self.History(symbols, self.daysSinceEarnings+3, Resolution.Daily)
        
        #iterate through security objects, find date closest to 1 day after earnings for each stock
        for sec in fine:
            date = min(pricesAroundEarnings.loc[sec.Symbol]["close"].index,
                        key = lambda x: abs(x-(sec.EarningsReports.FileDate - timedelta(1))))
            priceOnEarnings = pricesAroundEarnings.loc[sec.Symbol]["close"][date]
            if priceOnEarnings * (1 - self.entryMove) > sec.Price:
                self.longSymbols.append(sec.Symbol)
        return self.longSymbols

    #called at 10 am every trading day, implement actual trading and stop loss mechanisms
    def EveryMarketOpen(self):
        positions = [sec.Symbol for sec in self.Portfolio.Values if self.Portfolio[sec.Symbol].Invested]
        self.Plot("Positions", "Longs", len(positions))
        availableTrades = self.maxPositions - len(positions)
        
        #iterate over objects finely selected that aren't already an opened position, only buy as many as trades available
        for symbol in [x for x in self.longSymbols if x not in positions][:availableTrades]:
            if self.Securities.ContainsKey(symbol):
                #buys a given stock
                self.setHoldings(symbol, 1 / self.maxPositions)
        
        #reset stock list so the same stocks aren't bought again        
        self.longSymbols = []
        
        #implements trailing stop loss
        for symbol in positions:
            if not self.Transactions.GetOpenOrders(symbol):
                self.stopMarketTicket[symbol] = self.StopMarketOrder(symbol, \
                                        -self.Portfolio[symbol].Quantity, \
                                        (1-self.stopLoss)*self.entryPrices[symbol])
            elif self.Securities[symbol].Close > self.highestPrice[symbol]:
                self.highestPrice[symobl] = self.Securities[symbol].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.Securities[symbol].Close * (1-self.stopLoss)
                self.stopMarketTicket[symbol].Update(updateFields)
    
    #method called on every order event, make sure that order goes through - save fill price
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self.entryPrices[orderEvent.Symbol] = orderEvent.FillPrice
            self.highestPrice[orderEvent.Symbol] = orderEvent.FillPrice