#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:43:04 2022

@author: byersjw

TurtleStrategy Class

"""
import pandas as pd

class TurtleStrategy(object):

    def __init__(self, strategyType = 20, startDate = None, dpP = 1, N = None,
                 capitalN = .01):
        self.strategyType = strategyType
        self.startDate = startDate
        self.dollarsperPoint = dpP
        self.units = None
        self.addUnitsPrice = None
        self.stopPrice = None
        self.N = N
        self.dollarVolatility = None
        self.MKT = 0
        self.capitalN = capitalN
        #self.trigger1 = None
        self.trigger2 = None
        self.trigger3 = None
        self.trigger4 = None
        self.triggered = False # determines if triggered from previous day
                               # and need to transact at open
        self.sellTriggered = False #triggered to sell at open
        self.portfolio = pd.DataFrame(columns=['Date', 'Position', 'Cost',
                            'Close', 'MtM', 'Capital']).set_index('Date')

    def calcMtM(self, obj):
        if self.portfolio.index[len(self.portfolio)-1] == obj[0]:
            #self.portfolio.loc[obj[0], :] = 0
            if self.portfolio.loc[obj[0], 'Position'] != 0:
                t1 = self.portfolio.loc[obj[0], 'Close'] - self.portfolio.loc[obj[0], 'Cost']
                t2 = self.portfolio.loc[obj[0], 'Position']
                self.portfolio.loc[obj[0], 'MtM'] = t1 * t2
                t1 = self.portfolio.loc[obj[0] - pd.tseries.offsets.BusinessDay(n = 1), 'Capital']
                self.portfolio.loc[obj[0], 'Capital'] = t1 + self.portfolio.loc[obj[0], 'MtM']
            else:
                t1 = self.portfolio.loc[obj[0] - pd.tseries.offsets.BusinessDay(n = 1), 'Position']
                self.portfolio.loc[obj[0], 'Position'] = t1
                t1 = self.portfolio.loc[obj[0] - pd.tseries.offsets.BusinessDay(n = 1), 'Cost']
                self.portfolio.loc[obj[0], 'Cost'] = t1
                self.portfolio.loc[obj[0], 'Close'] = obj.Close
                t1 = self.portfolio.loc[obj[0], 'Close'] - self.portfolio.loc[obj[0]
                + pd.tseries.offsets.BusinessDay(n = 1), 'Close']
                t2 = self.portfolio.loc[obj[0], 'Position']
                self.portfolio.loc[obj[0], 'MtM'] = t1 * t2
                t1 = self.portfolio.loc[obj[0] - pd.tseries.offsets.BusinessDay(n = 1), 'Capital']
                self.portfolio.loc[obj[0], 'Capital'] = t1 + self.portfolio.loc[obj[0], 'MtM']

        else:
            cap = self.portfolio.loc[self.portfolio.index[len(self.portfolio)-2], 'Capital']
            self.portfolio.loc[obj[0], :] = [0, 0, obj.Close, 0, cap]
        # clear positions if selling, cost < 0 and positions > 0
        if self.portfolio.loc[obj[0], 'Cost'] < 0 and self.portfolio.loc[obj[0], 'Position'] > 0:
            self.portfolio.Position = 0


    def setPortfolio(self, obj, firstdate, capital):
        # using loc to avoid SettingWithCopyWarning
            self.portfolio.loc[firstdate, :] = 0
# # do not need to set these since : sets all values to zero above
#             self.portfolio.loc[:, ('Position')] = 0
#             self.portfolio.loc[:, ('Cost')] = 0
#             self.portfolio.loc[:, ('Close')] = 0
#             self.portfolio.loc[:, ('MtM')] = 0
#reset capital to capital since set to zero from index statement above
            self.portfolio.loc[:, ('Capital')] = capital

    def setTrigger1(self, trigger, N):
        self.trigger2 = trigger + 1/2 * N
        self.trigger3 = trigger + N
        self.trigger4 = trigger + 3/2 * N

    def setStop(self, price, N):
        self.stopPrice = price - 2 * N

    def buy(self, obj, price):
        self.portfolio.loc[obj[0], :] = 0
        self.portfolio.loc[obj[0], 'Position'] = self.units + self.portfolio.Position[len(self.portfolio)-2]
        self.portfolio.loc[obj[0], 'Cost'] = price
        cap = self.portfolio.loc[self.portfolio.index[len(self.portfolio)-2], 'Capital']
        self.portfolio.loc[obj[0], 'Capital'] = cap
        self.portfolio.loc[obj[0], 'Close'] = obj.Close

    def sell(self, obj, price):
        self.portfolio.loc[obj[0], :] = 0
        self.portfolio.loc[obj[0], 'Position'] =  self.portfolio.Position[len(self.portfolio)-2]
        self.portfolio.loc[obj[0], 'Cost'] = -price
        cap = self.portfolio.loc[self.portfolio.index[len(self.portfolio)-2], 'Capital']
        self.portfolio.loc[obj[0], :] = [0, 0, obj.Close, 0, cap]

    def setUnits(self, dpP):
        cap = self.portfolio.loc[self.portfolio.index[len(self.portfolio)-2], 'Capital']
        self.units = (self.capitalN * cap) / (self.N * dpP * self.dollarsperPoint)

