#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 19:13:27 2021

@author: haydenlw4
"""

import pandas as pd

econ = pd.read_csv('Key_Economic_Indicators.csv',
                   )
zri = pd.read_csv('target.csv', index_col = 0,
                  )
# remvoning old or missing values.
econ = econ[econ['Year']>=2012].reset_index(drop=True)
econ = econ.dropna(axis = 'columns', thresh=100)


# setting up a mapping of state to zip_code
state_zip_map = zri.groupby(['State','RegionName']
                            ).agg({'zori_ssa':'sum'}).reset_index()
state_zip_map.columns = ['State', 'zip_code', 'zori_ssa']
state_zip_map = state_zip_map[['State','zip_code']]
econ['State'] = 'TX'
# performing the mapping
econ = econ.merge(state_zip_map, how = 'left', on=['State'])

econ.to_csv('key_econ.csv')