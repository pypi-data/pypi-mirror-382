import pandas as pd
import json
import numpy as np


def load_statsbomb_skillcorner(statsbomb_event_dir: str, skillcorner_tracking_dir: str, skillcorner_match_dir: str, statsbomb_match_id: str, skillcorner_match_id: str) -> pd.DataFrame:
    """
    Load and merge StatsBomb event data with SkillCorner tracking data.

    Args:
        statsbomb_event_dir (str): Directory path for StatsBomb event data.
        skillcorner_tracking_dir (str): Directory path for SkillCorner tracking data.
        skillcorner_match_dir (str): Directory path for SkillCorner match data.
        statsbomb_match_id (str): Match ID for StatsBomb data.
        skillcorner_match_id (str): Match ID for SkillCorner data.

    Returns:
        pd.DataFrame: Combined DataFrame with event and tracking data.
    """
    
    # File paths
    statsbomb_event_path = f"{statsbomb_event_dir}/{statsbomb_match_id}.csv"
    skillcorner_tracking_path = f"{skillcorner_tracking_dir}/{skillcorner_match_id}.json"
    skillcorner_match_path = f"{skillcorner_match_dir}/{skillcorner_match_id}.json"

    #check if the file exists
    import os
    if not os.path.exists(statsbomb_event_path):
        print(f"Statsbomb event file not found: {statsbomb_event_path}")
        return None
    if not os.path.exists(skillcorner_tracking_path):
        print(f"Skillcorner tracking file not found: {skillcorner_tracking_path}")
        return None
    if not os.path.exists(skillcorner_match_path):
        print(f"Skillcorner match file not found: {skillcorner_match_path}")
        return None

    # Load StatsBomb events
    events = pd.read_csv(statsbomb_event_path)
    
    # Load SkillCorner tracking and match data
    with open(skillcorner_tracking_path) as f:
        tracking = json.load(f)
    
    with open(skillcorner_match_path) as f:
        match = json.load(f)

    # Team name mapping
    team_name_dict = {
        'UD Almería': 'Almería', 'Real Sociedad': 'Real Sociedad', 'Athletic Club de Bilbao': 'Athletic Club', 
        'Villarreal CF': 'Villarreal', 'RC Celta de Vigo': 'Celta Vigo', 'Getafe CF': 'Getafe', 
        'UD Las Palmas': 'Las Palmas', 'Sevilla FC': 'Sevilla', 'Cadiz CF': 'Cádiz', 
        'Atlético Madrid': 'Atlético Madrid', 'RCD Mallorca': 'Mallorca', 'Valencia CF': 'Valencia', 
        'CA Osasuna': 'Osasuna', 'Girona FC': 'Girona', 'Real Betis Balompié': 'Real Betis', 
        'FC Barcelona': 'Barcelona', 'Deportivo Alavés': 'Deportivo Alavés', 'Granada CF': 'Granada', 
        'Rayo Vallecano': 'Rayo Vallecano', 'Real Madrid CF': 'Real Madrid'
    }
    
    home_team_name = team_name_dict[match['home_team']['name']]
    away_team_name = team_name_dict[match['away_team']['name']]
    
    team_dict = {
        match['home_team']['id']: {'role': 'home', 'name': home_team_name},
        match['away_team']['id']: {'role': 'away', 'name': away_team_name}
    }

    # Convert the trackable object dict
    trackable_objects = {}
    home_count = away_count = 0
    
    for player in match['players']:
        role = team_dict[player['team_id']]['role']
        if role == 'home':
            trackable_objects[player['trackable_object']] = {
                'name': f"{player['first_name']} {player['last_name']}",
                'team': team_dict[player['team_id']]['name'],
                'role': role,
                'id': home_count
            }
            home_count += 1
        elif role == 'away':
            trackable_objects[player['trackable_object']] = {
                'name': f"{player['first_name']} {player['last_name']}",
                'team': team_dict[player['team_id']]['name'],
                'role': role,
                'id': away_count
            }
            away_count += 1

    trackable_objects[match['ball']['trackable_object']] = {'name': 'ball', 'team': 'ball', 'role': 'ball'}

    # Process tracking data
    tracking_dict = {}
    for frame in tracking:
        time = frame['timestamp']
        if time:
            time_components = time.split(':')
            seconds = float(time_components[0]) * 3600 + float(time_components[1]) * 60 + float(time_components[2])
            period = frame['period']
            uid = f"{period}_{seconds}"
            tracking_dict[uid] = frame['data']

    # Prepare data for DataFrame
    df_list = []
    for _, event in events.iterrows():
        event_id = event['id']
        match_id = statsbomb_match_id
        period = event['period']
        time = event['timestamp']
        minute = event['minute']
        second = event['second']
        event_type = event['type']
        event_type_2 = None
        end_x = end_y = None
        if event_type == "Pass":
            end_location=event.get('pass_end_location')
            #check if end_location is a string
            if isinstance(end_location, (str)):
                end_location = [float(x) for x in end_location[1:-1].split(",")]
                end_x = end_location[0]
                end_y = end_location[1]
            cross=event.get('pass_cross')
            pass_height=event.get('pass_height')
            pass_type=event.get('pass_type')
            if pass_type=="Corner":
                event_type_2="Corner"
            elif cross and not np.isnan(cross):
                event_type_2="Cross"
            elif pass_height:
                event_type_2=pass_height
        elif event_type=="Shot":
            event_type_2=event.get('shot_outcome')

        team = event['team']
        player = event['player']
        location = event['location']

        if isinstance(location, str):
            location = [float(x) for x in location[1:-1].split(",")]
            start_x, start_y = location[0], location[1]
        else:
            start_x = start_y = None

        time_components = time.split(':')
        seconds = float(time_components[0]) * 3600 + float(time_components[1]) * 60 + round(float(time_components[2]), 1)
        if period == 2:
            seconds += 45 * 60
        elif period == 3:
            seconds += 90 * 60
        elif period == 4:
            seconds += (90 + 15) * 60

        uid = f"{period}_{seconds}"
        tracking_data = tracking_dict.get(uid)
        home_tracking = [None] * 2 * 23
        away_tracking = [None] * 2 * 23
        
        if tracking_data:
            for obj in tracking_data:
                track_obj = trackable_objects[obj['trackable_object']]
                if track_obj['role'] == 'home':
                    home_tracking[2 * track_obj['id']] = obj['x']
                    home_tracking[2 * track_obj['id'] + 1] = obj['y']
                elif track_obj['role'] == 'away':
                    away_tracking[2 * track_obj['id']] = obj['x']
                    away_tracking[2 * track_obj['id'] + 1] = obj['y']

        df_list.append([match_id, period, time, minute, second, seconds, event_type, event_type_2, team, player, start_x, start_y, end_x, end_y, *home_tracking, *away_tracking])
    
    # Define DataFrame columns
    home_tracking_columns = []
    away_tracking_columns = []
    for i in range(1, 24):
        home_tracking_columns.extend([f"h{i}_x", f"h{i}_y"])
        away_tracking_columns.extend([f"a{i}_x", f"a{i}_y"])
    columns = ["match_id", "period", "time", "minute", "second", 'seconds', "event_type", "event_type_2", "team", "player", "start_x", "start_y","end_x","end_y"] + home_tracking_columns + away_tracking_columns

    # Sort the DataFrame by 'period', 'minute', and 'second'
    df_list = sorted(df_list, key=lambda x: (x[1], x[3], x[4]))

    # Convert the event list to a DataFrame
    df = pd.DataFrame(df_list, columns=columns)

    return df

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import pdb

statsbomb_skillcorner_event_path="/data_pool_1/laliga_23/statsbomb/events"
statsbomb_skillcorner_tracking_path="/data_pool_1/laliga_23/skillcorner/tracking"
statsbomb_skillcorner_match_path="/data_pool_1/laliga_23/skillcorner/match"
match_id_path="/home/c_yeung/workspace6/python/openstarlab/PreProcessing/preprocessing/example/id_matching.csv"

out_df_list=[]
match_id_df=pd.read_csv(match_id_path)
# for i in tqdm(range(len(match_id_df))):
#     statsbomb_match_id=match_id_df.loc[i,"match_id_statsbomb"]
#     skillcorner_match_id=match_id_df.loc[i,"match_id_skillcorner"]
#     statsbomb_skillcorner_df=load_statsbomb_skillcorner(statsbomb_skillcorner_event_path,statsbomb_skillcorner_tracking_path,statsbomb_skillcorner_match_path,statsbomb_match_id,skillcorner_match_id)
#     out_df_list.append(statsbomb_skillcorner_df)

def process_match(i, match_id_df, statsbomb_skillcorner_event_path, statsbomb_skillcorner_tracking_path, statsbomb_skillcorner_match_path):
    statsbomb_match_id = match_id_df.loc[i, "match_id_statsbomb"]
    skillcorner_match_id = match_id_df.loc[i, "match_id_skillcorner"]
    statsbomb_skillcorner_df = load_statsbomb_skillcorner(
        statsbomb_skillcorner_event_path, 
        statsbomb_skillcorner_tracking_path, 
        statsbomb_skillcorner_match_path, 
        statsbomb_match_id, 
        skillcorner_match_id
    )
    return statsbomb_skillcorner_df

with ThreadPoolExecutor(max_workers=10) as executor:
    # Submit tasks to the executor
    futures = [executor.submit(process_match, i, match_id_df, statsbomb_skillcorner_event_path, statsbomb_skillcorner_tracking_path, statsbomb_skillcorner_match_path) for i in range(len(match_id_df))]

    # Collect the results as they complete
    for future in tqdm(as_completed(futures), total=len(futures)):
        out_df_list.append(future.result())


statsbomb_skillcorner_df=pd.concat(out_df_list)
statsbomb_skillcorner_df.to_csv("/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/statsbomb_skillcorner/all_data.csv",index=False)
    
print('---------------end---------------')
pdb.set_trace()