#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Wed Aug 31 11:29:25 2022

@author: byersjw


Risk Measures class
"""

import pandas as pd

class RiskModel(object):
   # import pandas as pd
   # import yfinance as yf

    def __init__(self, tickers=None, data=None, start=None, end=None, alpha=0.95):
        self.tickers = tickers
        self.data = data
        self.start = start
        self.end = end
        self.returns = None
        if alpha > .5:  # if passed lower tail accept it otherwise 1-alpha
            alpha = 1 - alpha
            

    def load_data(self):
        import yfinance as yf

        self.data = {} #pd.DataFrame()
        for item in self.tickers.index:
            print(item)
            raw = yf.Ticker(item)
            self.data[item] = raw.history(start=self.start, end=self.end, 
                                          auto_adjust=False)
            self.data[item] = self.data[item].drop(columns = 
                                ['Volume', 'Dividends', 'Stock Splits', 
                                 'Open', 'Low', 'High', 'Close'])

    def to_dataFrame(self, obj):
        t1 = pd.DataFrame(columns=['ticker', 'name', 'OuterKey', 
                                   'InnerKey']).set_index('ticker')
        for item in obj:
            for key1 in obj[item]:
                temp = pd.DataFrame(obj[item][key1]).set_index('ticker')
                temp['OuterKey'] = item
                temp['InnerKey'] = key1
                t1 = t1.append(temp)
                
        return t1
    
    def var_Parametric(self, alpha, mu, sigma):
        import numpy as np
        from scipy.stats import norm
        if alpha > .5:
            alpha = 1-alpha
        
        # mu + norm.ppf(alpha,0,1) * sigma
        return norm.ppf(alpha, mu, sigma)
    
    def var_Historical(self, alpha, returns, w):
        import numpy as np
        
        if alpha > .5:
            alpha = 1-alpha
        returns = np.matmul(returns,np.transpose(w))
        var = returns.quantile(q=alpha, interpolation="higher")
        
        return var

    def tvar_Parametric(self, alpha, mu, sigma):
        import numpy as np
        from scipy.stats import norm
        if alpha > .5:
            alpha = 1-alpha
        
        return -mu - sigma * norm.pdf(norm.ppf(alpha, 0, 1),0,1) / (alpha)
    
    def tvar_Historical(self, alpha, returns, w):
        import numpy as np
        if alpha > .5:
            alpha = 1-alpha
        
        returns = np.matmul(returns,np.transpose(w))
        var = returns.quantile(q=alpha, interpolation="higher")
        tvar = returns[returns<var].mean()
        return tvar
