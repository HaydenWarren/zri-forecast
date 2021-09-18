#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 11:23:59 2021

@author: haydenlw4
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler


def time_lag_merge(df_1, df_2,lag_dictionary = {},return_cols = False):
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
    if return_cols:
        return df_1_, list(set(df_1_.columns) - set(df_1.columns))
    else:
        return df_1_
    
def lasso_grid_cv(train_, y_val_, keep_cols_, cat_feats_,
                  starting_alphas_=[0.0001, 0.0003, 0.0006, 0.001, 
                                    0.003, 0.006, 0.01, 0.03, 0.06, 0.1,
                                    0.3, 0.6, 1],
                  n_jobs_ = None,
                  cv_ = 5
                 ):

    scaler = StandardScaler(with_mean=False)
    lasso = Lasso(max_iter = 100000, random_state = 33)

    X = train_[keep_cols_]
    transformer = ColumnTransformer([("Cat", 
                                      OneHotEncoder(handle_unknown = 'ignore'), 
                                      cat_feats_)], remainder='passthrough')
    X = transformer.fit_transform(X)
    X = scaler.fit_transform(X)
    y = train_[y_val_]

    # Grid Search set up.

    alphas = starting_alphas_
    tuned_parameters = [{'alpha': alphas}]
    print(f'Performing Grid Search with alphas of: {alphas}')
    clf1 = GridSearchCV(lasso, tuned_parameters, 
                        cv=cv_,n_jobs = n_jobs_)
    clf1.fit(X, y)

    # best alpha with first draft. Now iterate for more precision with alphas.
    best_alpha = clf1.best_params_['alpha']
    best_score = clf1.best_score_
    print(f'Current best alpha: {best_alpha}')
    print(f'Current best CV R2: {best_score}')
    best_score_last = 1
    best_score_diff = 1
    while best_score_diff > .001:
        best_score_last = best_score
        alphas_multiply = np.array([.3,.4,.5,.6,.7,.8,.9,1,
                            1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9])
        alphas = alphas_multiply*best_alpha
        tuned_parameters = [{'alpha': alphas}]
        print(f'Performing Grid Search with alphas of: {alphas}')
        clf2 = GridSearchCV(lasso, tuned_parameters, cv=5)
        clf2.fit(X, y)
        best_alpha = clf2.best_params_['alpha']
        best_score = clf2.best_score_
        
        print(f'Current best alpha: {best_alpha}')
        print(f'Current best CV R2: {best_score}')        
        best_score_diff = abs(best_score-best_score_last)
    print('Modeling complete :)')
    return clf2, transformer, scaler, clf1