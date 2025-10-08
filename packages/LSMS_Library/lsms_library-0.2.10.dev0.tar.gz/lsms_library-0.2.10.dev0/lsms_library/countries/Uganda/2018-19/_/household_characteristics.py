#!/usr/bin/env python
from lsms_library.local_tools import to_parquet, age_sex_composition
import numpy as np

myvars = dict(fn='../Data/GSEC2.dta',
              HHID='hhid',
              sex='h2q3',
              age='h2q8',
              months_spent='h2q5')

df = age_sex_composition(**myvars)

df = df.filter(regex='ales ')

N = df.sum(axis=1)

df['log HSize'] = np.log(N[N>0])

# Switch to hhid that is constant across waves...
#with dvc.api.open('../Data/GSEC1.dta',mode='rb') as dta:
 #   id = pd.read_stata(dta,convert_categoricals=False)

to_parquet(df, 'household_characteristics.parquet')
