import sqlite3 as sql
import pandas as pd
from TracabModules.External.DataHub import DataHub
from TracabModules.Internal.tools import is_date_in_current_week


datahub_download = DataHub()
season_id = datahub_download.season_id()
data = pd.DataFrame(columns=['League', 'Team', 'Name', 'Speed'])
for league in ['51', '52']:
    comp_id = datahub_download.sts_competition_id(tracab_id=league)
    matchday_ids = datahub_download.matchday_ids(season_id, comp_id)
    current_md = matchday_ids[str(int([x for x in matchday_ids  if is_date_in_current_week(matchday_ids[x]['Date'])][0])-1)]['MatchDayId']
    speeds = datahub_download.positionalfeed(season_id, comp_id, current_md)

    speeds_df = pd.DataFrame(
        [{'Name': f"{x['PlayerAlias']}" if 'PlayerAlias' in x.attrs else f"{x['PlayerFirstName'][0]}. {x['PlayerLastName']}",
          'Speed': x['Absolute'],
          'Team': x.contents[1]['TeamName']}
         for x in speeds.find_all('ListEntry') if x.contents[1]['TeamName']]
    )
    if league == '51':
        speeds_df['League'] = '1.Bundesliga'
    elif league == '52':
        speeds_df['League'] = '2.Bundesliga'
    data = pd.concat([data, speeds_df], axis=0).drop(columns=speeds_df.columns[[0]])

# Connect to DB
conn = sql.connect(r'N:\07_QC\Alex\DFLPlayerDatabase.db')

# Create or Update DB
data.to_sql('DFLPlayerStats', conn, if_exists='replace', index=False)


