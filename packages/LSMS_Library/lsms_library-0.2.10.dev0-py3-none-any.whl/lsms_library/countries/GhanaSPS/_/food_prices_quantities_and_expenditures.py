from lsms_library.local_tools import to_parquet
from lsms_library.local_tools import get_dataframe
#!/usr/bin/env python3

import pandas as pd
import numpy as np

df = get_dataframe('../var/food_acquired.parquet')
df.index = df.index.rename({'unit':'u'})
df = df.reset_index()
df['m'] = df['m'].fillna('')
df = df.set_index(['j','t','m','i', 'u'])
prices = ['price']
quantities =  ['purchased_quantity','produced_quantity','inkind_quantity']
expenditures = ['purchased_value', 'produced_value', 'inkind_value']

x = df[expenditures].replace(np.nan, 0).groupby(['j','t','m','i']).sum().replace(0,np.nan)
to_parquet(x, '../var/food_expenditures.parquet')


p = df[prices].groupby(['t','m','i','u']).median()
p = p.reset_index()
p['t'] = p['t'].astype(str)
p = p.set_index(['t','m','i','u'])
to_parquet(p.unstack('t'), '../var/food_prices.parquet')


#quantity to be updated once conversion_to_kg is created
"""q = df['quantity']
q = q.dropna()
pd.DataFrame({'Quantity':q}).to_parquet('../var/food_quantities.parquet')"""
