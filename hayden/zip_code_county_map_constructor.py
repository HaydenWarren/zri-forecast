#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 11:58:35 2021

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
zips_of_interest = list(zri['RegionName'].unique())

# adding month and year. shrinking the dataframe to only after 2012.
tax.loc[:,'year'] = tax.loc[:,'Outlet First Sales Date'].dt.year
tax = tax[tax['year']>=2012].reset_index(drop=True)

taxpayer = tax[tax['Taxpayer Zip Code'].isin(zips_of_interest)]


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

# match the upper case to allow for merging and having city be the same.
tax_rev.loc[:,'City'] = tax_rev.loc[:,'City'].str.upper()
zip_tax_rev_wide = zip_city_map.merge(tax_rev, how='left', left_on = 'city', 
                           right_on = 'City')

zip_tax_rev_wide = zip_tax_rev_wide.drop_duplicates(
    subset=['zip_code','city','count'],keep='first')

zip_county_map = zip_tax_rev_wide.groupby(['zip_code','County']).agg(
    {'count':'sum'}).reset_index()

# dropping city - zip code connections that aren't most frequent.
zip_county_map = zip_county_map.sort_values(['zip_code','count'],
                                        ascending = [True,False])
zip_county_map = zip_county_map.drop_duplicates(subset=['zip_code'],
                                            keep='first')

zip_county_map = zip_county_map[['zip_code','County']]
zip_county_map.columns = ['zip_code','county']

zip_county_map.to_csv('zip_county_map.csv')