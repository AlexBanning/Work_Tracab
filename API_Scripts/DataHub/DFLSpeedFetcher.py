import pandas as pd
from TracabModules.External.DataHub import DataHub


datahub_download = DataHub()
season_id = datahub_download.season_id()
comp_id = datahub_download.sts_competition_id(tracab_id='51')
matchday_ids = datahub_download.matchday_ids(season_id, comp_id)
speeds = datahub_download.positionalfeed(season_id, comp_id, matchday_ids['31'])

speeds_df = pd.DataFrame(
    [{'Name': f"{x['PlayerAlias']}" if 'PlayerAlias' in x.attrs else f"{x['PlayerFirstName'][0]}. {x['PlayerLastName']}",
      'Speed': x['Absolute'],
      'Team': x.contents[1]['TeamName']}
     for x in speeds.find_all('ListEntry') if x.contents[1]['TeamName']]
)

speeds_df.to_csv('speeds_BL2.csv')
