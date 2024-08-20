"""
Generating a PDF out of Tracab's Gateway output.
1. Fetch all relevant KPIs 
2. Manipulate KPIs into the correct format for the PDF
3. Generate the PDF
"""
import pandas as pd

from TracabModules.Internal.gateway import GatewayDownloader
import numpy as np

game_id = '2445451'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

downloader = GatewayDownloader(game_id, vendor_id, data_quality, extr_vers)
tf09_data, tf09_success = downloader.download_tf09_feed()
tf08_data, tf08_success = downloader.download_tf08_feed()


ft = tf08_data['Periods'][0]
firsthalf = tf08_data['Periods'][1]
secondhalf = tf08_data['Periods'][2]

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


"""
Physical Overview
"""
# Get players' names with an extra check for players with only a single name
physical_overview = {}
for team in ['HomeTeam', 'AwayTeam']:
    players = [
        f"{name_parts[0][0]}. {' '.join(name_parts[1:])}" if len(name_parts) > 1 else name_parts[0]
        for x in ft[team]['Players']
        if (name_parts := x['PlayerName'].split())
    ]

    total_distance = [x['Distance'] for x in ft[team]['Players']]
    top_speed = [x['TopSpeed'] for x in ft[team]['Players']]
    avg_speed = [x['AvgSpeed'] for x in ft[team]['Players']]
    n_sprints = [x['Sprints'] for x in ft[team]['Players']]
    n_speedruns = [x['SpeedRuns'] for x in ft[team]['Players']]
    n_hia = [x + y for x,y in zip(n_sprints,n_speedruns)]
    sprint_distance = [np.round(((x['PercentDistanceHighSpeedSprinting'] + x['PercentDistanceLowSpeedSprinting']) / 100 * x['Distance']),2) for x in ft[team]['Players']]
    speedrun_distance = [np.round((x['PercentDistanceHighSpeedRunning'] / 100 * x['Distance']),2) for x in ft[team]['Players']]
    lowspeedrun_distance = [np.round((x['PercentDistanceLowSpeedRunning'] / 100 * x['Distance']),2) for x in ft[team]['Players']]
    jogging_distance = [np.round((x['PercentDistanceJogging'] / 100 * x['Distance']),2) for x in ft[team]['Players']]
    walking_distance = [np.round((x['PercentDistanceWalking'] / 100 * x['Distance']),2) for x in ft[team]['Players']]
    standing_distance = [np.round((x['PercentDistanceStanding'] / 100 * x['Distance']),2) for x in ft[team]['Players']]

    df = pd.DataFrame({
        'Player Name': players,
        'Total Distance (m)': total_distance,
        'Top Speed (km/h)': top_speed,
        'Avg Speed (km/h)': avg_speed,
        'High Intensity Activity': n_hia,
        'Sprint Distance (m)': sprint_distance,
        'Num. Sprints': n_sprints,
        'HSR Distance (m)': speedrun_distance,
        'Num. HSR': n_speedruns,
        'LSR Distance (m)': lowspeedrun_distance,
        'Jogging Distance (m)': jogging_distance,
        'Walking Distance (m)': walking_distance,
        'Standing Distance (m)': standing_distance
    })
    df = df[df['Total Distance (m)'] != 0]
    physical_overview.update({team: df})

