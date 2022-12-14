#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 15:53:29 2022

@author: byersjw
"""

import os
import pandas as pd
from datetime import datetime, timedelta

# check if goto-label is installed and install if necessary
# this should be in our setup.py install_requires
# try:
#     from goto import goto, label
# except ModuleNotFoundError:
#     sys.exit("""You need goto-label
#                 run pip install goto-label.""")

cwd = '/home/byersjw/work/repo/5550/Module1/pycode'
os.chdir(cwd)

#Test libyaml vs pyyaml, default to pyyaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
    print("Using libyaml")
except ImportError:
    print("Using pyyaml")
    from yaml import Loader, Dumper

import TurtleInputs as TurtleInputs
import TurtleCalcs as TurtleCalcs
import TurtleStrategy as TurtleStrategy

cwd = '/home/byersjw/work/repo/5550/Module1/inputs'

filename = 'Currency.yaml'
start = "2005-01-01"
end = "2022-12-31"

stream = open(os.path.join(cwd,filename))
data = load(stream, Loader=Loader)

data = pd.DataFrame(data['Currency'])

inputs=TurtleInputs.TurtleInputs(tickers=data, data={}, start=start, end=end)

inputs.load_data()

calcs = TurtleCalcs.TurtleCalcs()

inputs.data = calcs.seed(inputs.data)
inputs.data = calcs.calcN(inputs.data)

# Main algorithm

item = "FXA"

strategy = TurtleStrategy.TurtleStrategy(strategyType=20, 
                                         startDate=inputs.data[item].index[20] 
                                         + pd.tseries.offsets.BusinessDay(n = 1))

for row in inputs.data[item].itertuples():
    jump = False
    
    #seed for trigger prices
    if row[0] < strategy.startDate: #==  inputs.data[item].index[0]:
        strategy.setPortfolio(row,  row[0], inputs.capital)
        jump = True
        # goto skip
   
    #if Triggered buy at open
    if strategy.triggered == True:
        strategy.buy(row, row.Open)
        strategy.triggered = False

    #sell is triggered
    if strategy.sellTriggered == True:
        strategy.sell(row, row.Open)
        strategy.sellTriggered = False
        strategy.units = 0

    #Check if hold position, if so calculate MTM and Capital, only need to 
    # check after first day
    if row[0]  >=  strategy.startDate:
        #set trigger1 price, update each day
        strategy.setTrigger1(row.H20Day, row.N)
        strategy.calcMtM(row)

    #Check if MKT = +/- 4 skip all following since can't transact anymore units
    if strategy.MKT == 4 or strategy.MKT == -4:
        jump = True
        # goto skip
   
    #Check if triggered and transact based on MKT state long (+)/short(-)
    #Check if trigger1 and MKT = 0
    if jump == False and strategy.MKT == 0 and row.Close > row.H20Day:
        #buy Units
        strategy.setStop(row.H20Day, row.N)
        strategy.N = row.N
        strategy.setUnits(row.Close)
        strategy.triggered = True
        strategy.setTrigger1(row.H20Day, row.N)
        strategy.MKT = 1
        jump = True
        print('Buy ', row[0], row.Close, strategy.units, strategy.portfolio.loc[row[0],'Position'])
        # goto skip
    
    #Check if trigger2 and MKT = +/- 1
    if jump == False and strategy.MKT == 1 and row.Close > strategy.trigger2:
        #buy next units and strategy.MKT=2
        print('Buy 2nd ', row[0], row.Close, strategy.units, strategy.portfolio.loc[row[0],'Position'])
        strategy.setStop(row.H20Day, strategy.N)
        strategy.triggered = True
        strategy.MKT = 2
        jump = True
        # goto skip

    #Check if trigger3 and MKT = +/- 2, strategy.portofolio.loc[row[0],'Position']
    if jump == False and strategy.MKT == 2 and row.Close > strategy.trigger3:
        #buy next units and MKT=3
        print('Buy 3rd ', row[0], row.Close, strategy.units, strategy.portfolio.loc[row[0],'Position'])
        strategy.setStop(row.H20Day, strategy.N)
        strategy.triggered = True
        strategy.MKT = 3
        jump = True
        # goto skip
        
    #Check if trigger4 and MKT = +/- 3
    if jump == False and strategy.MKT == 3 and row.Close > strategy.trigger4:
        #buy last units and MKT=4
        print('Buy last units ', row[0], row.Close, strategy.units, strategy.portfolio.loc[row[0],'Position'])
        strategy.setStop(row.H20Day, strategy.N)
        strategy.triggered = True
        strategy.MKT = 4
        jump = True
        # goto skip
                    
    #Check if exit triggered
    #Exit and Stop should be check on all rows
    if strategy.MKT > 0 and row.Close < row.L10Day:
        #sell all units
        print('Exiting, Sell all units ', row[0], row.Close, strategy.portfolio.loc[row[0],'Position'])
        strategy.sellTriggered == True
        strategy.MKT = 0
        
    #Check if stop triggered
    if strategy.MKT > 0 and row.Close < strategy.stopPrice:
        #sell all units
        print('Stopped out, Sell all units ', row[0], row.Close, strategy.portfolio.loc[row[0],'Position'])
        strategy.sellTriggered == True
        strategy.MKT = 0
        
#Label: skip
# print(row[0], row.Close)
############################################################################