#!/usr/bin/env python
from lsms_library.local_tools import to_parquet
from lsms_library.local_tools import get_dataframe
"""Calculate food prices for different items across rounds; allow
different prices for different units.  
"""
import pandas as pd
import numpy as np
import json

v = get_dataframe('../var/food_acquired.parquet')

# Drop expenditures
prices = ['market', 'farmgate', 'unitvalue_home', 'unitvalue_away', 'unitvalue_own',
          'unitvalue_inkind', 'market_home', 'market_away', 'market_own']

quantities =  ['quantity_home', 'quantity_away', 'quantity_own', 'quantity_inkind' ]

expenditures = ['value_home', 'value_away', 'value_own', 'value_inkind']

x = v.groupby(['j','t','m','i'])[expenditures].sum()
x = x.sum(axis=1).replace(0,np.nan).dropna()

to_parquet(pd.DataFrame({'x':x}), '../var/food_expenditures.parquet')

v = v[prices + quantities]

with open('kgs_per_other_units.json','r') as f:
    d = json.load(f)

kgs = pd.Series(d)
kgs.index.name = 'u'
kgs.name = 'Kgs/unit'

kgs = kgs.reindex(v.index,level='u')
kgs = kgs[kgs!=0]

# Convert other units to kilograms, where possible
p = v[prices]
p = p.divide(kgs,axis=0)

q = v[quantities]
q = q.multiply(kgs,axis=0)

# What units were converted?
tokg = {k:'Kg' for k,v in d.items() if np.isreal(v)}

p = p.rename(index=tokg,level='u')
q = q.rename(index=tokg,level='u')

p = p.replace(0,np.nan)
to_parquet(p, '../var/food_prices.parquet')

q = q.replace(0,np.nan)
to_parquet(q, '../var/food_quantities.parquet')
