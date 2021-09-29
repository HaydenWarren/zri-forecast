#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 11:23:59 2021

@author: haydenlw4
"""

import pandas as pd
import numpy as np
import datetime
from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler


def time_lag_merge(df_1, df_2,lag_dictionary = {},return_full = False):
    '''
    Parameters
    ----------
    df_1 : pandas Dataframe
        left dataframe that has a 'zip_code' and 'Time' column.
    df_2 : pandas Dataframe
        right dataframe that has a 'zip_code' and 'Time' column.
    lag_dictionary : dictionary
        keys are number of months you want to lag. 
        values are lists of columns that you want to have that lag.

    Returns
    -------
    df_1_ : pandas Dataframe
        dataframe to have new lagged columns.
    '''
    if lag_dictionary:
        df_1_ = df_1.copy()
        for lag in lag_dictionary.keys():
            df_2_ = df_2.copy()
            df_2_.loc[:,'Time'] = df_2_.loc[:,'Time'] + pd.DateOffset(months=lag)
            if return_full:
                df_1_ = df_1_.merge(
                    df_2_[lag_dictionary[lag]+['zip_code','Time']
                          ].add_suffix(f'_{lag}_month_shift').rename(
                      columns={f'Time_{lag}_month_shift':'Time',
                               f'zip_code_{lag}_month_shift':'zip_code'}), 
                    how = 'outer', 
                    on = ['zip_code','Time'])
            else: 
                df_1_ = df_1_.merge(
                    df_2_[lag_dictionary[lag]+['zip_code','Time']
                          ].add_suffix(f'_{lag}_month_shift').rename(
                      columns={f'Time_{lag}_month_shift':'Time',
                               f'zip_code_{lag}_month_shift':'zip_code'}), 
                    how = 'left', 
                    on = ['zip_code','Time'])
    else:
        df_1_ = df_1.merge(df_2, how = 'left', on = ['zip_code','Time'],
                          suffixes = (None,'_right'))
    return df_1_

    

def lasso_gridCV_fit(X, y, 
                     max_iter = 50000, random_state = 33,
                     alphas = [0.1,0.2,0.3, 0.6, 1], 
                     cv = 5, 
                     scoring = 'neg_root_mean_squared_error'):
    '''
    Fits model to given features X and target y. 
    Returns lasso model trained with grid search 
    cross validation. 
    
    Parameters
    ----------
    X : pandas Dataframe
        Model features..
    y : pandas series
        Target variable.
    max_iter : integer, optional
        Number of max iterations done in lasso. The default is 50000.
    random_state : integer, optional
        Random state for model.. The default is 33.
    alphas : list of floats, optional
        List of alphas to do a grid search on.. 
        The default is [0.1,0.2,0.3, 0.6, 1].
    cv : integer, optional
        Number of cross validations. 
        The default is 5.
    scoring : string, optional
        sklearn scoring input. 
        The default is 'neg_root_mean_squared_error'.

    Returns
    -------
    clf : TYPE
        DESCRIPTION.

    '''
    lasso = Lasso(max_iter = max_iter, random_state = random_state)
    tuned_parameters = [{'alpha': alphas}]
    print(f'Performing Grid Search with alphas of: {alphas}')
    clf = GridSearchCV(lasso, tuned_parameters, 
                        cv = cv,n_jobs = -1, verbose=3,
                      scoring = scoring)
    clf.fit(X, y)
    print(f"Best alpha {clf.best_params_['alpha']}")
    return clf

def zri_data_pipeline(zri, texas_data, acs_data):
    '''
    Process Zori, ACS, and texas specific data together
    with the proper shifts necessary to have a 12 month forecast.

    Parameters
    ----------
    zri : pandas Dataframe
        Target variable dataframe.
    texas_data : pandas Dataframe
        Feature variables dataframe without any census data.
    acs_data : pandas Dataframe
        Feature variables dataframe with only census data.

    Returns
    -------
    merged_df : pandas Dataframe
        All target and feature variables with proper shift to produce
        a forecast of zri 12 months in the future.

    '''
    # adding shift to zri
    zri_shift = time_lag_merge(
        zri, zri, 
        {
            12:['zori_ssa'],
            13:['zori_ssa'],
            18:['zori_ssa'],
            24:['zori_ssa']
            },
        return_full = True
        )
    
    # there should now be extra values after our target. 
    # We are gonna remove the missing values that happen 
    # at the start of our inputs tho
    zri_shift = zri_shift.sort_values('Time')
    zri_shift = zri_shift.dropna(subset = ['zori_ssa_24_month_shift'],
                                 axis='index',
                                 how = 'any').reset_index(drop = True)
    # Adding the shift values
    zri_shift.loc[:,'zori_ssa_1_diff_lag_12'] = (
        zri_shift.loc[:,'zori_ssa_12_month_shift'] -
        zri_shift.loc[:,'zori_ssa_13_month_shift'])
    zri_shift.loc[:,'zori_ssa_6_diff_lag_12'] = (
        zri_shift.loc[:,'zori_ssa_12_month_shift'] -
        zri_shift.loc[:,'zori_ssa_18_month_shift'])
    zri_shift.loc[:,'zori_ssa_12_diff_lag_12'] = (
        zri_shift.loc[:,'zori_ssa_12_month_shift'] -
        zri_shift.loc[:,'zori_ssa_24_month_shift'])
    zri_shift['zori_ssa_12_diff_lag_12_per'] = (
        zri_shift['zori_ssa_12_diff_lag_12']/
        zri_shift['zori_ssa_12_month_shift'])
    
    zri_shift = zri_shift[['Time','zip_code','zori_ssa',
                           'zori_ssa_12_month_shift',
                           'zori_ssa_1_diff_lag_12', 
                           'zori_ssa_6_diff_lag_12',
                           'zori_ssa_12_diff_lag_12_per']]
    
    
    # merge non acs data 
    extra_shift = ['Gross Value Natural Gas Production', 
                   'sap_case_shiller_index']
    merged_df = time_lag_merge(
        zri_shift, 
        texas_data, 
        {
            12:list(texas_data.drop(columns = ['Time',
                                               'zip_code']+extra_shift
                                    ).columns),
            13:extra_shift
            },
        return_full = True
        )
    # merge acs data
    acs_1_cols = [
        'black_pop',
        'white_pop',
        'hispanic_pop',
        'high_school_diploma',
        'female_female_households',
        'armed_forces',
        'children',
        'black_pop_annual_pct_change',
        'white_pop_annual_pct_change',
        'hispanic_pop_annual_pct_change',
        'high_school_diploma_annual_pct_change',
        'children_annual_pct_change',
        ]
    merged_df = time_lag_merge(
        merged_df, 
        acs_data, 
        {
            36:list(acs_data.drop(columns = ['Time',
                                             'zip_code'] + acs_1_cols
                                  ).columns),
            48:acs_1_cols
            },
        return_full = True
        )
    # removing missing values from the features
    merged_df = merged_df.loc[merged_df['Time']>datetime.datetime(2016,6,2),:
                              ].reset_index(drop=True)
    merged_df = merged_df.loc[merged_df['Time']<datetime.datetime(2022,7,2),:
                              ].reset_index(drop=True)
    merged_df = merged_df.sort_values('Time')
    merged_df = merged_df.dropna(subset = ['single_women_36_month_shift'],
                                 axis = 'index',
                                 how = 'any').reset_index(drop = True)
    # Adding net approve feature 
    merged_df['tx_net_approve_12_month_shift'] = (
        merged_df['tx_is_better_12_month_shift'] - 
        merged_df['tx_is_worse_12_month_shift'])
    return merged_df

def train_test_forecast_split(df, 
                              train_date = datetime.datetime(2020,7,2), 
                              forecast_date = datetime.datetime(2021,7,2)):
    
    # split train and test based on a year in advance.
    train = df.loc[df['Time']<train_date,:].reset_index(drop=True)
    post_train = df.loc[df['Time']>train_date,:].reset_index(drop=True)
    # test will have all zips. 
    test = post_train.loc[post_train['Time']<forecast_date,
                          :].reset_index(drop=True)
    forecast = post_train.loc[post_train['Time']>forecast_date,
                              :].reset_index(drop=True)
    
    return train, test, forecast