"""
Goal of this code is to calculate new metrics out of the gateway output (Dat-File)
- Defending Space

- ‘Avg player velocity’

- Space/Pitch  control

- Group centroids

- Team Density

- Distance to closest opponent

- Avg. Ball x,y Speed in/out possession phases
"""
from TracabModules.Internal.gateway import GatewayDownloader
import json
from floodlight.io.tracab import read_position_data_dat

# Define match parameters
game_id = '2374219'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

downloader = GatewayDownloader(game_id, vendor_id, data_quality, extr_vers)
dat_response, dat_success = downloader.download_binary_feed()
metadata_response, metadata_success = downloader.download_metadata_file()

dat_text = dat_response.text
with open(r'C:\Users\a.banning\Desktop\dat_file.dat', 'w', encoding='utf-8') as f:
    f.write(dat_text)
    f.close()

with open(r'C:\Users\a.banning\Desktop\metadata.json', 'w') as f:
    json.dump(metadata_response.json(), f)

pos_data = read_position_data_dat(filepath_dat=r'C:\Users\a.banning\Downloads\dat_file.dat',
                                  filepath_metadata=r'C:\Users\a.banning\Downloads\metadata_file.json')

"""
Create Sub_Groups dictionaries
"""

with open(r'C:\Users\a.banning\Downloads\metadata_file.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sub_groups = {'Home': {'GK': [], 'DEF': [], 'MID': [], 'ATT': []},
              'Away': {'GK': [], 'DEF': [], 'MID': [], 'ATT': []}}

for team in ['Home', 'Away']:
    gk_ids = [player['PlayerID'] for player in data[f'{team}Team']['Players'] if player['StartingPosition'] == 'G' or
              player['CurrentPosition'] == 'G']
    def_ids = [player['PlayerID'] for player in data[f'{team}Team']['Players'] if player['StartingPosition'] == 'D' or
              player['CurrentPosition'] == 'D']
    mid_ids = [player['PlayerID'] for player in data[f'{team}Team']['Players'] if player['StartingPosition'] == 'M' or
              player['CurrentPosition'] == 'M']
    att_ids = [player['PlayerID'] for player in data[f'{team}Team']['Players'] if player['StartingPosition'] == 'A' or
                   player['CurrentPosition'] == 'A']

    # Adding player IDs to Home team
    sub_groups[team]['GK'].extend(gk_ids)
    sub_groups[team]['DEF'].extend(def_ids)
    sub_groups[team]['MID'].extend(mid_ids)
    sub_groups[team]['ATT'].extend(att_ids)

"""
Calculate team centroids and stretch index
"""
from floodlight.models.geometry import CentroidModel
import numpy as np
cm = CentroidModel()

# Initialize centroids and stretch_index dictionaries with nested dictionaries
centroids = {'Home': {'HT1': {'x': 0.0, 'y': 0.0}, 'HT2': {'x': 0.0, 'y': 0.0}},
             'Away': {'HT1': {'x': 0.0, 'y': 0.0}, 'HT2': {'x': 0.0, 'y': 0.0}}}

stretch_index = {'Home': {'HT1': 0.0, 'HT2': 0.0},
                 'Away': {'HT1': 0.0, 'HT2': 0.0}}
for team in ['Home', 'Away']:
    for half in pos_data[0]:
        data = pos_data[0][half][team]
        cm.fit(data)
        centroid_x = cm.centroid().x.mean() / 100
        centroid_y = cm.centroid().y.mean() / 100
        si = np.round(np.mean(cm.stretch_index(data)) / 100,2)
        stretch_index[team][half] = si
        centroids[team][half]['x'] = np.round(centroid_x,2)
        centroids[team][half]['y'] = np.round(centroid_y,2)

"""
Calculate players acceleration
"""
from floodlight.models.kinematics import AccelerationModel
am = AccelerationModel()

accs = []
for team in ['Home', 'Away']:
    for half in pos_data[0]:
        data = pos_data[0]['HT1']['Home']
        am.fit(data)

        accs.append(am.acceleration())

"""
Calculate Pitch Control
"""
import numpy as np
from floodlight import XY, Pitch
from floodlight.models.space import DiscreteVoronoiModel
pitch = Pitch.from_template("tracab", length=105, width=68, sport='football')
dvm = DiscreteVoronoiModel(pitch)
dvm.fit(pos_data[0]['HT1']['Home'], pos_data[0]['HT1']['Away'])

pitch_control = dvm.team_controls()
home_control = np.round(np.mean(pitch_control[0]),2)
away_control = np.round(np.mean(pitch_control[1]),2)

fitted_dvm_model = dvm.fit(pos_data[0]['HT1']['Home'], pos_data[0]['HT1']['Away'])
ax = pitch.plot(color_scheme="bw")
fitted_dvm_model.plot(ax=ax)


import time
from floodlight.models.geometry import CentroidModel
from floodlight.models.kinematics import DistanceModel, VelocityModel
from floodlight.io.dfl import create_links_from_mat_info
from scipy.spatial import Voronoi, ConvexHull, distance
from floodlight import XY
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import basic_functions as bf
import copy
import warnings


def group_centroids(position_data, sub_groups, positions):
    """
    Calculation of the centroid for each position-group and both teams in both half-times

    Parameters
    ----------
    position_data: Floodlight XY-Object
        XY-Object containing the position data of the team and half of interest
    sub_groups: Dict in Dict
        Dictionary containing two dicts (one for each team) with the team's position groups' dicts in which the xIDs
        of the players for each position group are in

    positions: Dict in Dict
        Dictionary containing the position groups (Attack, Defense, Midfield, Goalkeeper) and their belonging positions
        in abbreviated form

    Returns
    -------
        group_centroids: Dict: {0: {}, 1: {}, 2 = {}, 3 = {}}
        Dictionaries containing the centroids of the position groups for both halfs and both teams
        0: Home HT1, 1: Home HT2, 2: Away HT1, 3: Away HT2
    """

    # Dict where the player-dicts for both teams are stored in
    group_centroids = {0: {}, 1: {}, 2: {},
                       3: {}}  # Dict, in which group-centroids will be stored(0: Home, HT1, 1: Home, HT2...)

    for h, data in enumerate(position_data[:4]):  # IF goes through loop, malignant centroids are calculated,
        if h <= 1:  # manual calculation works
            t = 0
        else:
            t = 1
        # 3. Create XY-Objects for the sub-groups of both teams
        group_data = {}  # Dict, in which the np.arrays for all  players of a position group are stored in
        for pos in positions:
            arr = np.empty((len(data), 2))
            for j in sub_groups[t][pos]:
                xy = data.player(j)
                arr = np.concatenate((arr, xy), axis=1)
                dat = arr[:, 2:]
            group_data.update({pos: dat})

        # 4. Calculate individual centroids for each sub-group
        sub_group_centroids = {}
        for pos in positions:
            if pos != "Goalkeeper":
                cm = CentroidModel()
                cm.fit(XY(group_data[pos]))
                centroid = cm.centroid()
                sub_group_centroids.update({pos + "Centroid": abs(np.round(np.nanmean(centroid, axis=0)[0], 2))})
                # abs value so every team "plays" from left to right
            else:
                pass
        group_centroids.update({h: sub_group_centroids})

    return group_centroids


def stretch_index(position_data):
    """
    Calculation of the stretch-index (mean distance of all players to the team centroid) for both teams in both
    half-times

    Parameters
    ----------
    position_data: Floodlight XY-Object
        XY-Object containing the position data of both teams and both halfs

    Returns
    -------
    team_stretch: Dict: {0: {}, 1: {}, 2: {}, 3: {}}
            Dictionaries containing the stretch indices for both teams and halfs
            0: Home HT1, 1: Home HT2, 2: Away HT1, 3: Away HT2
    """

    team_stretch = {0: {}, 1: {}, 2: {}, 3: {}}
    for j, dat in enumerate(position_data[:4]):
        cm = CentroidModel()
        cm.fit(dat, exclude_xIDs=([0]))
        team_stretch.update({j: np.round(np.nanmean(cm.stretch_index(dat)), 2)})
    return team_stretch


def def_space(match_id, player_IDs, position_data, events):
    """
    Calculating the space (distance) between the last defender and own goal line as percentage of the whole pitch

    Parameters
    ----------
    match_id:
    player_IDs:
    position_data:
    events:


    Returns
    -------
    space: Dict in Dict[0: {}, 1: {}, 2: {}, 3: {}]
        Dictionary containing the mean amount of space between last defender and goal line for both halfs and teams in the
        following order: 1: Home HT1, 2: Home HT2, 3: Away HT1, 4: Away HT2

    """

    # 1.) Go through defender-list of team
    sub_groups, _ = bf.get_sub_groups(match_id, player_IDs)
    # 2.) Check which defender is last
    # Get defense_xy_data
    def_data = {}
    for h, data in enumerate(position_data[:4]):  # IF goes through loop, malignant centroids are calculated,
        if h <= 1:  # manual calculation works
            t = 0
        else:
            t = 1
        # 3. Create XY-Objects for the sub-groups of both teams
        group_data = {}
        arr = np.empty(
            (len(data), 2))  # Dict, in which the np.arrays for all  players of a position group are stored in
        for j in sub_groups[t]["Defense"]:
            xy = data.player(j)
            arr = np.concatenate((arr, xy), axis=1)
            dat = arr[:, 2:]
        group_data.update({h: dat})
        def_data.update({h: group_data})
    # Find out which defender is last in each frame, playing direction is needed
    min_x = {}
    for i in def_data:
        if i == 0 or i == 1:
            if events[i].direction == "rl":
                dist = [(position_data[10].length / 2) - abs(np.nanmax(frame[::2])) for frame in def_data[i][i]]
            elif events[i].direction == "lr":
                dist = [(position_data[10].length / 2) - abs(np.nanmin(frame[::2])) for frame in def_data[i][i]]
        else:
            if events[i].direction == "rl":
                dist = [(position_data[10].length / 2) - abs(np.nanmin(frame[::2])) for frame in def_data[i][i]]
            elif events[i].direction == "lr":
                dist = [(position_data[10].length / 2) - abs(np.nanmax(frame[::2])) for frame in def_data[i][i]]
        min_x.update({i: dist})
    # 3.) Calculate space % (to whole pitch) behind this defender
    space = {}
    for i in min_x:
        s = [(frame / position_data[10].length) * 100 for frame in min_x[i]]
        # percentage = (frame / position_data[10].length) * 100
        # s.append(np.round(percentage, 2))
        space.update({i: np.round(np.nanmean(s), 2)})

    return space


def length_width_ratio(position_data, info_path):
    """
    Calculation of the length/width-ratio of the teams in possession and out of possession for both halfes
    Parameters
    ----------
    position_data: Floodlight XY-Object
        XY-Object containing the position data of both teams and both halfs
    info_path: str or pathlib.Path
        Full path to XML File where the Match Information data in DFL format is saved
    Returns
    -------
    lw_ratio: List [lw0, lw1, lw2, lw3]
        Dictionary containing the length/width-ratio for both half-times and teams in the
        following order: lw0: Home HT1, lw1: Home HT2, lw2: Away HT1, lw3: Away HT2
    oppo_lw_ratio: List [oppo_lw0, oppo_lw1, oppo_lw2, oppo_lw3]
        Dictionary containing the length/width-ratio for both half-times and teams in the
        following order: oppo_lw0: AwayHT1, oppo_lw1: AwayHT2, oppo_lw2: HomeHT1, oppo_lw3: HomeHT2
    """
    possessions_one = position_data[6].find_sequences()
    possessions_two = position_data[7].find_sequences()

    # Get xIDs for Goalkeepers to exclude them
    player_positions = bf.player_positions(info_path)
    player_IDs = create_links_from_mat_info(info_path)
    gk_xID = {}
    for j in ["Home", "Away"]:
        gk = [x[0] for x in player_positions[j].items() if x[1] == "TW"]
        jID = [x[1] for x in player_IDs[1][j].items() for y in gk if x[0] == y]
        xID = [x[1] for x in player_IDs[0][j].items() for y in jID if x[0] == y]
        gk_xID.update({j: xID})

    teams_length = {}
    teams_width = {}
    oppo_teams_length = {}
    oppo_teams_width = {}
    for n, dat in enumerate(position_data[:4]):
        if n == 0:
            team = "Home"
            oppo_team = "Away"
            oppo_dat = position_data[2]
            possessions = possessions_one[1]
        elif n == 1:
            team = "Home"
            oppo_team = "Away"
            oppo_dat = position_data[3]
            possessions = possessions_two[1]
        elif n == 2:
            team = "Away"
            oppo_team = "Home"
            oppo_dat = position_data[0]
            possessions = possessions_one[2]
        elif n == 3:
            team = "Away"
            oppo_team = "Home"
            oppo_dat = position_data[1]
            possessions = possessions_two[2]
        # Exclude Goalkeepers for team in possession
        include = np.full((dat.N * 2), True)
        for g in gk_xID[team]:
            exclude_start = g * 2
            exclude_end = exclude_start + 2
            include[exclude_start:exclude_end] = False
        n_team = XY(dat.xy[:, include])
        # Exclude Goalkeepers for team in possession
        include_oppo = np.full((oppo_dat.N * 2), True)
        for g in gk_xID[oppo_team]:
            exclude_start = g * 2
            exclude_end = exclude_start + 2
            include_oppo[exclude_start:exclude_end] = False
        n_oppo_team = XY(oppo_dat.xy[:, include_oppo])
        start = [pos[0] for pos in possessions]
        end = [pos[1] for pos in possessions]
        sequences = list(np.column_stack((start, end)))
        sequences = [x for x in sequences if len(range(x[0], x[1])) >= 75]
        # Length and Width for team in possession
        frame_x = [n_team[start:end][:, ::2] for start, end in sequences]
        frame_y = [n_team[start:end][:, 1::2] for start, end in sequences]
        # Calculate Team-Width
        y_min = [np.nanmin(y) for f in frame_y for y in f]
        y_max = [np.nanmax(y) for f in frame_y for y in f]
        # y_max = [np.nanmax(y) for y in n_team.y]
        widths = [abs(y_max[j] - y_min[j]) for j in range(0, len(y_min))]
        # Calculate Team-Length
        x_min = [np.nanmin(x) for f in frame_x for x in f]
        x_max = [np.nanmax(x) for f in frame_x for x in f]
        lengths = [abs(x_max[k] - x_min[k]) for k in range(0, len(x_min))]

        teams_length.update({n: np.round(np.nanmean(lengths), 2)})
        teams_width.update({n: np.round(np.nanmean(widths), 2)})

        # Length and Width for team in out of possession
        oppo_frame_x = [n_oppo_team[start:end][:, ::2] for start, end in sequences]
        oppo_frame_y = [n_oppo_team[start:end][:, 1::2] for start, end in sequences]
        # Calculate Team-Width
        oppo_y_min = [np.nanmin(y) for f in oppo_frame_y for y in f]
        oppo_y_max = [np.nanmax(y) for f in oppo_frame_y for y in f]
        # y_max = [np.nanmax(y) for y in n_team.y]
        oppo_widths = [abs(oppo_y_max[j] - oppo_y_min[j]) for j in range(0, len(oppo_y_min))]
        # Calculate Team-Length
        oppo_x_min = [np.nanmin(x) for f in oppo_frame_x for x in f]
        oppo_x_max = [np.nanmax(x) for f in oppo_frame_x for x in f]
        oppo_lengths = [abs(oppo_x_max[k] - oppo_x_min[k]) for k in range(0, len(oppo_x_min))]

        oppo_teams_length.update({n: np.round(np.nanmean(oppo_lengths), 2)})
        oppo_teams_width.update({n: np.round(np.nanmean(oppo_widths), 2)})

    # Length per Width ratio
    lw_ratio = [np.round(teams_length[i] / teams_width[i], 2) for i in range(0, len(teams_length))]
    oppo_lw_ratio = [np.round(oppo_teams_length[i] / oppo_teams_width[i], 2) for i in range(0, len(oppo_teams_length))]

    return lw_ratio, oppo_lw_ratio


def possession_areas(position_data, events):
    """
    Calculation of the amount of possession in defined pitch locations (def, mid, att third; l_wide, central, r_wide)
    Parameters
    ----------
    position_data: Floodlight XY-Objects
        XY-Objects containing the position data of both teams and both halfs
    events

    Returns
    -------
    pos_thirds: Dict in Dict [0= {0: %0, 1: %1, 2: %2},
                              1= {0: %0, 1: %1, 2: %2},
                              2= {0: %0, 1: %1, 2: %2},
                              3= {0: %0, 1: %1, 2: %2}]
        Dictionary for both half-times and teams in the following order: 1: Home HT1, 2: Home HT2, 3: Away HT1, 4: Away HT2
        containing dictionaries with the % of possession in the defined locations  in the following order:
        0: Defensive Third, 1: Middle Third, 2: Attacking Third
    pos_area: Dict in Dict [0= {0: %0, 1: %1, 2: %2},
                          1= {0: %0, 1: %1, 2: %2},
                          2= {0: %0, 1: %1, 2: %2},
                          3= {0: %0, 1: %1, 2: %2}]
        Dictionary for both half-times and teams in the following order: 1: Home HT1, 2: Home HT2, 3: Away HT1, 4: Away HT2
        containing dictionaries with the % of possession in the defined locations  in the following order:
        0: Left-wide area, 1: Central area, 2: Right-wide area

    """

    pos_third = {}
    pos_area = {}
    for i, team in enumerate(position_data[:4]):
        possession_third = []
        if i == 0:
            pos_sequences = position_data[6].find_sequences(return_type="dict")[1.0]
            ball_data = position_data[4]
        elif i == 1:
            pos_sequences = position_data[7].find_sequences(return_type="dict")[1.0]
            ball_data = position_data[5]
        elif i == 2:
            pos_sequences = position_data[6].find_sequences(return_type="dict")[2.0]
            ball_data = position_data[4]
        elif i == 3:
            pos_sequences = position_data[7].find_sequences(return_type="dict")[2.0]
            ball_data = position_data[5]

        ball_positions = {}
        for j, seq in enumerate(pos_sequences):
            new_dat = ball_data.slice(startframe=seq[0], endframe=seq[1])
            ball_positions.update({j: new_dat})

        if events[i].direction == "rl":
            # Attacking third: -52.5 to -17.5, Middle third: -17.5 to 17.5, Defending third: 17.5 to 52.5
            for frame in ball_positions:
                for f in ball_positions[frame]:
                    if f[0] >= 17.5:
                        possession_third.append(0)
                    elif -17.5 <= f[0] <= 17.5:
                        possession_third.append(1)
                    elif f[0] <= -17.5:
                        possession_third.append(2)

        if events[i].direction == "lr":
            # Defending third: -52.5 to -17.5, Middle third: -17.5 to 17.5, Attacking third: 17.5 to 52.5
            for frame in ball_positions:
                for f in ball_positions[frame]:
                    if f[0] >= 17.5:
                        possession_third.append(2)
                    elif -17.5 <= f[0] <= 17.5:
                        possession_third.append(1)
                    elif f[0] <= -17.5:
                        possession_third.append(0)

        possession_thirds = {0: np.round(possession_third.count(0) / len(possession_third), 4) * 100,
                             1: np.round(possession_third.count(1) / len(possession_third), 4) * 100,
                             2: np.round(possession_third.count(2) / len(possession_third), 4) * 100
                             }

        possession_area = []
        # Possession central or wide areas
        if events[i].direction == "rl":
            # Left-wide area: -34 to -17, Central area: -17 to 17, Right-wide area: 17 to 34
            for frame in ball_positions:
                for f in ball_positions[frame]:
                    if f[1] <= -17:
                        possession_area.append(0)
                    elif -17 <= f[1] <= 17:
                        possession_area.append(1)
                    elif f[1] >= 17:
                        possession_area.append(2)

        if events[i].direction == "lr":
            # Left-wide area: 34 to 17, Central area: 17 to -17, Right-wide area: -17 to -34
            for frame in ball_positions:
                for f in ball_positions[frame]:
                    if f[1] >= 17:
                        possession_area.append(0)
                    elif 17 <= f[1] >= -17:
                        possession_area.append(1)
                    elif f[1] <= -17:
                        possession_area.append(2)

        pitch_area = {0: np.round(possession_area.count(0) / len(possession_area), 4) * 100,
                      1: np.round(possession_area.count(1) / len(possession_area), 2) * 100,
                      2: np.round(possession_area.count(2) / len(possession_area), 4) * 100
                      }

        pos_third.update({i: possession_thirds})
        pos_area.update({i: pitch_area})

    differences = {}
    for i in pos_third:
        dict = {}
        if i == 0:
            for n in pos_third[i]:
                dict.update({n: np.round(pos_third[i][n] - pos_third[2][n], 2)})
        if i == 1:
            for n in pos_third[i]:
                dict.update({n: np.round(pos_third[i][n] - pos_third[3][n])})
        if i == 2:
            for n in pos_third[i]:
                dict.update({n: np.round(pos_third[i][n] - pos_third[0][n], 2)})
        if i == 3:
            for n in pos_third[i]:
                dict.update({n: np.round(pos_third[i][n] - pos_third[1][n], 2)})
        differences.update({i: dict})

    return pos_third, pos_area, differences


# Voronoi_Cells Area
def voronoi_area(extended_points):
    vor = Voronoi(extended_points)
    area = np.zeros(22)
    for i, reg_num in enumerate(vor.point_region[0:22]):
        indices = vor.regions[reg_num]
        area[i] = ConvexHull(vor.vertices[indices]).volume

    return area


def space_control(position_data):
    """
    Calculation of mean space control for both teams in their possession sequences that take up more than 3s
    Parameters.
    ----------
    position_data: Floodlight XY-Objects
        XY-Objects containing the position data of both teams and both half-times

    Returns
    -------
    space_control: Dict[0: sc0, 1:sc1, 2:sc2, 3:sc3]
        Dictionary containing the mean space control of each team in their possession sequences (>3s) for both
        half-times.
        sc0: HomeHT1, sc2: HomeHT2, sc2: AwayHT1, sc3: AwayHT2

    """
    # t = time.time()
    # Only in ball possession:
    possessions_one = position_data[6].find_sequences()
    possessions_two = position_data[7].find_sequences()

    space_control = {}
    for j in range(0, 4):
        sc = []
        if j == 0:
            possessions = possessions_one[1]
            away = 2
        elif j == 1:
            possessions = possessions_two[1]
        elif j == 2:
            possessions = possessions_one[2]
        elif j == 3:
            possessions = possessions_two[2]
        for pos in possessions:
            start = pos[0]
            end = pos[1]
            sequence = range(start, end)
            if len(sequence) <= 75:
                pass
            else:
                # print(np.round(time.time() - t, 3), "s of pos start")
                pos_sc = []
                for n, frame in enumerate(position_data[j][start:end]):
                    if j == 0:
                        frame_oppo = position_data[2][sequence[n]]
                    if j == 1:
                        frame_oppo = position_data[3][sequence[n]]
                    if j == 2:
                        frame_oppo = position_data[0][sequence[n]]
                    if j == 3:
                        frame_oppo = position_data[1][sequence[n]]

                    # Manipulate data to get points
                    home_y = [np.round(i, 2) for i in frame[1::2]]
                    home_x = [np.round(i, 2) for i in frame[::2]]
                    home = list(np.zeros((len(home_y),), dtype=int))

                    away_y = [np.round(i, 2) for i in frame_oppo[1::2]]
                    away_x = [np.round(i, 2) for i in frame_oppo[::2]]
                    away = list(np.ones((len(away_y),), dtype=int))

                    df = pd.DataFrame({
                        "x": home_x + away_x,
                        "y": home_y + away_y,
                        "team": home + away
                    })
                    df = df.dropna()
                    points = np.column_stack((df.x, df.y))

                    # Reflecting points on all four side-lines---
                    # Reflection on left goal-line
                    l_t_x = np.array([((x + 105) * -1, y) for x, y in points if x > 0])
                    l_t_x_m = np.array([(abs(x) - 105, y) for x, y in points if x < 0])
                    if len(l_t_x) and len(l_t_x_m) > 0:
                        l_points = np.row_stack((l_t_x, l_t_x_m))
                    elif len(l_t_x) == 0:
                        t_points = l_t_x_m
                    elif len(l_t_x_m) == 0:
                        t_points = l_t_x

                    # Reflection on right goal-line
                    r_t_x = np.array([((x - 105) * -1, y) for x, y in points if x > 0])
                    r_t_x_m = np.array([(abs(x) + 105, y) for x, y in points if x < 0])
                    if len(r_t_x) and len(r_t_x_m) > 0:
                        r_points = np.row_stack((r_t_x, r_t_x_m))
                    elif len(r_t_x) == 0:
                        t_points = r_t_x_m
                    elif len(r_t_x_m) == 0:
                        t_points = r_t_x

                    # Reflection on bottom side-line
                    b_t_y = np.array([(x, (y + 68) * -1) for x, y in points if y > 0])
                    b_t_y_m = np.array([(x, abs(y) - 68) for x, y in points if y < 0])
                    if len(b_t_y) and len(b_t_y_m) > 0:
                        b_points = np.row_stack((b_t_y, b_t_y_m))
                    elif len(b_t_y) == 0:
                        t_points = b_t_y_m
                    elif len(b_t_y_m) == 0:
                        t_points = b_t_y

                    # Reflection on top side-line
                    t_t_y = np.array([(x, (y - 68) * -1) for x, y in points if y > 0])
                    t_t_y_m = np.array([(x, abs(y) + 68) for x, y in points if y < 0])
                    if len(t_t_y) and len(t_t_y_m) > 0:
                        t_points = np.row_stack((t_t_y, t_t_y_m))
                    elif len(t_t_y) == 0:
                        t_points = t_t_y_m
                    elif len(t_t_y_m) == 0:
                        t_points = t_t_y

                    extended_points = np.row_stack((points,
                                                    l_points,  # Reflection in left touchline
                                                    b_points,  # Reflection in bottom touchline
                                                    r_points,  # Reflection in right touchline
                                                    t_points,  # Reflection in top touchline
                                                    ))

                    area = voronoi_area(extended_points)
                    if j == 0 or j == 1:
                        pos_sc.append((np.sum(area[:11])) / (105 * 68))
                    if j == 2 or j == 3:
                        pos_sc.append((np.sum(area[11:])) / (105 * 68))
                sc.append(np.mean(pos_sc))
        # print(np.round(time.time() - t, 3), "sec half")
        space_control.update({j: np.round(np.mean(sc), 2)})

    # print(np.round(time.time() - t, 3), "sec elapsed")
    return space_control


def team_surface_possession(position_data, info_path):
    """
    Calculation of the mean enclosed surface by the team (goalkeeper excluded) during possessions that take longer than
    3s using the ConvexHull-Method. It also returns the mean enclosed surface when the opponent is in possession for
    longer than 3s.

    Parameters
    ----------
    position_data: Floodlight XY-Objects
        XY-Objects containing the position data of both teams and both half-times
    info_path: str or pathlib.Path
        Full path to XML File where the Match Information data in DFL format is saved

    Returns
    -------
    surface_possession: Dict[0: sp0, 1:sp1, 2:sp2, 3:sp3]
        Dictionary containing the mean enclosed area of each team in their possession sequences (>3s) for both
        half-times.
        sp0: HomeHT1, sp2: HomeHT2, sp2: AwayHT1, sp3: AwayHT2


    surface_possession: Dict[0: sop0, 1:sop1, 2:sop2, 3:sop3]
        Dictionary containing the mean enclosed area of each team during opponent's possession sequences (>3s) for both
        half-times.
        sp0: AwayHT1, sop2: AwayHT2, sop2: HomeHT1, sp3: HomeHT2
    """
    possessions_one = position_data[6].find_sequences()
    possessions_two = position_data[7].find_sequences()

    # Get xIDs for Goalkeepers to exclude them
    player_positions = bf.player_positions(info_path)
    player_IDs = create_links_from_mat_info(info_path)
    gk_xID = {}
    for j in ["Home", "Away"]:
        gk = [x[0] for x in player_positions[j].items() if x[1] == "TW"]
        jID = [x[1] for x in player_IDs[1][j].items() for y in gk if x[0] == y]
        xID = [x[1] for x in player_IDs[0][j].items() for y in jID if x[0] == y]
        gk_xID.update({j: xID})
    # Edited data without goalkeepers
    n_data = {}
    for n, dat in enumerate(position_data[:4]):
        if n == 0 or n == 1:
            team = "Home"
        else:
            team = "Away"
        include = np.full((dat.N * 2), True)
        for g in gk_xID[team]:
            exclude_start = g * 2
            exclude_end = exclude_start + 2
            include[exclude_start:exclude_end] = False
        n_data.update({n: XY(dat.xy[:, include])})

    s_pos = []
    s_opos = []
    for j in range(0, 4):
        if j == 0:
            possessions = possessions_one[1]
            n_pos_team = n_data[0]
            n_opo_team = n_data[2]
        elif j == 1:
            possessions = possessions_two[1]
            n_pos_team = n_data[1]
            n_opo_team = n_data[3]
        elif j == 2:
            possessions = possessions_one[2]
            n_pos_team = n_data[2]
            n_opo_team = n_data[0]
        elif j == 3:
            possessions = possessions_two[2]
            n_pos_team = n_data[3]
            n_opo_team = n_data[1]

        start = [pos[0] for pos in possessions]
        end = [pos[1] for pos in possessions]
        sequences = list(np.column_stack((start, end)))
        sequences = [x for x in sequences if len(range(x[0], x[1])) >= 75]
        # Area Pos
        frame_x = [n_pos_team[start:end][:, ::2] for start, end in sequences]
        frame_y = [n_pos_team[start:end][:, 1::2] for start, end in sequences]

        points_pos = []
        for n, frame in enumerate(frame_x):
            p = []
            for i, f in enumerate(frame):
                q = np.column_stack((f, frame_y[n][i]))
                q = np.array([x for x in q if pd.isnull(x[0]) is False])
                p.append(q)
            points_pos.append(p)

        area_pos = []
        for n, pos in enumerate(points_pos):
            frames_area = []
            for f in pos:
                frames_area.append(np.round(ConvexHull(f).volume, 2))
            area_pos.append(frames_area)

        # Opo Area NEW
        opo_frame_x = [n_opo_team[start:end][:, ::2] for start, end in sequences]
        opo_frame_y = [n_opo_team[start:end][:, 1::2] for start, end in sequences]

        points_opos = []
        for n, frame in enumerate(opo_frame_x):
            p = []
            for i, f in enumerate(frame):
                q = np.column_stack((f, opo_frame_y[n][i]))
                q = np.array([x for x in q if pd.isnull(x[0]) is False])
                p.append(q)
            # p_pos = np.column_stack((frame, frame_y[n]))
            points_opos.append(p)

        area_opos = []
        for n, pos in enumerate(points_opos):
            frames_area = []
            for f in pos:
                frames_area.append(np.round(ConvexHull(f).volume, 2))
            area_opos.append(frames_area)

        s_pos.append(np.round(np.mean([np.mean(x) for x in area_pos]), 2))
        s_opos.append(np.round(np.mean([np.mean(x) for x in area_opos]), 2))

    return s_pos, s_opos


def closest_distance(position_data, info_path):
    """
    Calculation of the mean closest distance from players to the opponent players when out of possession
    Parameters
    ----------
    position_data: Floodlight XY-Objects
        XY-Objects containing the position data of both teams and both half-times
    info_path: str or pathlib.Path
        Full path to XML File where the Match Information data in DFL format is saved

    Returns
    -------

    """

    possessions_one = position_data[6].find_sequences()
    possessions_two = position_data[7].find_sequences()
    # Only for outfield players, mean for whole team

    # Get xIDs for Goalkeepers to exclude them
    player_positions = bf.player_positions(info_path)
    player_IDs = create_links_from_mat_info(info_path)
    gk_xID = {}
    for j in ["Home", "Away"]:
        gk = [x[0] for x in player_positions[j].items() if x[1] == "TW"]
        jID = [x[1] for x in player_IDs[1][j].items() for y in gk if x[0] == y]
        xID = [x[1] for x in player_IDs[0][j].items() for y in jID if x[0] == y]
        gk_xID.update({j: xID})

    n_data = {}
    for n, dat in enumerate(position_data[:4]):
        if n == 0 or n == 1:
            team = "Home"
        else:
            team = "Away"
        include = np.full((dat.N * 2), True)
        for g in gk_xID[team]:
            exclude_start = g * 2
            exclude_end = exclude_start + 2
            include[exclude_start:exclude_end] = False
        n_data.update({n: XY(dat.xy[:, include])})

    c_distances = {}
    for j in range(0, 4):
        if j == 0:
            possessions = possessions_one[1]
            n_def_team = n_data[0]
            n_att_team = n_data[2]
        elif j == 1:
            possessions = possessions_two[1]
            n_def_team = n_data[1]
            n_att_team = n_data[3]
        elif j == 2:
            possessions = possessions_one[2]
            n_def_team = n_data[2]
            n_att_team = n_data[0]
        elif j == 3:
            possessions = possessions_two[2]
            n_def_team = n_data[3]
            n_att_team = n_data[1]
        start = [pos[0] for pos in possessions]
        end = [pos[1] for pos in possessions]
        sequences = list(np.column_stack((start, end)))
        sequences = [x for x in sequences if len(range(x[0], x[1])) >= 75]

        def_x = [n_def_team[start:end][:, ::2] for start, end in sequences]
        def_y = [n_def_team[start:end][:, 1::2] for start, end in sequences]

        att_x = [n_att_team[start:end][:, ::2] for start, end in sequences]
        att_y = [n_att_team[start:end][:, 1::2] for start, end in sequences]

        points_def = []
        for n, frame in enumerate(def_x):
            p = []
            for i, f in enumerate(frame):
                q = np.column_stack((f, def_y[n][i]))
                q = np.array([x for x in q if pd.isnull(x[0]) is False])
                p.append(q)
            points_def.append(p)
        points_att = []
        for n, frame in enumerate(att_x):
            p = []
            for i, f in enumerate(frame):
                q = np.column_stack((f, att_y[n][i]))
                q = np.array([x for x in q if pd.isnull(x[0]) is False])
                p.append(q)
            points_att.append(p)

        def_p = [x for y in points_def for x in y]
        att_p = [x for y in points_att for x in y]

        closest_distances = []
        for n, frame in enumerate(def_p):
            closest_distances_frame = []
            for player in frame:
                distances = [distance.euclidean(player, player_away) for player_away in att_p[n]]
                closest_distances_frame.append(np.min(distances))
            closest_distances.append(np.mean(closest_distances_frame))

        c_distances.update({j: np.round(np.mean(closest_distances), 2)})

    return c_distances
