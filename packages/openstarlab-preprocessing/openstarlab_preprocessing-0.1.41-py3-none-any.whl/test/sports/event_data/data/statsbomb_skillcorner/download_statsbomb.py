import os
import pandas as pd
from statsbombpy import sb
from tqdm import tqdm
import json
import pdb

def convert_df_in_dict(d):
    for key, value in d.items():
        if isinstance(value, pd.DataFrame):
            d[key] = value.to_dict(orient='records')
        elif isinstance(value, dict):
            convert_df_in_dict(value)
    return d

save_dir = "/data_pool_1/laliga_23/statsbomb/"
os.makedirs(save_dir, exist_ok=True)
    
creds = {"user": "yeung.chikwong@g.sp.m.is.nagoya-u.ac.jp", "passwd": "00rixRYG"}

matches = sb.matches(competition_id=11, season_id=281, creds=creds)
matches["competition_id"] = 11
matches["season_id"] = 281
#moev the competition_id and season_id to the first column
cols = matches.columns.tolist()
cols = cols[-2:] + cols[:-2]
matches = matches[cols]
#save the matches to csv
matches.to_csv(os.path.join(save_dir, "matches.csv"), index=False)


# Get lineups and events
os.makedirs(os.path.join(save_dir, "lineups"), exist_ok=True)
os.makedirs(os.path.join(save_dir, "events"), exist_ok=True)
for match_id in tqdm(matches["match_id"].unique()):
    lineups = sb.lineups(match_id=match_id, creds=creds)
    events = sb.events(match_id=match_id, include_360_metrics=True, creds=creds)
    events.to_csv(os.path.join(save_dir, "events", f"{match_id}.csv"), index=False)
    #save the lineups as json and with row changes
    lineups = convert_df_in_dict(lineups)
    with open(os.path.join(save_dir, "lineups", f"{match_id}.json"), "w") as f:
        json.dump(lineups, f, indent=4)


    



