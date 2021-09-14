#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 20:58:03 2021

@author: haydenlw4
"""

## load packages and data sets
import pandas as pd

zri = pd.read_csv('zori.csv')
tax = pd.read_csv('Active_Sales_Tax_Permit_Holders.csv',
                  parse_dates=['Outlet First Sales Date'])

# find all zipcodes for the metros that we are going to forecast.
metros_of_interest = ['Dallas-Fort Worth, TX',  
                      'Houston, TX', 
                      'Austin, TX', 
                      'San Antonio, TX',
                      'El Paso, TX']
zri_of_interest = zri[zri['MsaName'].isin(metros_of_interest)]
zips_of_interest = list(zri_of_interest['RegionName'].unique())

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

# adding version that has only inside city limits to test if thats better
outlet_inside = outlet[outlet['Outlet Inside/Outside City Limits Indicator'
                              ]=='Y'].reset_index(drop=True)

# doing groupby.
outlet_group = outlet.groupby(['year','month','Outlet Zip Code']
                              ).agg({'Outlet City':'count',
                                     'taxpayer_non_tx':'sum',
                                     'org_type_cl':'sum',
                                     'org_type_is':'sum',
                                     'org_type_foreign':'sum',
                                     }).reset_index()
outlet_group.columns = ['year', 'month', 'zip_code',
                        'city', 'taxpayer_non_tx',
                        'org_type_cl', 'org_type_is',
                        'org_type_foreign']   
                                     
outlet_inside_group = outlet_inside.groupby(['year','month','Outlet Zip Code']
                              ).agg({'Outlet City':'count',
                                     'taxpayer_non_tx':'sum',
                                     'org_type_cl':'sum',
                                     'org_type_is':'sum',
                                     'org_type_foreign':'sum',
                                     }).reset_index()
outlet_inside_group.columns = ['year', 'month', 'zip_code',
                               'city', 'taxpayer_non_tx',
                               'org_type_cl', 'org_type_is', 
                               'org_type_foreign']                                 

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
                          'city', 'org_type_cl',
                          'org_type_is', 'org_type_foreign', 
                          'payer_outlet_same_zipcode']

# outplut the groups for analysis
outlet_group.to_csv('new_biz_outlet.csv')
outlet_inside_group.to_csv('new_biz_outlet_inside.csv')
taxpayer_group.to_csv('new_biz_taxpayer.csv')