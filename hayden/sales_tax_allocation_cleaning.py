#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:33:50 2021

@author: haydenlw4
"""

import pandas as pd
# load data and mapping city to zip codes.
tax_rev = pd.read_csv(
    'Sales_Tax_Allocation_City-County_Comparison_Summary.csv')
# zip_city_map = pd.read_csv('city_zip_init_map.csv',index_col=0)
tax = pd.read_csv('Active_Sales_Tax_Permit_Holders.csv',
                  parse_dates=['Outlet First Sales Date'])
zri = pd.read_csv('target.csv')


# find all zipcodes for the metros that we are going to forecast.
zips_of_interest = list(zri['zip_code'].unique())

# adding month and year. shrinking the dataframe to only after 2012.
# tax.loc[:,'year'] = tax.loc[:,'Outlet First Sales Date'].dt.year
# tax = tax[tax['year']>=2012].reset_index(drop=True)

# using the connection between taxpayer zipcode and taxpayer city 
# as a proxy for what city should be mapped to what zip codes. 
# the logic being that if most business being made in a given city
# for that zip code then that we should treat that city <-> zip code.
# it is a bad solution to a bad problem.

# mapping names that have entry errors or...
# mapping to Houston if that is the local gov for those cities.
taxpayer_city_corrections = {
    'ALLAN':'ALLEN',
    'CEDAR PARL': 'CEDAR PARK',
    'CROSSROADS':'CROSS ROADS',
    'CYPRESS':'HOUSTON',
    'DESOTO':'DE SOTO',
    'DWG':'DWG_BUTTS',
    'EDGECLIFF VLG':'EDGECLIFF VILLAGE',
    'FARMERS BRNCH':'FARMERS BRANCH',
    'FLOWERMOUND':'FLOWER MOUND',
    'FORT  WORTH':'FORT WORTH',
    'FOURNEY':'FORNEY',
    'FT WORTH':'FORT WORTH',
    'HOLLYWOOD PK':'HOLLYWOOD PARK',
    'IVIRING':'IRVING',
    'JERSEY VLG':'JERSEY VILLAGE',
    'KINGWOOD':'HOUSTON',
    'LAKEWOOD VLG':'LAKEWOOD VILLAGE',
    'MC KINNEY':'MCKINNEY',
    'N RICHLAND HILLS':'NORTH RICHLAND HILLS',
    'N RICHLND HLS':'NORTH RICHLAND HILLS',
    'OAK RIDGE N':'OAK RIDGE',
    'PROVIDNCE VLG':'PROVIDENCE VILLAGE',
    'RICHLAND HLS':'RICHLAND HILLS',
    'SPRING':'HOUSTON',
    'THE WOODLANDS':'HOUSTON',
    'UNIVERSAL CTY':'UNIVERSAL CITY',
    'W LAKE HILLS':'WEST LAKE HILLS',
    'WEST LAKE HLS':'WEST LAKE HILLS',
    'WHT SETTLEMT':'WHITE SETTLEMENT',
    'WOODLANDS':'HOUSTON'
    }
taxpayer = tax[tax['Taxpayer Zip Code'].isin(zips_of_interest)]
taxpayer.loc[:,'Taxpayer City'] = taxpayer.loc[:,'Taxpayer City'
            ].map(taxpayer_city_corrections).fillna(taxpayer['Taxpayer City'])

# seeing which zip codes are associated with what city the most.
zip_city_map = taxpayer.groupby(['Taxpayer Zip Code','Taxpayer City']
                                ).agg({'Taxpayer Number':'count'}
                                      ).reset_index()
zip_city_map.columns = ['zip_code','city','count']
# dropping city - zip code connections that aren't most frequent.
zip_city_map = zip_city_map.sort_values(['zip_code','count'],
                                        ascending = [True,False])
zip_city_map = zip_city_map.drop_duplicates(subset=['zip_code'],
                                            keep='first')

# match the upper case to allow for merging and having city be the same.
tax_rev.loc[:,'City'] = tax_rev.loc[:,'City'].str.upper()
zip_tax_rev_wide = zip_city_map.merge(tax_rev, how='left', left_on = 'city', 
                           right_on = 'City')
# getting df to look like i want it to with less columns and nice names.
zip_tax_rev = zip_tax_rev_wide[['zip_code','Report Year','Report Month',
                                'Current Rate','Net Payment This Period',
                                'Comparable Payment Prior Year',
                                'Percent Change From Prior Year','city']]
zip_tax_rev.columns = ['zip_code','year','month',
                       'sales_tax_rate','total_sales_tax',
                       'total_sales_tax_last_year',
                       'per_diff_total_sales_tax','city']


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
zip_tax_rev['day'] = 1
zip_tax_rev['Time'] = pd.to_datetime(zip_tax_rev[['year','month','day']])
zip_tax_rev = zip_tax_rev.drop(['month', 'year', 'day'], axis=1)
# use that dataframe to map to dataset to create a complete dataset
zip_tax_rev = date_zip_map.merge(zip_tax_rev, how = 'left', 
                                  on = ['Time','zip_code'])

zip_tax_rev = zip_tax_rev.dropna(thresh=3)


# dealing with the missing value for zipcode 76065 in march
trouble_row_1 = zip_tax_rev[
    zip_tax_rev['per_diff_total_sales_tax']==-100].index[0]
zip_tax_rev.loc[trouble_row_1, 'per_diff_total_sales_tax'] = 24.19
zip_tax_rev.loc[trouble_row_1, 'total_sales_tax'] = (
    zip_tax_rev.loc[trouble_row_1, 'total_sales_tax_last_year']*(1.2419)
    )

trouble_row_2 = zip_tax_rev[
    zip_tax_rev['per_diff_total_sales_tax'].isna()].index[0]
zip_tax_rev.loc[trouble_row_2, 'total_sales_tax_last_year'] = (
    zip_tax_rev.loc[trouble_row_1, 'total_sales_tax_last_year']*(1.2419)
    )
zip_tax_rev.loc[trouble_row_2, 'per_diff_total_sales_tax'] = (
    (zip_tax_rev.loc[trouble_row_2, 'total_sales_tax'] / 
    zip_tax_rev.loc[trouble_row_2, 'total_sales_tax_last_year']) - 1
    ) * 100

zip_tax_rev.to_csv('sales_tax_allocation.csv')