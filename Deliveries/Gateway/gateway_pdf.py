"""
Generating a PDF out of Tracab's Gateway output.
1. Fetch all relevant KPIs 
2. Manipulate KPIs into the correct format for the PDF
3. Generate the PDF
"""
import pandas as pd
import json
from collections import Counter
from TracabModules.Internal.gateway import GatewayDownloader
import numpy as np

game_id = '2445451'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

downloader = GatewayDownloader(game_id, vendor_id, data_quality, extr_vers)
tf09_data, tf09_success = downloader.download_tf09_feed()
tf08_data, tf08_success = downloader.download_tf08_feed()
metadata, metadata_sucess = downloader.download_metadata_file()
metadata = metadata.json()

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
    home_net_possession_time_ft = np.round(ft[team]['PossessionData']['OwnTeamPossession']['Time'] / 1000 / 60,
                                           decimals=2)
    home_net_possession_time_firstht = np.round(
        firsthalf[team]['PossessionData']['OwnTeamPossession']['Time'] / 1000 / 60, decimals=2
    )
    home_net_possession_time_secondht = np.round(
        secondhalf[team]['PossessionData']['OwnTeamPossession']['Time'] / 1000 / 60, decimals=2
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
    team_values = [f'{home_possession}%', home_net_possession_time_ft, f'{home_dist}m', home_num_sprints,
                   home_num_hsruns,
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
    n_hia = [x + y for x, y in zip(n_sprints, n_speedruns)]
    sprint_distance = [np.round(
        ((x['PercentDistanceHighSpeedSprinting'] + x['PercentDistanceLowSpeedSprinting']) / 100 * x['Distance']), 2) for
        x in ft[team]['Players']]
    speedrun_distance = [np.round((x['PercentDistanceHighSpeedRunning'] / 100 * x['Distance']), 2) for x in
                         ft[team]['Players']]
    lowspeedrun_distance = [np.round((x['PercentDistanceLowSpeedRunning'] / 100 * x['Distance']), 2) for x in
                            ft[team]['Players']]
    jogging_distance = [np.round((x['PercentDistanceJogging'] / 100 * x['Distance']), 2) for x in ft[team]['Players']]
    walking_distance = [np.round((x['PercentDistanceWalking'] / 100 * x['Distance']), 2) for x in ft[team]['Players']]
    standing_distance = [np.round((x['PercentDistanceStanding'] / 100 * x['Distance']), 2) for x in ft[team]['Players']]

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

"""
Player Distance Charts
"""
distances = {}
for team in ['HomeTeam', 'AwayTeam']:
    players = [
        f"{name_parts[0][0]}. {' '.join(name_parts[1:])}" if len(name_parts) > 1 else name_parts[0]
        for x in ft[team]['Players']
        if (name_parts := x['PlayerName'].split())
    ]
    ft_total_distance = [x['Distance'] for x in ft[team]['Players']]
    fh_total_distance = [x['Distance'] for x in firsthalf[team]['Players']]
    sh_total_distance = [x['Distance'] for x in secondhalf[team]['Players']]

    team_dict = {x: {'firstHalf': f, 'secondHalf': s, 'fullTime': t} for x, f, s, t in
                 zip(players, fh_total_distance, sh_total_distance,
                     ft_total_distance)}
    distances.update({team: team_dict})

"""
Individual Possession Control --- Discuss necessety of implementation
"""
poss_control = {}


def calculate_average_control_time(player):
    sequences = [x for x in player['IndividualBallControlSequences'] if x['ControlType'] == 'PossessionControl']
    total_time = sum((x['EndFramecount'] - x['StartFramecount']) / 25 for x in sequences)
    count = len(sequences)
    return np.round(total_time / count, 2) if count > 0 else 0


def calculate_average_control_distance(player):
    sequences = [x for x in player['IndividualBallControlSequences'] if x['ControlType'] == 'PossessionControl']
    distance = np.round(sum((x['Distance'] for x in sequences)), 2)
    count = len(sequences)
    return np.round(distance / count, 2) if count > 0 else 0


for team in ['HomeTeam', 'AwayTeam']:
    players = [
        f"{name_parts[0][0]}. {' '.join(name_parts[1:])}" if len(name_parts) > 1 else name_parts[0]
        for x in ft[team]['Players']
        if (name_parts := x['PlayerName'].split())
    ]

    mins_played = [
        ((x['EndFrameCount'] - x['StartFrameCount']) -
         (metadata['Phase2StartFrame'] - metadata['Phase1EndFrame'])) / 25 / 60
        if (x['EndFrameCount'] >= metadata['Phase2StartFrame'] >= x['StartFrameCount'])
           and not (x['EndFrameCount'] == 0 and x[
            'StartFrameCount'] == 0)  # Additional check to prevent negative values
        else ((x['EndFrameCount'] - x['StartFrameCount']) / 25 / 60)
        for x in metadata[team]['Players']
    ]

    spc_count = [sum(1 for x in y['IndividualBallControlSequences'] if x['ControlType'] == 'SetPieceControl')
                 for y in tf09_data[team]['Players']]
    pc_count = [sum(1 for x in y['IndividualBallControlSequences'] if x['ControlType'] == 'PossessionControl')
                for y in tf09_data[team]['Players']]
    tc_count = [sum(1 for x in y['IndividualBallControlSequences'] if x['ControlType'] == 'TouchControl')
                for y in tf09_data[team]['Players']]

    pc_time = [
        sum((x['EndFramecount'] - x['StartFramecount']) / 25
            for x in y['IndividualBallControlSequences']
            if x['ControlType'] == 'PossessionControl')
        for y in tf09_data[team]['Players']
    ]

    pc_dist = [
        np.round(sum(x['Distance']
                     for x in y['IndividualBallControlSequences']
                     if x['ControlType'] == 'PossessionControl'), 2)
        for y in tf09_data[team]['Players']
    ]

    pc_avg_time = [calculate_average_control_time(y) for y in tf09_data[team]['Players']]
    pc_avg_dist = [calculate_average_control_distance(y) for y in tf09_data[team]['Players']]

    top_speed_pc = [
        np.round(max((x['TopSpeed']
                      for x in y['IndividualBallControlSequences']
                      if x['ControlType'] == 'PossessionControl'),
                     default=0), 2)  # Use default=0 to handle empty cases
        for y in tf09_data[team]['Players']
    ]

    team_dict = {x: {'mins_playerd': np.round(m, 2), 'SPC': s, 'TC': t, 'PC': p, 'Total PC': i, 'Avg PC': a,
                     'Total': d, 'Avg': v, 'Top Speed PC': k} for x, m, s, t, p, i, a, d, v, k in
                 zip(players, mins_played, spc_count, tc_count,
                     pc_count, pc_time, pc_avg_time, pc_dist, pc_avg_dist, top_speed_pc)}

    poss_control.update({team: team_dict})  ### Still missing all possession control related variables

"""
Summary: Ball Control
"""


def calculate_sprint_distance(possession_data):
    high_speed = possession_data.get('PercentDistanceHighSpeedSprinting', 0)
    low_speed = possession_data.get('PercentDistanceLowSpeedSprinting', 0)
    distance = possession_data.get('Distance', 0)
    return np.round((high_speed + low_speed) * distance / 100, 2)


ball_control_stats = {}
for team in ['HomeTeam', 'AwayTeam']:
    players = [
        f"{name_parts[0][0]}. {' '.join(name_parts[1:])}" if len(name_parts) > 1 else name_parts[0]
        for x in ft[team]['Players']
        if (name_parts := x['PlayerName'].split())
    ]

    mins_played = [
        ((x['EndFrameCount'] - x['StartFrameCount']) -
         (metadata['Phase2StartFrame'] - metadata['Phase1EndFrame'])) / 25 / 60
        if (x['EndFrameCount'] >= metadata['Phase2StartFrame'] >= x['StartFrameCount'])
           and not (x['EndFrameCount'] == 0 and x[
            'StartFrameCount'] == 0)  # Additional check to prevent negative values
        else ((x['EndFrameCount'] - x['StartFrameCount']) / 25 / 60)
        for x in metadata[team]['Players']
    ]

    own_dist = [x['PossessionData']['OwnTeamPossession']['Distance'] for x in ft[team]['Players']]
    opo_dist = [x['PossessionData']['OpponentPossession']['Distance'] for x in ft[team]['Players']]
    db_dist = [x['PossessionData']['DeadBall']['Distance'] for x in ft[team]['Players']]

    own_sprint_dist = [
        calculate_sprint_distance(x['PossessionData']['OwnTeamPossession'])
        for x in ft[team]['Players']
    ]
    opo_sprint_dist = [
        calculate_sprint_distance(x['PossessionData']['OpponentPossession'])
        for x in ft[team]['Players']
    ]
    db_sprint_dist = [
        calculate_sprint_distance(x['PossessionData']['DeadBall'])
        for x in ft[team]['Players']
    ]

    own_hsr_dist = [np.round(x['PossessionData']['OwnTeamPossession']['PercentDistanceHighSpeedRunning'] *
                             x['PossessionData']['OwnTeamPossession']['Distance'] / 100, 2)
                    for x in ft[team]['Players']]
    opo_hsr_dist = [np.round(x['PossessionData']['OpponentPossession']['PercentDistanceHighSpeedRunning'] *
                             x['PossessionData']['OpponentPossession']['Distance'] / 100, 2)
                    for x in ft[team]['Players']]
    db_hsr_dist = [np.round(x['PossessionData']['DeadBall']['PercentDistanceHighSpeedRunning'] *
                            x['PossessionData']['DeadBall']['Distance'] / 100, 2)
                   for x in ft[team]['Players']]

    own_hi_runs = [x['PossessionData']['OwnTeamPossession']['Sprints'] +
                   x['PossessionData']['OwnTeamPossession']['SpeedRuns']
                   for x in ft[team]['Players']]
    opo_hi_runs = [x['PossessionData']['OpponentPossession']['Sprints'] +
                   x['PossessionData']['OpponentPossession']['SpeedRuns']
                   for x in ft[team]['Players']]
    db_hi_runs = [x['PossessionData']['DeadBall']['Sprints'] +
                  x['PossessionData']['DeadBall']['SpeedRuns']
                  for x in ft[team]['Players']]

    team_dict = {x: {'mins_playerd': np.round(m, 2),
                     'Total dist': t, 'Sprint dist': s, 'HSR dist': h, 'High Int. Runs': i,
                     'Total dist Opo': ot, 'Sprint dist Opo': os, 'HSR dist Opo': oh, 'High Int. Runs Opo': oi,
                     'Total dist DB': dt, 'Sprint dist DB': ds, 'HSR dist DB': dh, 'High Int. Runs DB': di}
                 for x, m, t, s, h, i, ot, os, oh, oi, dt, ds, dh, di in
                 zip(players, mins_played, own_dist, own_sprint_dist, own_hsr_dist, own_hi_runs,
                     opo_dist, opo_sprint_dist, opo_hsr_dist, opo_hi_runs,
                     db_dist, db_sprint_dist, db_hsr_dist, db_hi_runs)}

    ball_control_stats.update({team: team_dict})

"""
Pass summary
"""

for team in ['HomeTeam', 'AwayTeam']:
    players = [
        f"{name_parts[0][0]}. {' '.join(name_parts[1:])}" if len(name_parts) > 1 else name_parts[0]
        for x in ft[team]['Players']
        if (name_parts := x['PlayerName'].split())
    ]

    passes_count = [
        np.round(sum(1
                     for x in y['SuccessfulPasses']), 2)
        for y in tf09_data[team]['Players']
    ]

    max_index, max_value = max(enumerate(passes_count),
                               key=lambda x: x[1])  # Only returns one value, what if several players with equal amount?
    most_passes_player = players[max_index]

    passes_count_total = sum(passes_count)

    pass_pressured_count = [
        np.round(sum(1
                     for x in y['SuccessfulPasses']
                     if x['ReleasePressure'] == 'HighPressure'), 2)
        for y in tf09_data[team]['Players']
    ]

    max_index_pressure, max_value_pressure = max(enumerate(pass_pressured_count), key=lambda x: x[
        1])  # Only returns one value, what if several players with equal amount?
    most_passes_pressure_player = players[max_index_pressure]

    pass_pressured_count_total = sum(pass_pressured_count)
    pass_pressured_perc = np.round(pass_pressured_count_total / passes_count_total * 100, 2)

    bypassed_count = [
        np.round(sum(x['BypassedPlayers']['Count']
                     for x in y['SuccessfulPasses']), 2)
        for y in tf09_data[team]['Players']
    ]
    bypassed_count_total = sum(bypassed_count)

    recipients = [
        Counter([x['ReceiveNumber']
                 for x in y['SuccessfulPasses']])
        for y in tf09_data[team]['Players']
    ]

    numbers = [
        x['JerseyNo']
        for x in metadata[team]['Players']
    ]

    pass_matrix = pd.DataFrame(0, index=numbers, columns=numbers)
    # Populate the DataFrame with counts from recipients_count
    for sender_idx, count in enumerate(recipients):
        sender_number = numbers[sender_idx]  # Get the sender's jersey number
        for receiver_number, cnt in count.items():
            pass_matrix.at[sender_number, receiver_number] = cnt  # Fill in the pass count

    # Display the resulting DataFrame
    print(pass_matrix)

    # Release/Receive Pressure from/in Location --- SKIPPED UNTIL ACTUAL INTEREST
    # Attacking 3rd:

"""
Passing Successful
"""
players = [
    f"{name_parts[0][0]}. {' '.join(name_parts[1:])}" if len(name_parts) > 1 else name_parts[0]
    for x in ft[team]['Players']
    if (name_parts := x['PlayerName'].split())
]

sp_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['FromSetPiece'] is True), 2)
    for y in tf09_data[team]['Players']
]
open_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['FromSetPiece'] is False), 2)
    for y in tf09_data[team]['Players']
]

off_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['Direction'] is 'Offensive'), 2)
    for y in tf09_data[team]['Players']
]

def_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['Direction'] is 'Defensive'), 2)
    for y in tf09_data[team]['Players']
]

byp_count = [
    np.round(sum(x['BypassedPlayers']['Count']
                 for x in y['SuccessfulPasses']), 2)
    for y in tf09_data[team]['Players']
]

high_press_rec_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['ReceiverPressure'] == 'HighPressure'), 2)
    for y in tf09_data[team]['Players']
]
low_press_rec_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['ReceiverPressure'] == 'LowPressure'), 2)
    for y in tf09_data[team]['Players']
]
no_press_rec_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['ReceiverPressure'] == 'NoPressure'), 2)
    for y in tf09_data[team]['Players']
]
high_press_rel_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['ReleasePressure'] == 'HighPressure'), 2)
    for y in tf09_data[team]['Players']
]
low_press_rel_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['ReleasePressure'] == 'LowPressure'), 2)
    for y in tf09_data[team]['Players']
]
no_press_rel_count = [
    np.round(sum(1
                 for x in y['SuccessfulPasses'] if x['ReleasePressure'] == 'NoPressure'), 2)
    for y in tf09_data[team]['Players']
]

