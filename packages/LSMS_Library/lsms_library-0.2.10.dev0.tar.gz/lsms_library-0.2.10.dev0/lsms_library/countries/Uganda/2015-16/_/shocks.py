#!/usr/bin/env python
from lsms_library.local_tools import to_parquet

from calendar import month
import sys
sys.path.append('../../_/')
import pandas as pd
import dvc.api
from datetime import datetime
from lsms import from_dta

#shock dataset
with dvc.api.open('../Data/GSEC16.dta',mode='rb') as dta: 
    df = from_dta(dta)
df = df[df['h16q2y'].notna()] #filter for valid entry 

#general hh dataset 
with dvc.api.open('../Data/gsec1.dta',mode='rb') as dta: 
    date = from_dta(dta)

#filter for hhs who have taken the shock questionnaire 
date = date[date.set_index('hh').index.isin(df.set_index('HHID').index)] 


#calculate shock onset 
df['h16q02a'] = pd.to_datetime(df.h16q02a, format='%B').dt.month

df['start_date'] = pd.to_datetime(df.rename(columns={'h16q2y': 'year', 'h16q02a': 'month'})[['year', 'month']].assign(DAY=1)) #no day reported; assume 1st of the month 
date['end_date'] = pd.to_datetime(date[['year', 'month']].assign(DAY=1)) #round the interview date to 1st of the month to match shock date
date = date[["hh", "end_date","HHID"]].rename(columns={'hh': 'HHID', 'HHID': 'master_hhid'})
df = pd.merge(df, date, on='HHID')
df['Onset'] = (df.end_date.dt.to_period('M') - df.start_date.dt.to_period('M')).apply(lambda x: x.n)

shocks = pd.DataFrame({"j": df.master_hhid.values.tolist(),
                    "Shock":df.h16q00.values.tolist(), 
                    "Year": df.h16q2y.values.tolist(),
                    "Onset":df.Onset.values.tolist(), 
                    "Duration":df.h16q02b.values.tolist(),
                    "EffectedIncome":df.h16q3a.values.tolist(), 
                    "EffectedAssets":df.h16q3b.values.tolist(), 
                    "EffectedProduction":df.h16q3c.values.tolist(), 
                    "EffectedConsumption":df.h16q3d.values.tolist(), 
                    "HowCoped0":df.h16q4a.values.tolist(),
                    "HowCoped1":df.h16q4b.values.tolist(),
                    "HowCoped2":df.h16q4c.values.tolist()})

#converting data types 
for col in ["EffectedIncome",  "EffectedAssets",  "EffectedProduction", "EffectedConsumption"]:
    shocks[col] = shocks[col].map({"Yes": True,"No": False})
    shocks[col] = shocks[col].astype('boolean')
shocks = shocks.astype({'Shock': 'category',
                        'Year': 'Int64',
                        'Onset': 'Int64',
                        'Duration': 'float',
                        "HowCoped0": 'category',
                        "HowCoped1": 'category',
                        "HowCoped2": 'category'
                        }) 

shocks.insert(1, 't', '2015-16')
shocks.set_index(['j','t','Shock'], inplace = True)

to_parquet(shocks, 'shocks.parquet')
