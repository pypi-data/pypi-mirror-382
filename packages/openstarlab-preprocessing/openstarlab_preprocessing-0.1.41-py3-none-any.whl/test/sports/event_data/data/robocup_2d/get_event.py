import pandas as pd 
import pdb

data_path='/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/robocup_2d/test_data.csv'

df=pd.read_csv(data_path)

df['event_type'].value_counts()

pdb.set_trace()