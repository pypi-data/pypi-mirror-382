import os
import pandas as pd
import json
import pdb


statsbomb_meta_data_path="/data_pool_1/laliga_23/statsbomb/matches.csv"
# skillcorner_match_dir="/data_pool_1/laliga_23/skillcorner/match"
# skillcorner_tracking_dir="/data_pool_1/laliga_23/skillcorner/tracking"
skillcorner_match_dir="/work3/fujii/work/TeamSportsDataCore/processed_data/skillcorner/LaLiga-2023-2024/match"
skillcorner_tracking_dir="/work3/fujii/work/TeamSportsDataCore/processed_data/skillcorner/LaLiga-2023-2024/tracking"
save_dir="/home/c_yeung/workspace6/python/openstarlab/PreProcessing/test/sports/event_data/data/statsbomb_skillcorner/id_matching.csv"

# Load the statsbomb meta data
statsbomb_meta_data = pd.read_csv(statsbomb_meta_data_path)
# get all the match data in skillcorner directory
skillcorner_match_data = os.listdir(skillcorner_match_dir)
skillcorner_tracking_data = os.listdir(skillcorner_tracking_dir)
print(f"Number of match data in skillcorner: {len(skillcorner_match_data)}")
print(f"Number of tracking data in skillcorner: {len(skillcorner_tracking_data)}")

skillcorner_list = []
for match in skillcorner_match_data:
    if match.endswith(".json"):
        #read the json file
        with open(os.path.join(skillcorner_match_dir, match)) as f:
            skillcorner_match = json.load(f)
        #get the match_id
        match_id = skillcorner_match["id"]
        time=skillcorner_match["date_time"]
        #get the home and away team name
        home_team = skillcorner_match["home_team"]["name"]
        home_team_short = skillcorner_match["home_team"]["short_name"]
        away_team = skillcorner_match["away_team"]["name"]
        away_team_short = skillcorner_match["away_team"]["short_name"]
        skillcorner_list.append([match_id, time, home_team, home_team_short, away_team, away_team_short])

#convert the list to a dataframe
skillcorner_df = pd.DataFrame(skillcorner_list, columns=["match_id", "time", "home_team", "home_team_short", "away_team", "away_team_short"])
#get the unique home team name
# home_team_unique = skillcorner_df["home_team"].unique()
#get the unique home team short name
# home_team_short_unique = skillcorner_df["home_team_short"].unique()

#get the statsbomb meta data required columns
statsbomb_meta_data = statsbomb_meta_data[["match_id",  "match_date", "home_team", "away_team"]]
#get the unique home team name
# home_team_unique_statsbomb = statsbomb_meta_data["home_team"].unique()

#match the team name
dict={'UD Almería':'Almería', 'Real Sociedad':'Real Sociedad', 'Athletic Club de Bilbao':'Athletic Club', 'Villarreal CF':'Villarreal', 'RC Celta de Vigo':'Celta Vigo', 'Getafe CF':'Getafe', 'UD Las Palmas':'Las Palmas', 'Sevilla FC':'Sevilla', 'Cadiz CF':'Cádiz', 'Atlético Madrid':'Atlético Madrid', 'RCD Mallorca':'Mallorca', 'Valencia CF':'Valencia', 'CA Osasuna':'Osasuna', 'Girona FC':'Girona', 'Real Betis Balompié':'Real Betis', 'FC Barcelona':'Barcelona', 'Deportivo Alavés':'Deportivo Alavés', 'Granada CF':'Granada', 'Rayo Vallecano':'Rayo Vallecano', 'Real Madrid CF':'Real Madrid'}

#match the match_id based on the team name
matching_list = []
for i in range(len(skillcorner_df)):
    row=skillcorner_df.iloc[i]
    home_team = row["home_team"]
    away_team = row["away_team"]
    statsbomb_home_team = dict[home_team]
    statsbomb_away_team = dict[away_team]
    #get the row in statsbomb meta data
    matching_row = statsbomb_meta_data[(statsbomb_meta_data["home_team"]==statsbomb_home_team) & (statsbomb_meta_data["away_team"]==statsbomb_away_team)]
    if len(matching_row) == 0:
        print(f"Cannot find the match for {home_team} vs {away_team}")
        # pdb.set_trace()
    elif len(matching_row) == 1:
        matching_list.append([row["match_id"], row["time"], row["home_team"], row["home_team_short"], row["away_team"], row["away_team_short"], matching_row["match_id"].values[0], matching_row["match_date"].values[0], matching_row["home_team"].values[0], matching_row["away_team"].values[0]])

#convert the list to a dataframe
matching_df = pd.DataFrame(matching_list, columns=["match_id_skillcorner", "time_skillcorner", "home_team_skillcorner", "home_team_short_skillcorner", "away_team_skillcorner", "away_team_short_skillcorner", "match_id_statsbomb", "match_date_statsbomb", "home_team_statsbomb", "away_team_statsbomb"])
#reorder the columns so that the 2 match_id are next to each other
matching_df = matching_df[["match_id_skillcorner", "match_id_statsbomb", "time_skillcorner", "match_date_statsbomb", "home_team_skillcorner", "home_team_short_skillcorner", "home_team_statsbomb", "away_team_skillcorner", "away_team_short_skillcorner", "away_team_statsbomb"]]
#save the dataframe
matching_df.to_csv(save_dir, index=False)
pdb.set_trace()




