#!/usr/bin/env python
from lsms_library.local_tools import to_parquet
import sys
sys.path.append('../../_')
import numpy as np
import dvc.api
import pandas as pd
sys.path.append('../../../_/')
from lsms_library.local_tools import df_from_orgfile

t = '2009-10'

myvars = dict(fn='../Data/S11A.dta',item='itname',HHID='hhno')

with dvc.api.open(myvars['fn'],mode='rb') as dta:
    df = pd.read_stata(dta, convert_categoricals=True)

# Values recorded as cedis & pesewas; add 'em up
df['purchased_value'] = df['s11a_cii'] + df['s11a_ciii']/100
df['produced_value'] = df['s11a_bii'] + df['s11a_biii']/100
df['inkind_value'] = df['s11a_dii'] + df['s11a_diii']/100

x = df[['hhno','itname',
        's11a_ci', 'purchased_value',
        's11a_bi', 'produced_value',
        's11a_di', 'inkind_value',
        's11a_f']]

col = {'hhno': 'j', 
       'itname': 'i', 
       's11a_ci': 'purchased_quantity', 
       's11a_bi': 'produced_quantity',
       's11a_di': 'inkind_quantity',
       's11a_f': 'unit'}

x = x.rename(col, axis = 1)
x['price'] = x['purchased_value']/x['purchased_quantity']
x['t'] = t
x['j'] = x['j'].astype(str)
x = x.set_index(['j','t','i'])
null_cells = x['unit'].isnull()
x['unit'] = x['unit'].astype('Int64').astype(str).mask(null_cells, np.NaN)
x = x.dropna(how='all')

units = df_from_orgfile('../../_/units.org',name='unit09',encoding='ISO-8859-1')
units['Code'] = units['Code'].astype('str')
unitsd = units.set_index('Code').squeeze().to_dict()

x = x.replace({'unit':unitsd})
to_parquet(x, 'food_acquired.parquet')


