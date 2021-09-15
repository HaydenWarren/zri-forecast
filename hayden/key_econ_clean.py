#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 19:13:27 2021

@author: haydenlw4
"""

import pandas as pd

econ = pd.read_csv('Key_Economic_Indicators.csv')

econ = econ[econ['Year']>=2012].reset_index(drop=True)
econ = econ.dropna(axis = 'columns', thresh=100)
econ['State'] = 'TX'

econ.to_csv('key_econ.csv')