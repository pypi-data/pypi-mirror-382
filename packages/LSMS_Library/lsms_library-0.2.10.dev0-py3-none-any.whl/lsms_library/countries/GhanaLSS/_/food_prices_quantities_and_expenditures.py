from lsms_library.local_tools import to_parquet
from lsms_library.local_tools import get_dataframe
#!/usr/bin/env python3

import pandas as pd
import numpy as np

df = get_dataframe('../var/food_acquired.parquet')
#df = df.reset_index()
#df['m'] = df['m'].fillna('')
#df = df.set_index(['j','t','m','i', 'u'])
df['produced_value'] = df['produced_quantity'] * df['produced_price']
 
prices = ['purchased_price', 'produced_price']
quantities =  ['purchased_quantity','produced_quantity']
expenditures = ['purchased_value'] #, 'produced_value']
                #'purchased_value_yearly',
                #'produced_value_daily', 'produced_value_yearly'
                #]

x = df[expenditures].replace(np.nan, 0).groupby(['j','t','m','i']).sum().replace(0,np.nan)
to_parquet(x, '../var/food_expenditures.parquet')


p = df[prices].groupby(['t','m','i','u']).mean()
to_parquet(p.unstack('t'), '../var/food_prices.parquet')


#quantity to be updated once conversion_to_kg is created
"""q = df['quantity']
q = q.dropna()
pd.DataFrame({'Quantity':q}).to_parquet('../var/food_quantities.parquet')"""
