# from skillcorner.client import SkillcornerClient
from event_synchronization import events
from event_synchronization.matcher import get_freeze_frames
from event_synchronization.utils import get_period_to_home_team_attacking_direction

MATCH_ID = 707007

# skc_client = SkillcornerClient()

# match_data_wyscout_matching = skc_client.get_match(MATCH_ID, params={'matching': 'wyscout'})