#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 01:12:08 2021

@author: haydenlw4
"""

# acs_variables_frame.csv
# acs_feature_list.csv

import pandas as pd
import numpy as np
import missingno as msno

acs_feat_list = pd.read_csv('acs_feature_list.csv', index_col = 0,
                   )

acs2 = pd.read_csv('acs2_clean.csv',                    
                   parse_dates=['Time'], 
                   usecols = [
                       'Time', 'zip_code',
                       'average_household_size_owners',
                        'driving_alone_population',
                        'bicycle_population',
                        'female_21',
                        'female_25_to_29',
                        'female_30_to_34',
                        'female_35_to_39',
                        'female_40_to_44',
                        'female_45_to_49',
                        'female_50_to_54',
                        'female_75_to_79',
                        'housing_units_built_1930_to_1939',
                        'housing_units_built_1940_to_1949',
                        'housing_units_built_1950_to_1959',
                        'housing_units_built_1960_to_1969',
                        'housing_units_built_1970_to_1979',
                        'housing_units_built_1990_to_1999',
                        'housing_units_built_1980_to_1989',
                        'single_women',
                        'quintile_1_upper_limit',
                        'quintile_2_upper_limit',
                        'quintile_3_upper_limit',
                        'quintile_4_upper_limit',
                        'women_with_associate_degree',
                        'women_with_doctoral_degree',
                        'men_with_bachelors_degree',
                        'median_household_income',
                        'units_paying_cash_rent',
                        'motorcycle_population',
                        'housing_units_10_to_19_units',
                        'housing_units_20_to_49_units',
                        'housing_units_5_to_9_units',
                        'housing_units_over_50_units',
                        'housing_units_single_family_attached',
                        'housing_units_single_family_attached_owned',
                        'walking_to_work_population']
                  )


acs = pd.read_csv('acs_clean.csv',                    
                   parse_dates=['Time'], 
                   usecols = [
                       'Time', 'zip_code',
                        'children',
                        'black_pop',
                        'white_pop',
                        'hispanic_pop',
                        'high_school_diploma',
                        'female_female_households',
                        'armed_forces',
                        ])
                        
                        
                        
acs_raw = pd.merge(acs, acs2, how='outer', on=['Time','zip_code'])                        


acs_pct = acs_raw.set_index(['Time']).copy()
acs_pct = acs_pct.sort_values('Time')
acs_pct_change_list = []

for zip_code in acs_pct.zip_code.unique():
    individual_zip_pct = acs_pct.loc[acs_pct['zip_code']==zip_code,:
                                        ].pct_change(periods = 12,
                                                     limit = 6)
    individual_zip_pct.loc[:,'zip_code'] = zip_code
    acs_pct_change_list.append(individual_zip_pct)
    
acs_pct = pd.concat(acs_pct_change_list)
acs_pct = acs_pct.replace([np.inf, -np.inf], np.nan).sort_values('Time')
acs_pct = acs_pct.drop(columns = ['armed_forces', 
                                  'female_female_households',
                                  'motorcycle_population', 
                                  'bicycle_population',]
)
acs_pct = acs_pct.reset_index()
pct_cols = [
    'white_pop', 'black_pop', 'hispanic_pop', 'children', 
    'high_school_diploma', 'driving_alone_population',
    'housing_units_built_1940_to_1949', 'female_45_to_49',
    'female_75_to_79', 'housing_units_built_1950_to_1959', 
    'quintile_4_upper_limit', 'quintile_3_upper_limit',
    'housing_units_10_to_19_units', 
    'housing_units_built_1970_to_1979',
    'median_household_income', 'women_with_doctoral_degree', 'female_21',
    'female_50_to_54', 'housing_units_built_1980_to_1989',
    'housing_units_built_1930_to_1939', 'female_35_to_39',
    'units_paying_cash_rent', 'housing_units_single_family_attached',
    'housing_units_20_to_49_units', 'female_25_to_29',
    'walking_to_work_population', 'men_with_bachelors_degree',
    'quintile_1_upper_limit', 'quintile_2_upper_limit',
    'women_with_associate_degree', 'female_40_to_44',
    'average_household_size_owners', 'female_30_to_34',
    'housing_units_5_to_9_units', 'single_women',
    'housing_units_built_1990_to_1999',
    'housing_units_single_family_attached_owned',
    'housing_units_over_50_units', 'housing_units_built_1960_to_1969'
       ]
for pct_col in pct_cols:
    third_quatile = acs_pct.loc[:,pct_col].quantile(.75)
    date_min = pd.Timestamp(
        acs_pct.loc[~acs_pct[pct_col].isna(),
                                  'Time'].dt.date.min())
    date_max = pd.Timestamp(
        acs_pct.loc[~acs_pct[pct_col].isna(),
                              'Time'].dt.date.max())

    acs_pct.loc[
        (acs_pct['Time']> date_min) & 
        (acs_pct['Time']< date_max), pct_col
        ] = acs_pct.loc[
            (acs_pct['Time']> date_min) & 
            (acs_pct['Time']< date_max), pct_col
            ].fillna(third_quatile)

    
    
acs_all = acs_raw.merge(acs_pct, how = 'left', 
                            on = ['Time','zip_code'], 
                            suffixes = (None,'_annual_pct_change'))
    
acs_all.to_csv('merged_acs_data.csv')
