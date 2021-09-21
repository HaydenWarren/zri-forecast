#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 18:03:57 2021

@author: haydenlw4
"""

import pandas as pd
import numpy as np


weather = pd.read_csv('weather.csv', 
                   parse_dates=['Time'], 
                   usecols = ['Time', 'zip_code', 'mintempC']
                  )

sales_tax = pd.read_csv('sales_tax_allocation.csv', 
                   parse_dates=['Time'],
                    usecols = ['Time', 'zip_code', 'sales_tax_rate', 
                               'total_sales_tax']
                  )

polls = pd.read_csv('poll_clean.csv', 
                   parse_dates=['Time'],
                   usecols = ['Time', 'tx_is_abt_same', 'tx_is_better', 
                              'tx_is_worse', 'zip_code']
                  )

econ = pd.read_csv('key_econ.csv', 
                   parse_dates=['Time'],
                   usecols = ['Time','zip_code',
                              'Gross Value Natural Gas Production',
                              'Single Family Building Permits TX']
                  )

shiller = pd.read_csv('sap_case_shiller.csv', 
                   parse_dates=['Time'],
                   usecols = ['zip_code', 'Time', 'sap_case_shiller_index']
                  )

taxpayer = pd.read_csv('new_biz_taxpayer.csv', 
                   parse_dates=['Time'],
                   usecols = ['Time', 'zip_code', 'taxpayer_count',
                              'taxpayer_cl_ratio', 'taxpayer_is_ratio', 
                              'taxpayer_foreign_ratio']
                  )
from functools import reduce
dfs = [weather, sales_tax, polls, econ, shiller, taxpayer]
feats_raw = reduce(lambda left,right: pd.merge(left,right,how='outer',on=['Time','zip_code']), dfs)

feats_raw = feats_raw.sort_values('Time').reset_index(drop = True)

feats_pct = feats_raw.set_index(['Time']).copy()
features_pct_change_list = []

for zip_code in feats_pct.zip_code.unique():
    individual_zip_pct = feats_pct.loc[feats_pct['zip_code']==zip_code,:
                                       ].pct_change(periods = 12,
                                                     limit = 6)
    individual_zip_pct.loc[:,'zip_code'] = zip_code
    features_pct_change_list.append(individual_zip_pct)
    
feats_pct = pd.concat(features_pct_change_list)
feats_pct = feats_pct.replace([np.inf, -np.inf], np.nan).sort_values('Time')
feats_pct = feats_pct.drop(columns = ['taxpayer_foreign_ratio'])
feats_pct = feats_pct.reset_index()

pct_cols = [
    'mintempC', 'sales_tax_rate', 'total_sales_tax',
    'tx_is_abt_same', 'tx_is_better', 'tx_is_worse',
    'Single Family Building Permits TX',
    'Gross Value Natural Gas Production', 
    'sap_case_shiller_index', 'taxpayer_count', 
    'taxpayer_cl_ratio', 'taxpayer_is_ratio',
                ]
for pct_col in pct_cols:
    third_quatile = feats_pct.loc[:,pct_col].quantile(.75)
    date_min = pd.Timestamp(
        feats_pct.loc[~feats_pct[pct_col].isna(),
                                  'Time'].dt.date.min())
    date_max = pd.Timestamp(
        feats_pct.loc[~feats_pct[pct_col].isna(),
                              'Time'].dt.date.max())

    feats_pct.loc[
        (feats_pct['Time']> date_min) & 
        (feats_pct['Time']< date_max), pct_col
        ] = feats_pct.loc[
            (feats_pct['Time']> date_min) & 
            (feats_pct['Time']< date_max), pct_col
            ].fillna(third_quatile)

    
    
feats_all = feats_raw.merge(feats_pct, how = 'left', 
                            on = ['Time','zip_code'], 
                            suffixes = (None,'_annual_pct_change'))
    
feats_all.to_csv('merged_texas_data.csv')


