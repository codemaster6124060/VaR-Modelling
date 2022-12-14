#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 15:53:29 2022

@author: byersjw
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

import matplotlib.pyplot as plt
from tabulate import tabulate
import math

# check if goto-label is installed and install if necessary
# this should be in our setup.py install_requires
# try:
#     from goto import goto, label
# except ModuleNotFoundError:
#     sys.exit("""You need goto-label
#                 run pip install goto-label.""")

cwd = '/home/byersjw/work/repo/5550/Module3/pycode'
os.chdir(cwd)

#Test libyaml vs pyyaml, default to pyyaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
    print("Using libyaml")
except ImportError:
    print("Using pyyaml")
    from yaml import Loader, Dumper

import RiskModel as Risk

cwd = '/home/byersjw/work/repo/5550/Module3/inputs'

filename = 'Tickers.yaml'
start = "2021-11-01"
end = "2022-12-31"
tickers = ['FXA', 'FXY']
capital = 1000000
alpha = .95
bins = 20
w = [.5, .5]

stream = open(os.path.join(cwd,filename))
data = load(stream, Loader=Loader)

Robj = Risk.RiskModel(start=start, end=end, alpha = alpha)
Robj.tickers = Robj.to_dataFrame(data)

Robj.load_data()

# Main algorithm
#filter on 2 tickers in tickers, need to move to class
Robj.returns = [Robj.data[x].pct_change() for x in tickers if x in Robj.data]
i = 0
for item in Robj.returns:
    print(tickers[i])
    item.rename(columns = {'Adj Close': tickers[i]}, inplace=True)
    if i==0:
        temp = item
    else:
        temp = temp.merge(Robj.returns[i], on='Date')
    i = i+1
Robj.returns = temp.dropna() #assign to class, move this into class

sum_stats = stats.describe(Robj.returns, axis = 0)._asdict()
sum_stats = pd.DataFrame(sum_stats, columns=sum_stats.keys()).transpose()
sum_stats.columns = tickers
print(tabulate(sum_stats, headers='keys')) #, floatfmt=".4f")) 

plt.figure() #(figsize = (10, 7)) 
Robj.returns.FXA.hist(bins = bins,density=True,histtype='stepfilled',alpha=0.5)
x = np.linspace(sum_stats.loc['mean'].FXA - 
                3*math.sqrt(sum_stats.loc['variance'].FXA), 
                sum_stats.loc['mean'].FXA + 3*math.sqrt(sum_stats.loc['variance'].FXA), 
                                100)
plt.plot(x, stats.norm.pdf(x, sum_stats.loc['mean'].FXA, math.sqrt(sum_stats.loc['variance'].FXA)), "r")
plt.title(tickers[0])
############################################################################

mu = np.matmul(Robj.returns,np.transpose(w)).mean()
bigsigma = math.sqrt(np.dot(np.dot(np.transpose(w),Robj.returns.cov()),w))

VaR = Robj.var_Parametric(alpha, 
                         np.matmul(Robj.returns,np.transpose(w)).mean(), 
                         math.sqrt(np.dot(np.dot(np.transpose(w),Robj.returns.cov()),w)))

VaR_HS = Robj.var_Historical(alpha=alpha, returns=Robj.returns, w=w)
 
TVaR = Robj.tvar_Parametric(alpha, 
                         np.matmul(Robj.returns,np.transpose(w)).mean(), 
                         math.sqrt(np.dot(np.dot(np.transpose(w),Robj.returns.cov()),w)))

TVaR_HS = Robj.tvar_Historical(alpha=alpha, returns=Robj.returns, w=w)

VaR_report = pd.DataFrame([['VaR', VaR], ['TVaR', TVaR], ['VaR_HS', VaR_HS], 
                           ['TVAR_HS', TVaR_HS]], columns=['Metric', 'Value'])
print(tabulate(VaR_report))

#test to spreadsheet
sigma =  8180.50334152092
Robj.var_Parametric(alpha, 0, 8180.50334152092)
Robj.tvar_Parametric(alpha, 0, 8180.50334152092)
