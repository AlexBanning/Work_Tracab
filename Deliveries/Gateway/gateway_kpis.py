"""
The purpose of this code will be to calculate relevant KPIs from Tracab's Gateway output (dat-file + metadata).
Only needed for additional KPIs that are not already provided by the Gateway

"""

from floodlight.io.tracab import read_position_data_dat
from floodlight.models.kinematics import DistanceModel
import numpy as np

pos_data = read_position_data_dat(filepath_dat=r'C:\Users\alexa\Desktop\dat_file.dat',
                                  filepath_metadata=r'C:\Users\alexa\Desktop\metadata.json')

# Total Distance - Teams -----------------------------------------------------------------------------------------------
dm_home = DistanceModel()
dm_away = DistanceModel()

t_distance_team = {}
for segment in pos_data[0]:
    dm_home.fit(pos_data[0][segment]['Home'])
    t_dist_home = dm_home.cumulative_distance_covered()[-1]
    dm_away.fit(pos_data[0][segment]['Away'])
    t_dist_away = dm_away.cumulative_distance_covered()[-1]
    t_dist_segment = {segment: {'Home': int(np.sum(t_dist_home)) / 100, 'Away': int(np.sum(t_dist_away)) / 100}}
    t_distance_team.update(t_dist_segment)

total_distance_home = sum([t_distance_team['HT1']['Home'], t_distance_team['HT2']['Home']])
total_distance_away = sum([t_distance_team['HT1']['Away'], t_distance_team['HT2']['Away']])

# Total Distance - Players ---------------------------------------------------------------------------------------------

t_distance_players = {}
for segment in pos_data[0]:
    dm_home.fit(pos_data[0][segment]['Home'])
    t_dist_home = dm_home.cumulative_distance_covered()[-1]
    dm_away.fit(pos_data[0][segment]['Away'])
    t_dist_away = dm_away.cumulative_distance_covered()[-1]
    t_dist_segment = {segment: {'Home': t_dist_home, 'Away': t_dist_away}}
    t_distance_players.update(t_dist_segment)

t_dist_player_home = [int(sum([x, y])) / 100 for x, y in zip(
    t_distance_players['HT1']['Home'], t_distance_players['HT2']['Home']
)
                      ]
t_dist_player_away = [int(sum([x, y])) / 100 for x, y in zip(
    t_distance_players['HT1']['Away'], t_distance_players['HT2']['Away']
)
                      ]

# Max distance (player with the highest distance of each team) ---------------------------------------------------------
max_dist_home = max(t_dist_player_home)
xid_max_dist_home = t_dist_player_home.index(max_dist_home)
name_max_dist_home = pos_data[3]['Home'].teamsheet.loc[
    pos_data[3]['Home'].teamsheet['xID'] == xid_max_dist_home
]['player'].values[0]

max_dist_away = max(t_dist_player_away)
xid_max_dist_away = t_dist_player_away.index(max_dist_away)
name_max_dist_away = pos_data[3]['Away'].teamsheet.loc[
    pos_data[3]['Away'].teamsheet['xID'] == xid_max_dist_home
]['player'].values[0]

# Possession % ---------------------------------------------------------------------------------------------------------
possession = {}
for segment in pos_data[1]:
    half_pos = pos_data[1][segment]
    home_possession = [x for x in half_pos.code if x == 'H']
    away_possession = [x for x in half_pos.code if x == 'A']
    total_time = len(half_pos.code)
    prop_pos_home = np.round(len(home_possession) / total_time * 100, decimals=2)
    prop_pos_away = np.round(len(away_possession) / total_time * 100, decimals=2)
    pos_segment = {segment: {'Home': prop_pos_home, 'Away': prop_pos_away}}
    possession.update(pos_segment)

home_tot_pos = np.round(sum([possession['HT1']['Home'], possession['HT2']['Home']]) / 2, decimals=2)
away_tot_pos = np.round(sum([possession['HT1']['Away'], possession['HT2']['Away']]) / 2, decimals=2)

# Net playing time -----------------------------------------------------------------------------------------------------
ht1 = np.round(len([x for x in pos_data[2]['HT1'].code if x == 'A']) / 25 / 60, decimals=2)
ht2 = np.round(len([x for x in pos_data[2]['HT2'].code if x == 'A']) / 25 / 60, decimals=2)
total_playing_time = np.round(sum([len(pos_data[2]['HT1'].code), len(pos_data[2]['HT2'].code)]) / 25 / 60, decimals=2)

total_net = np.round(sum([ht1, ht2]) / total_playing_time * 100, decimals=2)
net_possession_time_home = np.round(total_net * (home_tot_pos / 100), decimals=2)
net_possession_time_away = np.round(total_net * (away_tot_pos / 100), decimals=2)
