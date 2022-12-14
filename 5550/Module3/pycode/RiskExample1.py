#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 14:35:28 2022

@author: byersjw
"""

import matplotlib.pyplot  as plt
x = [-100,0,50,200,500]
p = [.2, .5, .25, .04, .01]
tvar90 = 155
tvar99 = 600
cte90 = 260
cte99 = 500

# defining plot size 
plt.figure() #(figsize = (10, 7)) 

plt.plot(x,p, label='Distribution')
plt.axvline(x=tvar90, ymin = 0, ymax = max(p), label='TVaR90', color='red')
plt.axvline(x=tvar99, ymin = 0, ymax = max(p), label='TVaR99', color='orange')
plt.axvline(x=cte90, ymin = 0, ymax = max(p), label='CTE90', color='purple')
plt.axvline(x=cte99, ymin = 0, ymax = max(p), label='CTE99', color='green')
plt.legend(loc='upper right');

plt.show() 
