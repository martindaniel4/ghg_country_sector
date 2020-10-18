import pandas as pd
import numpy as np

"""
This script takes as input: 
- emissions.csv a country, sector and emissions dataset obtained 
through the flexible query tool from the UN for climate change website
https://di.unfccc.int/detailed_data_by_party
- mapping.csv a custom categorization of each sector. 
It output emissions_all.csv that can be fed to a front-end visualization. 
"""

# read data and mapping
df = pd.read_csv('data/emissions.csv', 
                dtype={'Country':'str',
                        'Category':'str',
                        'emissions':np.float64})

mapping = pd.read_csv('data/mapping.csv')

# split string in levels
df['level'] = df['Category'].str.split('  ', n=1, expand=True)[0]

df = df.merge(mapping)
df.dropna(inplace=True) # if no match level should be removed

df.drop(['Category', 'level'], axis=1, inplace=True)
df.rename(columns={'new_level':'level'},
          inplace=True)

# sort values
df.sort_values(['Country', 'level'], 
               inplace=True)

# add a root level
root_df = pd.DataFrame(columns=df.columns)
root_df['Country'] = pd.Series(df['Country'].unique())
root_df['level'] = 'root'
root_df['emissions'] = 0
df = pd.concat([root_df, df])

# add parent node
def get_parent(x):
    x = str(x)
    split = x.rsplit('.', 1)[0]
    if x == 'root': 
        return np.nan
    elif x.find('.') == -1:
        return 'root'
    else:
        return split

df['parent'] = df.apply(lambda x : get_parent(x['level']), axis=1)

# add a boolean if the level is a leaf 
parents = list(df['parent'].unique())
df['is_leaf'] = df['level'].isin(parents).map({False:1, True:0})
df['value'] = df['emissions'] * df['is_leaf']

# export
df.to_csv('data/emissions_all.csv', 
          index=False)