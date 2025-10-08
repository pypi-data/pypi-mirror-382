#!/usr/bin/env python
from lsms_library.local_tools import to_parquet

import sys
sys.path.append('../../_/')
import pandas as pd
import pyreadstat
import numpy as np
import json
import dvc.api
from lsms import from_dta
from lsms.tools import get_household_roster
from panama import age_sex_composition

fs = dvc.api.DVCFileSystem('../../')
fs.get_file('/Panama/2003/Data/E03PE03.DTA', '/tmp/E03PE03.DTA')
df, meta = pyreadstat.read_dta('/tmp/E03PE03.DTA')

fs.get_file('/Panama/2003/Data/E03BASE.DTA', '/tmp/E03BASE.DTA')
regional_info, meta_r  = pyreadstat.read_dta('/tmp/E03BASE.DTA', apply_value_formats = True, formats_as_category = True)

regions = regional_info.groupby('form').agg({'prov' : 'first'})
regions.index = regions.index.map(str)

out  = age_sex_composition(df, sex='p003', sex_converter=lambda x: ['m', 'f'][x==2],
                           age='p004', age_converter=None, hhid='form')

out.index = out.index.map(str)

final = out.join(regions)
final = final.rename(columns = {'prov' : 'm'})
final['t'] = '2003'
final = final.set_index(['t', 'm'], append = True)
final.columns.name = 'k'

to_parquet(final, 'household_characteristics.parquet')
