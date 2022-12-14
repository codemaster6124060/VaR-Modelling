#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 11:29:25 2022

@author: byersjw


YAML Example and Test Script
"""

import os
import pandas as pd

#Test libyaml vs pyyaml, default to pyyaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
    print("Using libyaml")
except ImportError:
    print("Using pyyaml")
    from yaml import Loader, Dumper

cwd = '/home/byersjw/work/repo/fall20225550/YAML'
filename = 'test.yaml'

stream = open(os.path.join(cwd,filename))
data = load(stream, Loader=Loader)

dump(data)

# convert Ratchets to dataFrame
Ratchets = pd.DataFrame(data['Ratchets'])
CurveKeys = pd.DataFrame(data['DataKeys'])
ContractTerms = data['ContractTerms']
configurations = data['configurations']
Tariff = pd.DataFrame(data['Tariff'])
Company = data['Company']


##############################################################################
# from pyyaml
document = """
  a: 1
  b:
    c: 3
    d: 4
"""

print(dump(load(document, Loader=Loader)))

document = """
version: 1
Company: FSEAL
ContractTerms:
  FacilityAbbr: SouthLA
  FacilityName: South Lousiana
  dealstartdate: 04/01/2002
  enddate: 03/31/2003
  MSQ: 1000000
  test: FSEAL
"""
data = load(document, Loader=Loader)

print(dump(load(document, Loader=Loader)))
