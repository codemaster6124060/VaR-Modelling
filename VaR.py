# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 22:08:28 2022

@author: banik
"""
# Importing necessary libraries
import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import math
import scipy.stats
from scipy.stats import norm, t

#Test libyaml vs pyyaml, default to pyyaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
    print("Using libyaml")
except ImportError:
    print("Using pyyaml")
    from yaml import Loader, Dumper

# Key Facts of the portfolio
w1 = float(input(f'Weight of first ETF in the portfolio: '))
w2 = round((1 - w1),2)
print(f'Weight of second ETF in the portfolio: {w2}')
Portfolio_value = float(input(f'Portfolio value in USD: $'))
confidence_level = float(input(f'Confidence level (1 - alpha): '))

#-----------------------------------------------------------------------------#
# Historical VaR
#-----------------------------------------------------------------------------#
# Get daily return data of two ETFs from a specific class
def get_daily_return_data (Yaml,period):
    cwd = "C:/Users/banik/OneDrive/Desktop/Innovation in quantitative finance/5550/Module1/inputs"
    filename = f'{Yaml}.yaml'
    stream = open(os.path.join(cwd,filename))
    data = load(stream, Loader=Loader)
    data = pd.DataFrame(data[f'{Yaml}'])
    data = data.iloc[:,0].tolist()
    print(f'The range of metal tickers is between 0 and {len(data) - 2}')
    i = int(input('Choose any number from the range:' ))
    df= yf.Tickers(data).history(period,'1d').Close.iloc[:,i:i+2]
    df[f'{df.columns[0]} Log Price'] = np.log(df.iloc[:,0])
    df[f'{df.columns[1]} Log Price'] = np.log(df.iloc[:,1])
    df[f'{df.columns[0]} Log Return'] = df.iloc[:,2].pct_change()
    df[f'{df.columns[1]} Log Return'] = df.iloc[:,3].pct_change()
    df[f'{df.columns[0]} normal Return'] = df.iloc[:,0].pct_change()
    df[f'{df.columns[1]} normal Return'] = df.iloc[:,1].pct_change()
    return df
Yaml_type = input('Choose any type of YAML File e.g. Agriculture,Currency,Energy_Tickers,Interest,Metal,Treasury: ').capitalize()
# get_daily_return_data (Yaml_type,'1y')
df = get_daily_return_data (Yaml_type,'1y')
df.to_excel('VaR.xlsx')
print(f'Portfolio consists of two ETFs: {df.columns[0]} and {df.columns[1]}')

def Portfolio_return(w1,w2):
    ret = w1*df.iloc[:,0].pct_change() + w2*df.iloc[:,1].pct_change()
    return ret

def Portfolio_std(w1,w2):
    std = np.sqrt(math.pow(w1,2)*np.var(df.iloc[:,6])+math.pow(w2,
        2)*np.var(df.iloc[:,7])+2*w1*w2*scipy.stats.pearsonr(
            df.iloc[:,6].replace(np.nan,0),df.iloc[:,7].replace(
                np.nan,0))[0]*np.std(df.iloc[:,6])*np.std(df.iloc[:,7]))
    return std

# Estimation of VAR and Expected Shortfall under Full loss and Lineary Loss
def Full_loss(Portfolio_value,w1,w2,df):
    # df = get_daily_return_data (Yaml_type,'1y')
    Full_loss = -Portfolio_value*(w1*np.exp(df.iloc[:,-1])-1+w2*np.exp(df.iloc[:,-2]))
    return Full_loss

def Linear_loss(Portfolio_value,w1,w2,df):
    # df = get_daily_return_data (Yaml_type,'1y')
    Linear_loss = -Portfolio_value*((w1*df.iloc[:,-1])+w2*df.iloc[:,-2])
    return Linear_loss

def ValueAtRisk(loss_type,confidence_level):
    sorted_df = loss_type.sort_values(ascending=True)
    VaR = sorted_df.quantile(q=confidence_level,interpolation='higher')
    return VaR

def ExpectedShortfall(loss_type,confidence_level):
    sorted_df = loss_type.sort_values(ascending=True)
    Multiplier = 1/((1-confidence_level)*len(sorted_df))
    VaR = ValueAtRisk(loss_type,confidence_level)
    First_term = VaR
    Second_term = (sorted_df.searchsorted(VaR)+1)-len(sorted_df)*confidence_level
    Third_term = sum(sorted_df[sorted_df>VaR])
    ES = Multiplier*(First_term*Second_term+Third_term)
    return ES

# Estimating Portfolio VaR and Expected Shortfall with 70/30 weight ratio

print(f'Full Loss VaR: ${round(ValueAtRisk(Full_loss(Portfolio_value,w1,w2,df),confidence_level),2)}')
print(f'Linear Loss VaR: ${round(ValueAtRisk(Linear_loss(Portfolio_value,w1,w2,df),confidence_level),2)}')
print(f'Full Loss Expected Shortfall: ${round(ExpectedShortfall(Full_loss(Portfolio_value,w1,w2,df),confidence_level),2)}')
print(f'Linear Loss Expected Shortfall: ${round(ExpectedShortfall(Linear_loss(Portfolio_value,w1,w2,df),confidence_level),2)}')
# print(f'''
# Conditional Value at Risk (Full Loss) at the given confidence level: ${round(
#     (ExpectedShortfall(Full_loss(1000000,0.7,0.3,df),0.95)-
#      ValueAtRisk(Full_loss(1000000,0.7,0.3,df),0.95)),2)}
#     ''')
# print(f'''
# Conditional Value at Risk (Linear Loss) at the given confidence level: ${round(
#     (ExpectedShortfall(Linear_loss(1000000,0.7,0.3,df),0.95)-
#      ValueAtRisk(Linear_loss(1000000,0.7,0.3,df),0.95)),2)}
#     ''')
    
#-----------------------------------------------------------------------------#
# Parametric VaR
#-----------------------------------------------------------------------------#
PortRet = Portfolio_return(w1,w2).mean()
PortStd = Portfolio_std(w1,w2)
print(f'Portfolio Return: {round(PortRet*100,2)}%')
print(f'Portfolio Standard Deviation: {round(PortStd*100,2)}%')
dof=df.count()[0] - 1
def Parametric_VaR(distribution='normal'):
    if distribution == 'normal':
        VaR = norm.ppf(confidence_level)*PortStd - PortRet
    elif distribution == 't-distribution':
        nu = dof
        VaR = np.sqrt((nu-2)/nu)*t.ppf(confidence_level,nu)*PortStd - PortRet
    else:
        raise TypeError('Expected returns to be normal or t-distribution')
    return round(VaR*Portfolio_value,0)
    
def Parametric_CVaR(distribution='normal'):
    if distribution == 'normal':
        CVaR = math.pow((1-confidence_level),-1) * norm.pdf(norm.ppf(1-confidence_level))*PortStd - PortRet
    elif distribution == 't-distribution':
        nu = dof
        critical_value = t.ppf((1-confidence_level),nu)
        CVaR = -1/(1-confidence_level)*math.pow((1-nu),-1)*(
            nu-2+math.pow(critical_value,2))*t.pdf(critical_value,nu)*PortStd - PortRet
    else:
        raise TypeError('Expected returns to be normal or t-distribution')
    return round(CVaR*Portfolio_value,0)

print(f'''
Parametric VaR with normal distribution at {confidence_level*100}% CI: ${Parametric_VaR(distribution='normal')}
                          ''')
print(f'''
Parametric CVaR with normal distribution at {confidence_level*100}% CI: ${Parametric_CVaR(distribution='normal')}
                          ''')
print(f'''
Parametric VaR with Student's t-distribution at {confidence_level*100}% CI: ${Parametric_VaR(distribution='t-distribution')}
                          ''')
print(f'''
Parametric CVaR with Student's t-distribution at {confidence_level*100}% CI: ${Parametric_CVaR(distribution='t-distribution')}
                          ''')
                          
#-----------------------------------------------------------------------------#
# Historical Monte Carlo Value at Risk and Conditional Value at Risk
#-----------------------------------------------------------------------------#

def monteCarloVaR():
    if isinstance(Portfolio_return(w1,w2).replace(np.nan,0), pd.Series):
        return np.percentile(Portfolio_return(w1,w2).replace(np.nan,0),((1-confidence_level)*100))
    else:
        raise TypeError('Expected a Pandas data series')
        
def monteCarloCVaR():
    if isinstance(Portfolio_return(w1,w2).replace(np.nan,0),pd.Series):
        belowVaR = Portfolio_return(w1,w2).replace(np.nan,0) <= monteCarloVaR()
        return Portfolio_return(w1,w2).replace(np.nan,0)[belowVaR].mean()
    else:
        raise TypeError('Expected a Pandas data series')
        
print(f'Monte Carlo VaR at {confidence_level*100}% CI: ${round(abs(monteCarloVaR()*Portfolio_value),0)}')
print(f'Monte Carlo CVaR at {confidence_level*100}% CI: ${round(abs(monteCarloCVaR()*Portfolio_value),0)}')













