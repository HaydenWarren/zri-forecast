#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 19:38:26 2021

@author: haydenlw4
"""

import pandas as pd

booze = pd.read_csv('Mixed_Beverage_Taxes_City_and_County.csv')

# oh no they quarterly -> monthly reporting period in 2021.
# look at booze['Report Period'] and booze['Report Period Type'] to see it.