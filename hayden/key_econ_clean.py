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
state_zip_map = zri.groupby(['State','zip_code']
                            ).agg({'zori_ssa':'sum'}).reset_index()
state_zip_map.columns = ['State', 'zip_code', 'zori_ssa']
state_zip_map = state_zip_map[['State','zip_code']]
econ['State'] = 'TX'
# performing the mapping
econ = econ.merge(state_zip_map, how = 'left', on=['State'])
econ = econ.drop(['State'], axis=1)


## credit to julie for this code block
dates_list = []
new_date = pd.to_datetime('01-01-2012')
end_date = pd.to_datetime('09-01-2021')

while new_date != end_date:
    dates_list.append(new_date)
    new_date += pd.DateOffset(months=1)
# create a dataframe that has all zipcode/Date combos
dates = pd.DataFrame(dates_list)
dates.columns = ['Time']
dates.loc[:,'merge_col'] = 'merge'
zip_codes = pd.DataFrame({'zip_code':list(zri.zip_code.unique())})
zip_codes.loc[:,'merge_col'] = 'merge'
date_zip_map = dates.merge(zip_codes, how = 'left', on = 'merge_col')
date_zip_map = date_zip_map[['Time','zip_code']]
# adding a datetime column 
econ['day'] = 1
econ['Time'] = pd.to_datetime(econ[['Year','Month','day']])
econ = econ.drop(['Month', 'Year', 'day'], axis=1)
# use that dataframe to map to dataset to create a complete dataset
econ = date_zip_map.merge(econ, how = 'left', 
                                  on = ['Time','zip_code'])


econ.to_csv('key_econ.csv')