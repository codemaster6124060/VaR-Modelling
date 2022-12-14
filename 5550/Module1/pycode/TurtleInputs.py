"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

Created on Wed Aug 31 11:29:25 2022

@author: byersjw


Turtle Trading Rules Input class
"""


class TurtleInputs(object):
   # import pandas as pd
   # import yfinance as yf

    def __init__(self, tickers, data, start, end, capital=1000000):
        self.tickers = tickers
        self.data = data
        self.start = start
        self.end = end
        self.capital = capital
        
    def load_data(self):
        import yfinance as yf
        
        #tags = ['Open','High','Low','Close']
        #ticks = yf.Tickers(tickers)
        self.data = {} #pd.DataFrame()
        for item in self.tickers.ticker:
            raw = yf.Ticker(item)
            self.data[item] = raw.history(start=self.start, end=self.end, 
                                          auto_adjust=False)
            self.data[item] = self.data[item].drop(columns = 
                                ['Volume', 'Dividends', 'Stock Splits'])
    