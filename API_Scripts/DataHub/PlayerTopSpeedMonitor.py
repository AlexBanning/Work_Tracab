import pandas as pd
from TracabModules.External.DataHub import DataHub, SpeedWindowGUI

datahub_download = DataHub()
season_id = datahub_download.season_id()
comp_id = datahub_download.sts_competition_id(tracab_id='51')
matchday_ids = datahub_download.matchday_ids(season_id, comp_id)
speeds = datahub_download.speeds(season_id, comp_id, matchday_ids['30'])

home = 'TSG Hoffenheim'
speeds_home = pd.DataFrame(
    list({f'{x['PlayerFirstName'][0]}. {x['PlayerLastName']}': x['Absolute'] for x in speeds.find_all('ListEntry')
          if x.contents[1]['TeamName'] == home}.items()), columns=['Name', 'Speed']
)

away = 'RB Leipzig'
speeds_away = pd.DataFrame(
    list({f'{x['PlayerFirstName'][0]}. {x['PlayerLastName']}': x['Absolute'] for x in speeds.find_all('ListEntry')
          if x.contents[1]['TeamName'] == away}.items()), columns=['Name', 'Speed']
)

app = SpeedWindowGUI()