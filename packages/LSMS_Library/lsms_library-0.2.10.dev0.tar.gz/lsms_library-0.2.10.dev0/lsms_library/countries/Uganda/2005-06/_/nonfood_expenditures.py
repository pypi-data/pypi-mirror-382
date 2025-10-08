#!/usr/bin/env python
from lsms_library.local_tools import to_parquet
import sys
sys.path.append('../../_')
from uganda import nonfood_expenditures

myvars = dict(fn='../Data/GSEC14B.dta',
              item='h14bq2',
              HHID='HHID',
              purchased='h14bq5',
              away=None,
              produced='h14bq7',
              given='h14bq9')

x = nonfood_expenditures(**myvars) 
to_parquet(x, 'nonfood_expenditures.parquet')
