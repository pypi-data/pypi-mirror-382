import pandas as pd
from preprocessing import Event_data

event_path = '/data_pool_1/FIFA_WC_2022/Event Data'

# Load and process soccer data
soccertrack_df = Event_data('pff_fc',event_path).load_data()
print(soccertrack_df.head())