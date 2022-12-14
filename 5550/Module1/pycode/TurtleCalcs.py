"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

Created on Thu Sep 22 15:11:03 2022


Turtle Rules Calculations Class
@author: byersjw
"""

class TurtleCalcs():
   # import pandas as pd
   # import yfinance as yf

    def __init__(self):
        
        pass
    
    #set PDC
    def setPDC(self, obj):
        return obj.Close.shift(1)
    
    # calculate 10 day Short exit trigger
    def c10dayHigh(self, obj):
        return obj.Close.rolling(10).max()
    
    # calculate 10 day Long exit trigger
    def c10dayLow(self, obj):
        return obj.Close.rolling(10).min()
    
    #N normalized volatility
    def calcN(self, obj):
        
        for item in obj:
            
            obj[item]['N'] = obj[item].TrueRange.ewm(alpha=1/20, 
                                                adjust=False).mean()
        return obj
     
#    calculate strategy entry triggers
#    Strategy 1: 20 day high buy side use t=20, q=.75
#    Strategy 1: 20 day low sell side use t=20, q=.25
#    Strategy 2: 55 day high buy side use t=20, q=.75
#    Strategy 2: 55 day low sell side use t=20, q=.25
    def strategyHighLow(self, obj, t=20, q=.75):
        return obj.Close.rolling(t).quantile(quantile=q)

    #calculate the true range
    def trueRange(self, obj):
        import pandas as pd
        
        A = pd.DataFrame(obj.High - obj.Low)
        B = pd.DataFrame(obj.High - obj.PDC)
        C = pd.DataFrame(obj.PDC - obj.Low)
        return pd.merge(pd.merge( A, B, on = 'Date'),C, on ='Date').max(axis=1)
    
    #Seed input data
    def seed(self, obj):
        
        for item in obj:
            obj[item]['PDC'] = self.setPDC(obj[item])
            obj[item]['TrueRange'] = self.trueRange(obj[item])
            obj[item]['H10Day'] = self.c10dayHigh(obj[item])
            obj[item]['L10Day'] = self.c10dayLow(obj[item])
            obj[item]['H20Day'] = self.strategyHighLow(obj[item], 20, .75)
            obj[item]['L20Day'] = self.strategyHighLow(obj[item], 20, .25)
            obj[item]['H55Day'] = self.strategyHighLow(obj[item], 55, .75)
            obj[item]['L55Day'] = self.strategyHighLow(obj[item], 55, .25)

        return obj

    #Specific Trading calculation follow
    def addUnitsPrice(self, N):
        return .5 * N
    
    def stopPrice(self, N):
        return 2 * N

    def dollarVolatity(self, N, DpP):
        return N * DpP
    
    
# =============================================================================
#     import yfinance as yf
#     d = yf.download('FXA', start=start, end=end)
# 
# =============================================================================
