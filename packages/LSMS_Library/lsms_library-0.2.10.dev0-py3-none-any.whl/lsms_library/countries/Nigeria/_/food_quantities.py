import pandas as pd
import json
import numpy as np
from lsms_library.local_tools import to_parquet
from lsms_library.local_tools import get_dataframe

C = []
for t in ['2010-11','2012-13','2015-16','2018-19']:
    C.append(get_dataframe('../%s/_/food_quantities.parquet' % t))

c = pd.concat(C,axis=0)

# Eliminate infinities
c = c.replace(np.inf,np.nan)

with open('aggregate_items.json') as f:
    lbl = json.load(f)

c = c.rename(columns=lbl['Aggregated Label'])

c.columns.name = 'i'
c = c.groupby('i',axis=1).sum()

to_parquet(c, '../var/food_quantities.parquet')
