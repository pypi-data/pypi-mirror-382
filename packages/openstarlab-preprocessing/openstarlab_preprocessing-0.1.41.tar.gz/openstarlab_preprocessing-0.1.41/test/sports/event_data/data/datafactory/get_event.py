import pandas as pd 
import pdb

data_path='/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/datafactory/test_data.csv'

df=pd.read_csv(data_path)

summary=df['event_type'].value_counts()
print(summary)
# summary=df.groupby(['event_type', 'event_type_2']).size().reset_index(name='counts')
# summary.to_csv('/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/datafactory/summary.csv', index=False)
# pdb.set_trace()