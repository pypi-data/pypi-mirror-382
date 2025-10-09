import pandas as pd 
import pdb

data_path='/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/metrica/test_data_csv.csv'

df=pd.read_csv(data_path)

# df['event_type'].value_counts()
summary=df.groupby(['event_type', 'event_type_2']).size().reset_index(name='counts')
summary.to_csv('//home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/metrica/summary.csv', index=False)
pdb.set_trace()