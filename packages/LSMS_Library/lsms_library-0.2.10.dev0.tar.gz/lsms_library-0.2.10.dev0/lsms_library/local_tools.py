from lsms.tools import get_food_prices, get_food_expenditures, get_household_roster, get_household_identification_particulars
from lsms import from_dta
import numpy as np
import pandas as pd
import dvc.api
from collections import defaultdict
from cfe.df_utils import use_indices
import warnings
import json
import difflib
import types
from pyarrow.lib import ArrowInvalid
from functools import lru_cache
from pathlib import Path
from cfe.df_utils import df_to_orgtbl
from importlib.resources import files
from dvc.api import DVCFileSystem
import pyreadstat
import inspect

# Initialize DVC filesystem once and reuse it
DVCFS = DVCFileSystem(files('lsms_library')/'countries')

def _to_numeric(x,coerce=False):
    try:
        if coerce:
            return pd.to_numeric(x,errors='coerce')
        else:
            return pd.to_numeric(x)
    except (ValueError,TypeError):
        return x
    
@lru_cache(maxsize=3)
def get_dataframe(fn,convert_categoricals=True,encoding=None,categories_only=False):
    """From a file named fn, try to return a dataframe.

    Hope is that caller can be agnostic about file type,
    or if file is local or on a dvc remote.
    """

    def local_file(fn):
    # Is the file local?
        try:
            with open(fn) as f:
                pass
            return True
        except FileNotFoundError:
            return False
    
    def file_system_path(fn):
    # is the file a relative path or it's the full path from our fs (DVCFileSystem)?
        try:
            with DVCFS.open(fn) as f:
                pass
            return True
        except FileNotFoundError:
            return False

    def read_file(f,convert_categoricals=convert_categoricals,encoding=encoding):
        if isinstance(f,str):
            try:
                return pd.read_spss(f,convert_categoricals=convert_categoricals)
            except (pd.errors.ParserError, UnicodeDecodeError):
                pass

        try:
            return pd.read_parquet(f, engine='pyarrow')
        except (ArrowInvalid,):
            pass

        try:
            f.seek(0)
            return from_dta(f,convert_categoricals=convert_categoricals,encoding=encoding,categories_only=categories_only)
        except ValueError:
            pass

        try:
            f.seek(0)
            return pd.read_csv(f,encoding=encoding)
        except (pd.errors.ParserError, UnicodeDecodeError):
            pass

        try:
            f.seek(0)
            return pd.read_excel(f)
        except (pd.errors.ParserError, UnicodeDecodeError, ValueError):
            pass

        try:
            f.seek(0)
            return pd.read_feather(f)
        except (pd.errors.ParserError, UnicodeDecodeError,ArrowInvalid) as e:
            pass

        try:
            f.seek(0)
            return pd.read_fwf(f)
        except (pd.errors.ParserError, UnicodeDecodeError):
            pass


        raise ValueError(f"Unknown file type for {fn}.")

    if local_file(fn):
        try:
            with open(fn,mode='rb') as f:
                df = read_file(f,convert_categoricals=convert_categoricals,encoding=encoding)
        except (TypeError,ValueError): # Needs filename?
            df = read_file(fn,convert_categoricals=convert_categoricals,encoding=encoding)
    elif file_system_path(fn):
        try:
            with DVCFS.open(fn,mode='rb') as f:
                df = read_file(f,convert_categoricals=convert_categoricals,encoding=encoding)
        except TypeError: # Needs filename?
            df = read_file(fn,convert_categoricals=convert_categoricals,encoding=encoding)

    else:
        with dvc.api.open(fn,mode='rb') as f:
            df = read_file(f,convert_categoricals=convert_categoricals,encoding=encoding)

    return df

#def regularize_string(s):

def df_data_grabber(fn,idxvars,convert_categoricals=True,encoding=None,orgtbl=None,**kwargs):
    """From a file named fn, grab both index variables and additional variables
    specified in kwargs and construct a pandas dataframe.

    A special case: if fn is an orgfile, grab orgtbl.

    For both idxvars and kwargs, expect one of the three following formats:

     - Simple: {newvarname:existingvarname}, where "newvarname" is the name of
      the variable we want in the final dataframe, and "existingvarname" is the
      name of the variable as it's found in fn; or

     - Tricky: {newvarname:(existingvarname,transformation)}, where varnames are
       as in "Simple", but where "transformation" is a function mapping the
       existing data into the form desired for newvarname; or

     - Trickier: {newvarname:(listofexistingvarnames,transformation)}, where newvarname is
       as in "Simple", but where "transformation" is a function mapping the variables in
       listofexistingvarnames into the form desired for newvarname.

    Options convert_categoricals and encoding are passed to get_dataframe, and
    are documented there.

    Ethan Ligon                                                      March 2024

    """

    def grabber(df,v):
        if isinstance(v,str): # Simple
            if v in df.columns:
                return df[v]
            else:
                raise KeyError(f"{v} not in columns of dataframe.")
        else:
            s,f = v
            if isinstance(f,types.FunctionType):  # Tricky & Trickier
                if isinstance(s,str):
                    return df[s].apply(f)
                else:
                    return df[s].apply(f,axis=1)
            elif isinstance(f,dict):
                    if isinstance(s, list) and len(s) > 1:
                        # s refers to multiple columns, we should apply row-wise
                        return df[s].apply(lambda row: f.get(tuple(row), row), axis=1)
                    else:
                        # s is a single column name (string) or single-element list
                        col = s if isinstance(s, str) else s[0]
                        return df[col].map(lambda x: f.get(x, x))
            elif isinstance(f, tuple):
                for i in f:
                    return grabber(df, (s, i))

        raise ValueError(df_data_grabber.__doc__)

    if orgtbl is None:
        df = get_dataframe(fn,convert_categoricals=convert_categoricals,encoding=encoding)
    else:
        df = df_from_orgfile(fn,name=orgtbl,encoding=encoding)
        if df.shape[0]==0:
            raise KeyError(f'No table {orgtbl} in {fn}.')

    out = {}

    if isinstance(idxvars,str):
        idxvars={idxvars:idxvars}

    for k,v in idxvars.items():
        out[k] = grabber(df,v)

    out = pd.DataFrame(out)

    if len(kwargs):
        try:
            for k,v in kwargs.items():
                out[k] = grabber(df,v)
        except AttributeError:
            if isinstance(kwargs,str):
                out[k] = df[k]
            else: # A list?
                for k in kwargs:
                    out[k] = df[k]
    else:
        out = df

    out = out.set_index(list(idxvars.keys()))

    return out

def get_categorical_mapping(fn='categorical_mapping.org',tablename=None,idxvars='Code',
                            dirs=['./','../../_/','../../../_/'],asdict=True,**kwargs):
    """Return mappings for categories.

    By default, searches for =tablename= in an orgfile
    'categorical_mapping.org'. But if fn is a path to a dta file instead,
    returns categories for tablename from the stata file.
    """
    ext = Path(fn).suffix

    if ext.lower()=='.dta': # A stata file.
        cats = get_dataframe(fn,convert_categoricals=True,categories_only=True)
        if tablename is None:
            return cats
        else:
            return cats[tablename]

    for d in dirs:
        try:
            if d[-1]!="/": d+='/'
            df = df_data_grabber(d+fn,idxvars,orgtbl=tablename,**kwargs)
            df = df.squeeze()
            if asdict:
                return df.to_dict()
            else:
                return df
        except (FileNotFoundError,KeyError) as error:
            exc = error

    exc.add_note(f"No table {tablename} found in any file {fn} in directories {dirs}.")
    raise exc


def harmonized_unit_labels(fn='../../_/unitlabels.csv',key='Code',value='Preferred Label'):
    unitlabels = pd.read_csv(fn)
    unitlabels.columns = [s.strip() for s in unitlabels.columns]
    unitlabels = unitlabels[[key,value]].dropna()
    unitlabels.set_index(key,inplace=True)

    return unitlabels.squeeze().str.strip().to_dict()


def harmonized_food_labels(fn='../../_/food_items.org',key='Code',value='Preferred Label'):
    # Harmonized food labels
    food_items = pd.read_csv(fn,delimiter='|',skipinitialspace=True,converters={1:int,2:lambda s: s.strip()})
    food_items.columns = [s.strip() for s in food_items.columns]
    food_items = food_items[[key,value]].dropna()
    food_items.set_index(key,inplace=True)

    return food_items.squeeze().str.strip().to_dict()

def prices_and_units(fn='',units='units',item='item',HHID='HHID',market='market',farmgate='farmgate'):

    food_items = harmonized_food_labels(fn='../../_/food_items.org')

    # Unit labels
    with dvc.api.open(fn,mode='rb') as dta:
        sr = pd.io.stata.StataReader(dta)
        try:
            unitlabels = sr.value_labels()[units]
        except KeyError: # No guarantee that keys for labels match variables!?
            foo = sr.value_labels()
            key = [k for k,v in foo.items() if 'Kilogram' in [u[:8] for l,u in v.items()]][0]
            unitlabels = sr.value_labels()[key]

    with dvc.api.open(fn,mode='rb') as dta:
        # Prices
        prices,itemlabels=get_food_prices(dta,itmcd=item,HHID=HHID, market=market,
                                          farmgate=farmgate,units=units,itemlabels=food_items)

    prices = prices.replace({'units':unitlabels})
    prices.units = prices.units.astype(str)

    pd.Series(unitlabels).to_csv('unitlabels.csv')

    return prices

def food_acquired(fn,myvars,convert_categoricals):

    with dvc.api.open(fn,mode='rb') as dta:
        df = from_dta(dta,convert_categoricals=False)

    df = df.loc[:,[v for v in myvars.values()]].rename(columns={v:k for k,v in myvars.items()})

    df = df.set_index(['HHID','item','units']).dropna(how='all')

    df.index.names = ['j','i','units']


    # Fix type of hhids if need be
    if df.index.get_level_values('j').dtype ==float:
        fix = dict(zip(df.index.levels[0],df.index.levels[0].astype(int).astype(str)))
        df = df.rename(index=fix,level=0)

    df = df.rename(index=harmonized_food_labels(),level='i')
    unitlabels = harmonized_unit_labels()
    df = df.rename(index=unitlabels,level='units')

    if not 'market' in df.columns:
        df['market'] = df.filter(regex='^market').median(axis=1)

    # Compute unit values
    df['unitvalue_home'] = df['value_home']/df['quantity_home']
    df['unitvalue_away'] = df['value_away']/df['quantity_away']
    df['unitvalue_own'] = df['value_own']/df['quantity_own']
    df['unitvalue_inkind'] = df['value_inkind']/df['quantity_inkind']

    # Deal with possible zeros in quantities
    df['unitvalue_home'] = df['unitvalue_home'].where(np.isfinite(df['unitvalue_home']))
    df['unitvalue_away'] = df['unitvalue_away'].where(np.isfinite(df['unitvalue_away']))
    df['unitvalue_own'] = df['unitvalue_own'].where(np.isfinite(df['unitvalue_own']))
    df['unitvalue_inkind'] = df['unitvalue_inkind'].where(np.isfinite(df['unitvalue_inkind']))


    # Get list of units used in current survey
    units = list(set(df.index.get_level_values('units').tolist()))

    unknown_units = set(units).difference(unitlabels.values())
    if len(unknown_units):
        warnings.warn("Dropping some unknown unit codes!")
        print(unknown_units)
        df = df.loc[df.index.isin(unitlabels.values(),level='units')]

    with open('../../_/conversion_to_kgs.json','r') as f:
        conversion_to_kgs = pd.Series(json.load(f))

    conversion_to_kgs.name='Kgs'
    conversion_to_kgs.index.name='units'

    df = df.join(conversion_to_kgs,on='units')
    df = df.astype(float)

    return df

def food_expenditures(fn='',purchased=None,away=None,produced=None,given=None,item='item',HHID='HHID'):
    food_items = harmonized_food_labels(fn='../../_/food_items.org')

    with dvc.api.open(fn,mode='rb') as dta:
        expenditures,itemlabels=get_food_expenditures(dta,purchased,away,produced,given,itmcd=item,HHID=HHID,itemlabels=food_items)

    expenditures.index.name = 'j'
    expenditures.columns.name = 'i'

    expenditures = expenditures[expenditures.columns.intersection(food_items.values())]
        
    return expenditures


def nonfood_expenditures(fn='',purchased=None,away=None,produced=None,given=None,item='item',HHID='HHID'):
    nonfood_items = harmonized_food_labels(fn='../../_/nonfood_items.org',key='Code',value='Preferred Label')
    with dvc.api.open(fn,mode='rb') as dta:
        expenditures,itemlabels=get_food_expenditures(dta,purchased,away,produced,given,itmcd=item,HHID=HHID,itemlabels=nonfood_items)

    expenditures.index.name = 'j'
    expenditures.columns.name = 'i'
    expenditures = expenditures[expenditures.columns.intersection(nonfood_items.values())]

    return expenditures

def food_quantities(fn='',item='item',HHID='HHID',
                    purchased=None,away=None,produced=None,given=None,units=None):
    food_items = harmonized_food_labels(fn='../../_/food_items.org')

        # Prices
    with dvc.api.open(fn,mode='rb') as dta:
        quantities,itemlabels=get_food_expenditures(dta,purchased,away,produced,given,itmcd=item,HHID=HHID,units=units,itemlabels=food_items)

    quantities.index.names = ['j','u']
    quantities.columns.name = 'i'
        
    return quantities

def age_sex_composition(fn,sex='sex',sex_converter=None,age='age',months_spent='months_spent',HHID='HHID',months_converter=None, convert_categoricals=True,Age_ints=None,fn_type='stata'):

    if Age_ints is None:
        # Match Uganda FCT categories
        Age_ints = ((0,4),(4,9),(9,14),(14,19),(19,31),(31,51),(51,100))
        
    with dvc.api.open(fn,mode='rb') as dta:
        df = get_household_roster(fn=dta,HHID=HHID,sex=sex,age=age,months_spent=months_spent,
                                  sex_converter=sex_converter,months_converter=months_converter,
                                  Age_ints=Age_ints)

    df.index.name = 'j'
    df.columns.name = 'k'
    
    return df


def other_features(fn,urban=None,region=None,HHID='HHID',urban_converter=None):

    with dvc.api.open(fn,mode='rb') as dta:
        df = get_household_identification_particulars(fn=dta,HHID=HHID,urban=urban,region=region,urban_converter=urban_converter)

    df.index.name = 'j'
    df.columns.name = 'k'

    return df

def change_id(x,fn=None,id0=None,id1=None,transform_id1=None):
    """Replace instances of id0 with id1.

    The identifier id0 is assumed to be unique.

    If mapping id0->id1 is not one-to-one, then id1 modified with
    suffixes of the form _%d, with %d replaced by a sequence of
    integers.
    """
    idx = x.index.names

    if fn is None:
        x = x.reset_index()
        if x['j'].dtype==float:
            x['j'].astype(str).apply(lambda s: s.split('.')[0]).replace('nan',np.nan)
        elif x['j'].dtype==int:
            x['j'] = x['j'].astype(str)

        x = x.set_index(idx)

        return x

    try:
        with open(fn,mode='rb') as dta:
            id = from_dta(dta)
    except IOError:
        with dvc.api.open(fn,mode='rb') as dta:
            id = from_dta(dta)

    id = id[[id0,id1]]

    for column in id:
        if id[column].dtype==float:
            id[column] = id[column].astype(str).apply(lambda s: s.split('.')[0]).replace('nan',np.nan)
        elif id[column].dtype==int:
            id[column] = id[column].astype(str).replace('nan',np.nan)
        elif id[column].dtype==object:
            id[column] = id[column].replace('nan',np.nan)

    ids = dict(id[[id0,id1]].values.tolist())

    if transform_id1 is not None:
        ids = {k:transform_id1(v) for k,v in ids.items()}

    d = defaultdict(list)

    for k,v in ids.items():
        d[v] += [k]

    try:
        d.pop(np.nan)  # Get rid of nan key, if any
    except KeyError: pass

    updated_id = {}
    for k,v in d.items():
        if len(v)==1: updated_id[v[0]] = k
        else:
            for it,v_element in enumerate(v):
                updated_id[v_element] = '%s_%d' % (k,it)

    x = x.reset_index()
    x['j'] = x['j'].map(updated_id).fillna(x['j'])
    x = x.set_index(idx)

    assert x.index.is_unique, "Non-unique index."

    return x



def add_markets_from_other_features(country,df,additional_other_features=False):
    of = pd.read_parquet(f"../{country}/var/other_features.parquet", engine='pyarrow')

    df_idx = df.index.names

    try:
        df = df.droplevel('m')
    except KeyError:
        pass

    colname = df.columns.names

    if additional_other_features:
        if 'm' in of.index.names:
            df = df.join(of.reset_index('m'), on=['j','t'])
        else:
            df = df.join(of, on=['j','t'])
    else:
        if 'm' in of.index.names:
            df = df.join(of.reset_index('m')['m'], on=['j','t'])
        else:
            df = df.join(of['m'], on=['j','t'])


    df = df.reset_index().set_index(df_idx)
    df.columns.names = colname

    return df

def df_from_orgfile(orgfn,name=None,set_columns=True,to_numeric=True,encoding=None):
    """Extract the org table with name from the orgmode file named orgfn; return a pd.DataFrame.

    If name is None (the default), then we assume the orgtable is the very first
    thing in the file, with the possible exception of options (lines starting with #+).

    Note that we assume that cells with the string '---' should be null.

    Ethan Ligon                                                       March 2023
    """
    # Grab file as a list of strings
    with open(orgfn,'r',encoding=encoding) as f:
        contents = f.readlines()

    # Get indices of #+name: lines:
    names = [i for i,s in enumerate(contents) if f'#+name: {name}'.lower()==s.strip().lower()]

    if len(names)==0:
        #warnings.warn(f'No table {name} in {orgfn}.')
        start = 0
    elif len(names)>1:
        start = names[0]
        warnings.warn(f'More than one table with {name} in {orgfn}.  Reading first one at line {start}.')
    else:
        start = names[0]

    # Advance to line that starts table
    i = start
    while contents[i].strip()[:2] == '#+': i +=1

    table =[]
    nextline = contents[i].strip()
    if set_columns and len(nextline) and nextline[0] == '|':
        columns = [s.strip() for s in nextline.split('|')[1:-1]]
        i+=1
        nextline = contents[i].strip()
    else:
        columns = None

    while len(nextline) and nextline[0] == '|':
        line = contents[i].strip()
        if line[-1] == '|' and  line[:2] != '|-':
            table.append([s.strip() for s in line.split('|')[1:-1]])
        i+=1
        try:
            nextline = contents[i].strip()
        except IndexError: # End of file?
            break

    df = pd.DataFrame(table,columns=columns)

    df = df.replace({'---':np.nan})

    if to_numeric:
        # Try to convert columns to numeric types, but fail gracefully
        df = df.apply(_to_numeric)

    return df

def change_encoding(s,from_encoding,to_encoding='utf-8',errors='ignore'):
    """
    Change encoding of a string s from_encoding to_encoding.

    For example, strings in data may be encoded in latin-1 or ISO-8859-1.
    We usually want utf-8.
    """
    return bytes(s,encoding=from_encoding).decode(to_encoding,errors=errors)

def to_parquet(df,fn):
    """
    Write df to parquet file fn.

    Parquet (pyarrow) is slightly more picky about data types and layout than is pandas;
    here we fix some possible problems before calling pd.DataFrame.to_parquet.
    """
    if len(df.shape)==0: # A series?  Need a dataframe.
        df = pd.DataFrame(df)

    # Can't mix types of category labels.
    for col in df:
        if df[col].dtype == 'category':
            cats = df[col].cat.categories
            if str in [type(x) for x in cats]: # At least some categories are strings...
                df[col] = df[col].cat.rename_categories(lambda x: str(x))

    # Pyarrow can't deal with mixes of types in columns of type object. Just
    # convert them all to str.
    idxnames = df.index.names
    all = df.reset_index()
    for column in all:
        if all[column].dtype=='O':
            all[column] = all[column].astype(str).astype('string[pyarrow]').replace('nan',None)
    df = all.set_index(idxnames)

    df.to_parquet(fn, engine='pyarrow')

    return df

from collections import UserDict

class RecursiveDict(UserDict):
    def __init__(self,*arg,**kw):
      super(RecursiveDict, self).__init__(*arg, **kw)

    def __getitem__(self,k):
        try:
            while True:
                k = UserDict.__getitem__(self,k)
        except KeyError:
            return k

def format_id(id,zeropadding=0):
    """Nice string format for any id, string or numeric.

    Optional zeropadding parameter takes an integer
    formats as {id:0z} where
    """
    if pd.isnull(id) or id in ['','.']: return None

    try:  # If numeric, return as string int
        return ('%d' % id).zfill(zeropadding)
    except TypeError:  # Not numeric
        return id.split('.')[0].strip().zfill(zeropadding)
    except ValueError:
        return None

def update_id(d, id_splits):
    '''
    Update the dictionary d, which maps old ids to new ids, splits are followed by underscore ('_').
    For example:
        old_to_new_ids = {
                            'A': 'X',
                            'B': 'Y',
                            'C': 'X',
                            'D': 'Z',
                            'E': 'Y'
                        }
    would be updated to:
        updated_ids = {'A': 'X', 'C': 'X_1', 'B': 'Y', 'E': 'Y_1', 'D': 'Z'}
    '''
    D_inv = {}
    for k, v in d.items():
        if v not in D_inv:
            D_inv[v] = [k]
        else:
            D_inv[v].append(k)

    updated_id = {}
    for k, v in D_inv.items():
        if len(v)==1: 
            updated_id[v[0]] = k
            id_splits[k] = 0
        else:
            for it,v_element in enumerate(v):
                split = id_splits.get(k, 0) + it
                if it == 0:
                    updated_id[v_element] = k
                else:
                    updated_id[v_element] = '%s_%d' % (k,split)
            id_splits[k] = id_splits.get(k, 0)+len(v)-1

    return updated_id, id_splits


def panel_ids(Waves):
    '''
    Input: DataFrame with a MultiIndex that includes a level named 't' representing the wave and 'i' current househod ID'
            And single 'previous_i' column as the previous household ID.
    Output: Wave-specific panel id mapping dictionaires and a recursive dictionary of tuple of (wave, household identifiers)
    '''
    if isinstance(Waves, dict):
        dfs = []
        for wave_year, wave_info in Waves.items():
            if not wave_info:
                continue  # skip empty entries

            file_path = f"../{wave_year}/Data/{wave_info[0]}"
            if isinstance(wave_info[1], list):
                columns = wave_info[1]
            else:
                columns = [wave_info[1], wave_info[2]]

            df = get_dataframe(file_path)[columns]

            # Process mapping when recent_id is a list (list-based mapping)
            if isinstance(wave_info[1], list): #tanzania
                df = wave_info[2](df, wave_info[1])
            else:
                df.loc[:,wave_info[1]] = df[wave_info[1]].apply(format_id)
                df.loc[:,wave_info[2]] = df[wave_info[2]].apply(format_id)
                # If a transformation function is provided (tuple length 4), apply it to the old_id column
                if len(wave_info) == 4:
                    df.loc[:,wave_info[2]] = df[wave_info[2]].apply(wave_info[3])
                df['t'] = wave_year
                df = df.rename(columns={wave_info[1]: 'i', wave_info[2]: 'previous_i'})
                df = df.set_index(['t', 'i'])[['previous_i']]
            dfs.append(df)
        panel_ids_df = pd.concat(dfs, axis=0)
    else:
        # If Waves is not a dictionary, assume it's a DataFrame
        panel_ids_df = Waves.copy()

    updated_wave = {}
    check_id_split = {}
    sorted_waves = sorted(panel_ids_df.index.get_level_values('t').unique())
    recursive_D = RecursiveDict()
    for wave_year in sorted_waves:
        df = panel_ids_df[panel_ids_df.index.get_level_values('t') == wave_year].copy().reset_index()
        wave_matches = df[['i', 'previous_i']].dropna().set_index('i')['previous_i'].to_dict()
        previous_wave = sorted_waves[sorted_waves.index(wave_year) - 1] if sorted_waves.index(wave_year) > 0 else None
        if previous_wave:
            previous_wave_matches = updated_wave[previous_wave]
            # update the current wave matches dictionary values to the previous wave matches
            wave_matches = {k: previous_wave_matches.get(v, v)for k, v in wave_matches.items()}
            recursive_D.update({(wave_year, k): (previous_wave, v) for k, v in wave_matches.items()})
        wave_matches, check_id_split = update_id(wave_matches,  check_id_split)
        updated_wave[wave_year] = wave_matches
    return recursive_D, updated_wave

def id_walk(df, updated_ids, hh_index='i'):
    '''
    Updates household IDs in panel data across different waves separately.

    Parameters:
        df (DataFrame): Panel data with a MultiIndex, including 't' for wave and 'i' (default) for household ID.
        updated_ids (dict): A dictionary mapping each wave to another dictionary that maps original household IDs to updated IDs.
            Format:
                {wave_1: {original_id: new_id, ...},
                 wave_2: {original_id: new_id, ...}, ...}
        hh_index (str): Index name for the household ID level (default is 'i').

    Example:
        updated_ids = {
            '2013-14': {'0001-001': '101012150028', '0009-001': '101015620053', '0005-001': '101012150022'},
            '2016-17': {'0001-002': '0001-001', '0003-001': '0005-001', '0005-001': '0009-001'}
        }

        In this example, IDs are updated independently for each wave.
        Because the same original household ID across different waves may not represent the same household.
        Specifically, household '0005-001' in wave '2016-17' corresponds to household '0009-001' from wave '2013-14', not '0005-001' from '2013-14'.

    The function handles these wave-specific mappings separately, ensuring accurate household identification over time.
    '''
    #seperate df into different waves:
    dfs = {}
    waves = df.index.get_level_values('t').unique()
    for wave in waves:
        dfs[wave] = df[df.index.get_level_values('t') == wave].copy()
    #update ids for each wave
    for wave, df_wave in dfs.items():
        #update ids
        if wave in updated_ids:
            df_wave = df_wave.rename(index=updated_ids[wave], level=hh_index)
            #update the dataframe with the new ids
            dfs[wave] = df_wave
        else:
            continue
    #combine the updated dataframes
    df = pd.concat(dfs.values(), axis=0)

    # df= df.rename(index=updated_ids,level=['t', hh_index])
    df.attrs['id_converted'] = True
    return df      

        
def conversion_table_matching_global(df, conversions, conversion_label_name, num_matches=3, cutoff = 0.6):
    """
    Returns a Dataframe containing matches and Dictionary mapping top choice
    from a conversion table's labels to item labels from a given df.

    """
    D = defaultdict(dict)
    all_matches = pd.DataFrame(columns=["Conversion Table Label"] +
                               ["Match " + str(n) for n in range(1, num_matches + 1)])
    items_unique = df['i'].str.capitalize().unique()
    for l in conversions[conversion_label_name].unique():
        k = difflib.get_close_matches(l.capitalize(), items_unique, n = num_matches, cutoff=cutoff)
        if len(k):
            D[l] = k[0]
            k = [l] + k
            all_matches.loc[len(all_matches.index)] = k + [np.nan] * (num_matches + 1 - len(k))
        else:
            D[l] = l
            all_matches.loc[len(all_matches.index)] = [l] + [np.nan] * num_matches
    return all_matches, D

def category_union(dict_list):
    """Construct union of a list of dictionaries, preserving unique *values*.

    Returns this union, as well as a list of dictionaries mapping the original
    dicts into the union.

    >>> c1={1:'a',2:'b',3:'c'}
    >>> c2={1:'b',2:'c',3:'d',4:"a'"}
    >>> c0,t1,t2 = category_union([c1,c2])
    >>> c0[t1[2]]==c1[2]
    True
    """
    cv = []
    for i in range(len(dict_list)):
        cv += list(set(dict_list[i].values()))

    cv = list(set(cv))

    c0 = dict(zip(range(len(cv)),cv))

    c0inv = {v:k for k,v in c0.items()}

    t = []
    for i in range(len(dict_list)):
        t.append({k:c0inv[v] for k,v in dict_list[i].items()})

    return c0,*tuple(t)

def category_remap(c,remaps):
    """
    Return a "remapped" dictionary.

    This is a composition of two dictionaries.
    A dictionary remaps values in dict c into other values in c.
    """
    cinv = {v:k for k,v in c.items()}
    for k,v in remaps.items():
        c[cinv[k]] = v

    return c

def panel_attrition(df, waves, index='i', return_ids=False, split_households_new_sample=True):
    """
    Produce an upper-triangular) matrix showing the number of households (j) that
    transition between rounds (t) of df.
            split_households_new_sample (bool): Determines how to count split households:
                                - If True, we assume split_households as new sample. So we
                                     do not count and trace splitted household, only counts 
                                     the primary household in each split. The number represents
                                     how many main (primary) households in previous waves have 
                                     appeared in current round.
                                - If False, counts all split households that can be traced 
                                    back to previous wave households. The number represents how 
                                    many households (including splitted households
                                    round can be traced back to the previous round.
    
    Note: First three rounds used same sample. Splits of the main households may happen in different rounds.
    """
    waves = sorted(waves)
    df_reset = df.reset_index()
    idx_by_wave = df_reset.groupby('t')[index].apply(set).to_dict()

    # Precompute parent ID mappings for all IDs in all waves
    parent_ids_map = {
        t: {i: ['_'.join(i.split('_')[:-n]) for n in range(1, len(i.split('_')))] 
            for i in ids} 
        for t, ids in idx_by_wave.items()
    }

    foo = pd.DataFrame(index=waves, columns=waves)
    IDs = {}

    for i, s in enumerate(waves):
        ids_s = idx_by_wave[s]
        for t in waves[i:]:
            ids_t = idx_by_wave[t]
            common = ids_s & ids_t

            if not split_households_new_sample:
                # Consider split households
                additional = {i for i in ids_t - common
                              for p in parent_ids_map[t].get(i, [])
                              if p in ids_s}
                common |= additional

            IDs[(s, t)] = common
            foo.loc[s, t] = len(common)

    return (foo, IDs) if return_ids else foo

def write_df_to_org(df, table_name, filepath=None):
    '''
    Writes a DataFrame to an Org-mode table format.
    Parameters:
    df (pandas.DataFrame): The DataFrame to be converted and written.
    table_name (str): The name to be assigned to the Org table.
    filepath (str, optional): The file path where the Org table will be written. 
                              If None, the function returns the Org table as a string, used in Emacs Python Block.
    Returns:
    str: The Org table as a string if filepath is None.
    '''

    if filepath is not None:
        mode = 'a' if Path(filepath).exists() else 'w'
        with open(filepath, mode, encoding="utf-8") as file:
            file.write(f"#+NAME: {table_name}\n")
            file.write(df_to_orgtbl(df))  # Convert label DataFrame to Org table
            file.write("\n\n")  # Add spacing
    else:
        s = f"#+NAME: {table_name}\n"
        s += df_to_orgtbl(df)
        s += "\n\n"
        return s
    
def map_index(df):
    """
    Map index from old parquet file to new index used in data_info.yml
    -- March 11, 2025
    """
    mapping_rules = {'w': 't'}
    if 'u' in df.index.names:
        df = df.rename(index={k: 'unit' for k in ['<NA>', 'nan', np.nan]}, level='u')


    mapping_rules.update({
        'i': 'temp_j',
        'j': 'i',
        'previous_j': 'previous_i'
    })
    df_renamed = df.rename_axis(index=mapping_rules)
    df_renamed = df_renamed.rename_axis(index = {'temp_j': 'j'})
    
    return df_renamed


import importlib.util
def get_formatting_functions(mod_path, name, general_formatting_functions={} ):
    formatting_function = general_formatting_functions.copy()
    if mod_path.exists():
    # Load module dynamically
        spec = importlib.util.spec_from_file_location(name, mod_path)
        formatting_module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(formatting_module)
        formatting_function.update({
            name: func
            for name, func in vars(formatting_module).items()
            if callable(func)
            })
        return formatting_function
    else:
        formatting_function.update({})
        return formatting_function

def age_handler(age = None, interview_date = None, interview_year = None, format_interv = None, dob = None, format_dob  = None, m = None, d = None, y = None):
    '''
    a function to calculate the age of an individual with the best available information, prioritizes more precise estimates, in cases where day is unknown, the middle of the month is used

    Args:
        interview_date : interview date, can be passed as a list in [y, m, d] format, supports dropping columns from right
        interview_year: year of interview; please enter an estimation in case an interview date is not found
        format_interv: argument to be passed into pd.to_datetime(, format=) for interview_date
        age : age in years
        dob: date of birth, if given in a single column
        format_dob: to be passed into pd.to_datetime(, format=) for date of birth
        m, d, y: month, day, and year of birth respectively, if specified in separate columns

    Returns:
    a float representing the best estimate of the age of an individual
    '''

    final_date_of_birth = None
    final_interview_date = None
    interview_yr = int(interview_year)
    year_born = y

    def is_valid(x):
        if isinstance(x, list):
            return all(pd.notna(x)) and all([is_valid(i) for i in x])
        elif pd.notna(x) and int(float(x)) < 2100:
            return True
        return False

    if age is not None and pd.notna(age):
        if is_valid(int(age)):
            return int(age)

    # interview handling
    if interview_date is not None and pd.notna(interview_date):
        if isinstance(interview_date, list):
            if len(interview_date) == 3 and is_valid(interview_date):
                interview_date = str(int(interview_date[1])) + '/' + str(int(interview_date[2])) + '/' + str(int(interview_date[0]))
                format_interv = "%m/%d/%Y"
            elif len(interview_date) >= 2 and is_valid(interview_date):
                interview_date = str(int(interview_date[1])) + '/15/' + str(int(interview_date[0]))
                format_interv = "%m/%d/%Y"
            elif len(interview_date) >= 1 and is_valid(interview_date):
                interview_yr = int(interview_date[0])
        if format_interv:
            final_interview_date = pd.to_datetime(interview_date, format = format_interv)
            interview_yr = interview_date.year
        else:
            try:
                final_interview_date = pd.to_datetime(interview_date)
            except: 
                final_interview_date = None

    # dob handling
    if dob is not None and pd.notna(dob):
        final_date_of_birth = pd.to_datetime(dob, format = format_dob)
        year_born = final_date_of_birth.year
    #conversion to pd.datetime obj of the date of birth if we are given mdy or all values
    elif is_valid([m, d, y]):
        date_conv = str(int(m)) + '/' + str(int(d)) + '/' + str(int(y))
        final_date_of_birth = pd.to_datetime(date_conv, format = "%m/%d/%Y")
    elif is_valid([m, y]):
        date_conv = str(int(m)) + '/15/' + str(int(y))
        final_date_of_birth = pd.to_datetime(date_conv, format = "%m/%d/%Y")

    #final calculations
    if final_interview_date and final_date_of_birth:
        return round((final_interview_date - final_date_of_birth).days / 365.25, 2)
    elif is_valid([year_born, interview_yr]):
        return int(interview_yr) - int(year_born)
    else:
        return np.nan

def age_handler_wrapper(df, interview_date = None, interview_year = None, format_interv = None, age = None, dob = None, format_dob = None, m = None, d = None, y = None):
    '''
    a function that calculates ages for rows in a dataframe by calling age_handler 

    Args:
        df: the dataframe
        interview_date : column interview date
        interview_year: int year of interview or column, should exist for all rows
        format_interv: argument to be passed into pd.to_datetime(, format=) for interview_date
        age : column age
        dob: column date of birth
        format_dob: to be passed into pd.to_datetime(, format=) for date of birth
        m, d, y: columns month, day, and year of birth respectively

    Returns:
    returns a new Series with the calculated ages
    '''
    
    def row_funct(row):
        r_age = row[age] if age else None
        r_interview_date = row[interview_date] if interview_date else None
        if not isinstance(interview_year, int):
            interview_year = row[interview_year]
        r_dob = row[dob] if dob else None
        r_m = row[m] if m else None
        r_d = row[d] if d else None
        r_y = row[y] if y else None
        return age_handler(age = r_age, interview_date = r_interview_date, interview_year = interview_year, format_interv = format_interv, dob = r_dob, format_dob  = format_dob, m = r_m, d = r_d, y = r_y)

    return df.apply(row_funct, axis=1)




def all_dfs_from_orgfile(orgfn, set_columns=True, to_numeric=True, encoding=None):
    """
    Read all named org-mode tables from a .org file and return as a dictionary of DataFrames.
    
    Parameters:
        orgfn (str): Path to the org file.
        set_columns (bool): Whether to use the first table row as column names.
        to_numeric (bool): Attempt to convert all values to numeric.
    
    Returns:
        dict: {table_name: DataFrame}
    """
    with open(orgfn, 'r', encoding=encoding) as f:
        contents = f.readlines()

    tables = {}
    i = 0
    while i < len(contents):
        line = contents[i].strip()
        
        if line.lower().startswith('#+name:'):
            table_name = line.split(':', 1)[1].strip()
            i += 1
            # Skip any extra #+ lines
            while i < len(contents) and contents[i].strip().startswith('#+'):
                i += 1
            
            # Start reading table
            table_lines = []
            header = None

            if i < len(contents) and contents[i].strip().startswith('|'):
                if set_columns:
                    header = [s.strip() for s in contents[i].strip().split('|')[1:-1]]
                    i += 1

            while i < len(contents) and contents[i].strip().startswith('|'):
                row = contents[i].strip()
                if row.startswith('|-'):  # separator line
                    i += 1
                    continue
                row_data = [s.strip() for s in row.split('|')[1:-1]]
                table_lines.append(row_data)
                i += 1

            df = pd.DataFrame(table_lines, columns=header if set_columns else None)
            df = df.replace({'---': np.nan})

            if to_numeric:
                df = df.apply(_to_numeric)

            tables[table_name] = df
        else:
            i += 1

    return tables
