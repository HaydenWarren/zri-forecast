#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 20:58:03 2021

@author: haydenlw4
"""

## load packages and data sets
import pandas as pd

zri = pd.read_csv('target.csv',index_col = 0)
tax = pd.read_csv('Active_Sales_Tax_Permit_Holders.csv',
                  parse_dates=['Outlet First Sales Date'])

# find all zipcodes for the metros that we are going to forecast.
zips_of_interest = list(zri['zip_code'].unique())

# exporting the zip codes of interest for what we need in other places.
# zips_of_interest_df = pd.DataFrame({'zip_codes':zips_of_interest})
# zips_of_interest_df.to_csv('tx_zip_codes.csv')

# adding month and year. shrinking the dataframe to only after 2012.
tax.loc[:,'year'] = tax.loc[:,'Outlet First Sales Date'].dt.year
tax = tax[tax['year']>=2012].reset_index(drop=True)
tax.loc[:,'month'] = tax.loc[:,'Outlet First Sales Date'].dt.month

# limit tax dataset to when new sales tax permits are issued to taxpayer
# outlet in the zip codes of interest
outlet = tax[tax['Outlet Zip Code'].isin(zips_of_interest)]

# if the taxpayer setting up the business is from out of texas
outlet.loc[:,'taxpayer_non_tx'] = 1
outlet.loc[outlet['Taxpayer State']=='TX','taxpayer_non_tx'] = 0
# CL code is TEXAS LIMITED LIABILITY COMPANY. or LLC
outlet.loc[:,'org_type_cl'] = 0
outlet.loc[outlet['Taxpayer Organization Type']=='CL',
           'org_type_cl'] = 1
# IS code is INDIVIDUAL - SOLE OWNER. or small business
outlet.loc[:,'org_type_is'] = 0
outlet.loc[outlet['Taxpayer Organization Type']=='IS',
           'org_type_is'] = 1
# theses are any corporations that are foriegn.
foreign_codes = ['CI', 'CF', 'PF', 'CM', 'CU', 'TI', 
                 'CS', 'PW', 'AF', 'TF', 'AC']
outlet.loc[:,'org_type_foreign'] = 0
outlet.loc[outlet['Taxpayer Organization Type'].isin(foreign_codes),
           'org_type_foreign'] = 1

# doing groupby.
outlet_group = outlet.groupby(['year','month','Outlet Zip Code']
                              ).agg({'Outlet City':'count',
                                     'taxpayer_non_tx':'sum',
                                     'org_type_cl':'sum',
                                     'org_type_is':'sum',
                                     'org_type_foreign':'sum',
                                     }).reset_index()
outlet_group.columns = ['year', 'month', 'zip_code',
                        'outlet_count', 'outlet_taxpayer_non_tx',
                        'outlet_org_type_cl', 'outlet_org_type_is',
                        'outlet_org_type_foreign']   

# add ratios which will be better for analysis
outlet_group.loc[:,'outlet_non_tx_ratio'] = (
    outlet_group.loc[:,'outlet_taxpayer_non_tx'] / 
    outlet_group.loc[:,'outlet_count'])

outlet_group.loc[:,'outlet_cl_ratio'] = (
    outlet_group.loc[:,'outlet_org_type_cl'] / 
    outlet_group.loc[:,'outlet_count'])

outlet_group.loc[:,'outlet_is_ratio'] = (
    outlet_group.loc[:,'outlet_org_type_is'] / 
    outlet_group.loc[:,'outlet_count'])

outlet_group.loc[:,'outlet_foreign_ratio'] = (
    outlet_group.loc[:,'outlet_org_type_foreign'] / 
    outlet_group.loc[:,'outlet_count'])


# Create list of dates from 01-01-2012 to last complete data
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
outlet_group['day'] = 1
outlet_group['Time'] = pd.to_datetime(outlet_group[['year','month','day']])
outlet_group = outlet_group.drop(['month', 'year', 'day'], axis=1)
# use that dataframe to map to dataset to create a complete dataset
outlet_group = date_zip_map.merge(outlet_group, how = 'left', 
                                  on = ['Time','zip_code'])
# all missing values with 0
outlet_group = outlet_group.fillna(0)
## credit to julie for this code block

# limit tax dataset to when new sales tax permits are issued to taxpayer                 
taxpayer = tax[tax['Taxpayer Zip Code'].isin(zips_of_interest)]


# CL code is TEXAS LIMITED LIABILITY COMPANY. or LLC
taxpayer.loc[:,'org_type_cl'] = 0
taxpayer.loc[taxpayer['Taxpayer Organization Type']=='CL',
           'org_type_cl'] = 1
# IS code is INDIVIDUAL - SOLE OWNER. or small business
taxpayer.loc[:,'org_type_is'] = 0
taxpayer.loc[taxpayer['Taxpayer Organization Type']=='IS',
           'org_type_is'] = 1
# theses are any corporations that are foriegn.
foreign_codes = ['CI', 'CF', 'PF', 'CM', 'CU', 'TI', 
                 'CS', 'PW', 'AF', 'TF', 'AC']
taxpayer.loc[:,'org_type_foreign'] = 0
taxpayer.loc[taxpayer['Taxpayer Organization Type'].isin(foreign_codes),
           'org_type_foreign'] = 1
# stay inside zipcode
taxpayer.loc[:,'payer_outlet_same_zipcode'] = 0
taxpayer.loc[taxpayer['Taxpayer Zip Code']==taxpayer['Outlet Zip Code'],
             'payer_outlet_same_zipcode'] = 1

taxpayer_group = taxpayer.groupby(['year','month','Taxpayer Zip Code']
                              ).agg({'Taxpayer City':'count',
                                     'org_type_cl':'sum',
                                     'org_type_is':'sum',
                                     'org_type_foreign':'sum',
                                     'payer_outlet_same_zipcode':'sum',
                                     }).reset_index()
taxpayer_group.columns = ['year', 'month', 'zip_code', 
                          'taxpayer_count', 'taxpayer_org_type_cl',
                          'taxpayer_org_type_is', 'taxpayer_org_type_foreign', 
                          'payer_outlet_same_zipcode']

# add ratios which will be better for analysis
taxpayer_group.loc[:,'taxpayer_same_zip_ratio'] = (
    taxpayer_group.loc[:,'payer_outlet_same_zipcode'] / 
    taxpayer_group.loc[:,'taxpayer_count'])

taxpayer_group.loc[:,'taxpayer_cl_ratio'] = (
    taxpayer_group.loc[:,'taxpayer_org_type_cl'] / 
    taxpayer_group.loc[:,'taxpayer_count'])

taxpayer_group.loc[:,'taxpayer_is_ratio'] = (
    taxpayer_group.loc[:,'taxpayer_org_type_is'] / 
    taxpayer_group.loc[:,'taxpayer_count'])

taxpayer_group.loc[:,'taxpayer_foreign_ratio'] = (
    taxpayer_group.loc[:,'taxpayer_org_type_foreign'] / 
    taxpayer_group.loc[:,'taxpayer_count'])


# Create list of dates from 01-01-2012 to last complete data
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
taxpayer_group['day'] = 1
taxpayer_group['Time'] = pd.to_datetime(taxpayer_group[['year','month','day']])
taxpayer_group = taxpayer_group.drop(['month', 'year', 'day'], axis=1)
# use that dataframe to map to dataset to create a complete dataset
taxpayer_group = date_zip_map.merge(taxpayer_group, how = 'left', 
                                  on = ['Time','zip_code'])
# all missing values with 0
taxpayer_group = taxpayer_group.fillna(0)
## credit to julie for this code block

# outplut the groups for analysis
outlet_group.to_csv('new_biz_outlet.csv')
taxpayer_group.to_csv('new_biz_taxpayer.csv')