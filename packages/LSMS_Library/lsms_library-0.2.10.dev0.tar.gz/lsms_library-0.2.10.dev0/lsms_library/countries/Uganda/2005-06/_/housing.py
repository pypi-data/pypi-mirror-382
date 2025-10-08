from lsms_library.local_tools import to_parquet
#!/usr/bin/env python3
import numpy as np
import pandas as pd
import dvc.api
from lsms import from_dta

fn = '../Data/GSEC11.dta'
d = {"hhid":['HHID'],
    "Thatched roof" : ['h11q4a',lambda x:0 + ('thatch' in x.lower())],
     "Earthen floor" : ['h11q6a',lambda x:0 + ('earth' in x.lower())]}

with dvc.api.open(fn,mode='rb') as dta:
    df = from_dta(dta)

housing = df[[v[0] for v in d.values()]]
housing.columns.name = 'k'

housing = housing.rename(columns={v[0]:k for k,v in d.items()})

for k,v in d.items():
    try:
        housing[k] = housing[k].apply(v[1])
    except IndexError:
        pass
housing.set_index('hhid', inplace=True)
housing.index.name = 'j'

to_parquet(housing, 'housing.parquet')
