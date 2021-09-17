#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 12:24:39 2021

@author: haydenlw4
"""

import pandas as pd

zri = pd.read_csv('target.csv', index_col = 0,
                   parse_dates=['Time']
                  )
new_biz_owner = pd.read_csv('new_biz_taxpayer.csv',
                      parse_dates={"Time" : ["year","month"]},
                      index_col= 1)

new_biz_outlet = pd.read_csv('new_biz_outlet_inside.csv',
                      parse_dates={"Time" : ["year","month"]},
                      index_col= 1)

sales_tax = pd.read_csv('sales_tax_allocation.csv',
                       parse_dates={"Time" : ["year","month"]},
                       index_col= 1
                      )
econ = pd.read_csv('key_econ.csv',
                        parse_dates={"Time" : ["Month","Year"]},
                       index_col= 1
                      )

zri.columns = ['zip_code', 'City', 'State', 'Time', 'zori_ssa', 'zori_ssa_diff']
zri_merged = zri.merge(new_biz_owner, how = 'left', on=['zip_code','Time'])
zri_merged = zri_merged.merge(new_biz_outlet, how = 'left', on=['zip_code','Time'])
zri_merged = zri_merged.merge(sales_tax, how = 'left', on=['zip_code','Time'])
zri_merged = zri_merged.merge(econ, how = 'left', on=['zip_code','Time'])