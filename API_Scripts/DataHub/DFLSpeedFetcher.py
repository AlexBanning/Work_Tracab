import pandas as pd
from TracabModules.External.DataHub import DataHub
from TracabModules.Internal.tools import push_df_to_google

matchday = input('Which was the last 1. Bundesliga matchday?')
bl2_matchday = input('Which was the last 2. Bundesliga matchday?')

leagues = {'1. Bundesliga': '51',
           '2. Bundesliga': '52'}


for league, league_id in leagues.items():
    if league_id == '51':
        matchday = matchday
    elif league_id == '52':
        matchday = bl2_matchday
    datahub_download = DataHub()
    season_id = datahub_download.season_id()
    comp_id = datahub_download.sts_competition_id(tracab_id=league_id)
    matchday_ids = datahub_download.matchday_ids(season_id, comp_id)
    speeds = datahub_download.positionalfeed(season_id, comp_id, matchday_ids[matchday]['MatchDayId'])

    speeds_df = pd.DataFrame(
        [{'ObjectId': x['PlayerId'],
          'Name': f"{x['PlayerAlias']}" if 'PlayerAlias' in x.attrs else f"{x['PlayerFirstName'][0]}. {x['PlayerLastName']}",
          'Speed': x['Absolute'],
          'Team': x.contents[1]['TeamName']}
         for x in speeds.find_all('ListEntry') if x.contents[1]['TeamName']]
    )

    speeds_df = (
        speeds_df
        .reset_index(drop=False)  # Reset index and add it as a column
        .drop(columns=['ObjectId'])  # Drop the 'ObjectId' column
        .rename(columns={'index': 'Rank'})  # Rename 'index' column to 'Rank'
    )

    # Adjust the 'Rank' values to start from 1
    speeds_df['Rank'] += 1
    # speeds_df.to_csv('speeds_BL2.csv')

    push_df_to_google(df=speeds_df, spreadsheet_id='1W32cZHg2cmLdMSGDXSfNGrb-68BC6mHjCIJK0Sr40k4',
                      worksheet=league)



# https://httpget.distribution.production.datahub-sts.de/DeliveryPlatform/REST/PullOnce/ChyronHego-2fac-9065-53ed/DFL-07.03.01-Ranglisten-Saison_Spieler_Positionsdaten/DFL-SEA-0001K8_DFL-COM-000001_DFL-DAY-004C69