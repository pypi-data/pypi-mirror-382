from lsms_library.local_tools import get_dataframe
"""Calculate food prices for different items across rounds; allow
different prices for different units.  
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('../../_/')
from lsms_library.local_tools import to_parquet

fa = []
for t in ['2018-19']:
    df = get_dataframe('../'+t+'/_/food_acquired.parquet').squeeze()
    df = df.groupby(['j','t','i','units']).agg({'quantity': 'sum',
                                                'last expenditure': 'sum',
                                                'last purchase quantity':'sum',
                                                'last purchase units':'first'})
    df['price'] = df['last expenditure']/df['last purchase quantity']
    df = df.reset_index().set_index(['j','t','i','units'])
    #df = id_walk(df,t,Waves)
    fa.append(df)

fa = pd.concat(fa)

of = get_dataframe('../var/other_features.parquet')

fa = fa.join(of.reset_index('m'), on=['j','t'])
fa = fa.reset_index().set_index(['j','t','m','i','units'])

fa = fa.replace(0,np.nan)
to_parquet(fa, '../var/food_acquired.parquet')
