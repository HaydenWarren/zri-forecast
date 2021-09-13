#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 20:58:03 2021

@author: haydenlw4
"""

import pandas as pd

zri = pd.read_csv('zori.csv')

tax = pd.read_csv('Active_Sales_Tax_Permit_Holders.csv')

cities = ['Dallas-Fort Worth, TX', 
          'Houston, TX', 
          'Austin, TX', 
          'San Antonio, TX']

zri_tx = zri[zri['MsaName'].isin(cities)]

tx_zips = list(zri_tx['RegionName'].unique())

len(tax[tax['Taxpayer Zip Code'].isin(tx_zips)])

len(tax[tax['Outlet Zip Code'].isin(tx_zips)])


len(tax[(tax['Outlet Zip Code'].isin(tx_zips)) |
    (tax['Taxpayer Zip Code'].isin(tx_zips))])

outlet_zip = tax[tax['Outlet Zip Code'].isin(tx_zips)]
unique_cities = list(outlet_zip['Outlet City'].unique())