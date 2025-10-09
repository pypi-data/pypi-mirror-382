import pandas as pd
import pdb  

df_path = "/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/statsbomb_skillcorner/all_data.csv"

df = pd.read_csv(df_path)

df["action"] = df["event_type"].astype(str) + "_" + df["event_type_2"].astype(str)

print(df["action"].unique())

pdb.set_trace()