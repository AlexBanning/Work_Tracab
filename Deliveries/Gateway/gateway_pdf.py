"""
Generating a PDF out of Tracab's Gateway output.
1. Fetch all relevant KPIs 
2. Manipulate KPIs into the correct format for the PDF
3. Generate the PDF
"""
import pandas as pd

from TracabModules.Internal.gateway import download_tf08_feed, download_tf09_feed
import numpy as np

game_id = '2374222'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

tf09_data = download_tf09_feed(game_id, vendor_id, data_quality, extr_vers)
tf08_data = download_tf08_feed(game_id, vendor_id, data_quality, extr_vers)


ft = tf08_data[0]['Periods'][0]
firsthalf = tf08_data[0]['Periods'][1]
secondhalf = tf08_data[0]['Periods'][2]

# Get all KPIs for the PDFs frontpage
pdf_frontpage = pd.DataFrame(columns=["HomeTeam", "KPIs", "AwayTeam"])
pdf_frontpage['KPIs'] = ['POSSESSION', 'NET. POSS. TIME', 'DISTANCE', 'SPRINTS', 'HIGH SPEED RUNS',
                         'SPRINT DISTANCE', 'TOP SPEED', 'MAX DISTANCE', 'MAX SPRINTS']
for team in ['HomeTeam', 'AwayTeam']:
    home_dist = np.round(ft[team]['Distance'] / 10, decimals=2)
    home_possession = ft[team]['PossessionData']['PossessionPercentage']
    home_net_possession_time_ft = np.round(ft[team]['PossessionData']['OwnTeamPossession']['Time'] / 1000 / 60, decimals=2)
    home_net_possession_time_firstht = np.round(
        firsthalf[team]['PossessionData']['OwnTeamPossession']['Time'] / 1000 / 60,decimals=2
                                                )
    home_net_possession_time_secondht = np.round(
        secondhalf[team]['PossessionData']['OwnTeamPossession']['Time'] / 1000 / 60,decimals=2
                                                )

    home_players = ft[team]['Players']
    home_num_sprints = np.sum([x['Sprints'] for x in home_players])
    home_num_hsruns = np.sum([x['SpeedRuns'] for x in home_players])
    home_sprint_dist = np.sum(
        [np.round(
            np.sum(
                [y['Distance'] for y in x['Coordinates'] if y['Type'] == 'Sprint']),
            decimals=2
                  ) for x in home_players]
    )
    home_top_speed = [x['TopSpeed'] for x in home_players]
    home_max_distance = [x['Distance'] for x in home_players]
    home_max_num_sprints = [x['Sprints'] for x in home_players]
    home_names = [x['PlayerName'] for x in home_players]

    top_speed_home_players = max(home_top_speed)
    top_speed_home_players_name = home_names[home_top_speed.index(max(home_top_speed))]

    max_distance_home_players = max(home_max_distance)
    max_distance_home_players_name = home_names[home_max_distance.index(max(home_max_distance))]

    max_num_sprints_home_players = max(home_max_num_sprints)
    max_num_sprints_home_players_name = home_names[home_max_num_sprints.index(max(home_max_num_sprints))]
    team_values = [f'{home_possession}%', home_net_possession_time_ft, f'{home_dist}m', home_num_sprints, home_num_hsruns,
                   f'{home_sprint_dist}m', f'{top_speed_home_players_name} ({top_speed_home_players}km/h)',
                   f'{max_distance_home_players_name} ({max_distance_home_players}m)',
                   f'{max_num_sprints_home_players_name} ({max_num_sprints_home_players})']

    pdf_frontpage[team] = team_values


