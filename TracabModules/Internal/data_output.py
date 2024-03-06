import pandas as pd
import numpy as np
from xml.dom.minidom import parse
import os
from TracabModules.Internal.gamelog_functions import get_player_name

bvb_validation_kpis = ["TeamID", "PlayerID", "PlayerNumber", "PlayerName",
                       "PlayTime (min)", "Distance (m)", "Distance/min",
                       "TopSpeed (km/h)", "AvgSpeed (km/h)", "Sprints > 25,2km/h",
                       "Distance Sprints (m)", "Distance/min Sprints",
                       "HighSpeedRuns 19,8-25,2km/h", "Distance HSR (m)",
                       "Distance/min HSR", "Runnings 14,4-19,8kmh/",
                       "Running Distance (m)", "Running Distance/min",
                       "HighIntensityRuns > 14,4km/h", "Distance HIR (m)",
                       "Distance/min HIR", "VeryHighIntensityRuns",
                       "Distance VHIR (m)", "Distance/min VHIR",
                       "Distance IBC", "Sprints IBC", "SpeedRuns IBC",
                       "AvgTime IBC"]

resolution_kpis = ['Distance', 'TopSpeed', 'AvgSpeed', 'Sprints', 'SprintDistance', 'SpeedRuns',
                   'SpeedRunsDistance', 'LowSpeedRuns', 'LowSpeedRunsDistance', 'DistanceIBC', 'SprintsIBC',
                   'SpeedRunsIBC', 'AvgTimeIBC']


def get_player_stats(files, gamelog, ven):
    """
    This function aims to fetch all KPIs of interest for the BVB validation from the PlayerID_resolution.xml-files and
    returns them for both BVB and their opponents.
    :param ven: str
        String indicating whether DFL or EPL files should be fetched.
    :param gamelog: str
        String that is equal to the path of the gamelog that needs to be used to fetch the players' names.
    :param files: list of str
        List that contains the names of all PlayerID_resolution.xml files in the destined folder.
    :return:
        players_data_bvb: pd.DataFrame
        players_data_oppo: pd.DataFrame
            DataFrames that contain all KPI scores and player information for each player of the specific team.
    """

    # Create a DF for each team
    players_data_bvb = pd.DataFrame()
    players_data_oppo = pd.DataFrame()

    if ven == 'DFL':
        path = os.getcwd() + r'\Players_DFL'
    elif ven == 'EPL':
        path = os.getcwd() + r'\Players_EPL'

    # Loop through all PlayerID_Resolution.xml files to fetch KPI-scores for each player
    for i, file in enumerate(files):
        xml_doc = parse(path + '\\' + file)
        team_id = str(xml_doc.getElementsByTagName('PlayerData')[0].attributes['TeamID'].childNodes[0].data)
        player_id = str(xml_doc.getElementsByTagName('PlayerData')[0].attributes['PlayerID'].childNodes[0].data)
        player_nr = str(xml_doc.getElementsByTagName('PlayerData')[0].attributes['PlayerNumber'].childNodes[0].data)
        player_name = get_player_name(gamelog, team_id, player_id)
        stats_elements = xml_doc.getElementsByTagName('Stats')

        # Fetch those KPIs that are directly inside the PlayerID_Resolution.xml
        player_og_stats = []
        for j, kpi in enumerate(resolution_kpis):
            player_og_stats.append(float(stats_elements[-1].getElementsByTagName(kpi)[0].childNodes[0].data))

        # Do not add players who did not get any distances (total distance == 0)
        if player_og_stats[0] == float(0):
            continue

        # calculate those KPIs that are not directly inside the PlayerID_Resolution.xml
        tot_time = np.round(float(stats_elements[-1].getElementsByTagName('PlayTime')[0].childNodes[0].data) / 25 / 60,
                            2)
        dist_min = np.round(np.divide(player_og_stats[0], tot_time), 2)
        dist_min_sprints = np.round(np.divide(player_og_stats[5], tot_time), 2)
        dist_min_hsruns = np.round(np.divide(player_og_stats[7], tot_time), 2)
        dist_min_runs = np.round(np.divide(player_og_stats[9], tot_time), 2)
        n_vhiruns = np.sum([player_og_stats[4], player_og_stats[6]])
        dist_vhiruns = np.round(np.sum([player_og_stats[5], player_og_stats[7]]), 2)
        dist_min_vhiruns = np.round(np.divide(dist_vhiruns, tot_time), 2)
        n_hiruns = np.sum([player_og_stats[-6], n_vhiruns])
        dist_hiruns = np.round(np.sum([player_og_stats[-5], dist_vhiruns]), 2)
        dist_min_hiruns = np.round(np.divide(dist_hiruns, tot_time), 2)

        # Add all KPIs to a player DF
        player = pd.DataFrame({"TeamID": team_id, "PlayerID": player_id, "PlayerNumber": player_nr,
                               "PlayerName": player_name, "PlayTime (min)": tot_time,
                               "Distance (m)": player_og_stats[0],
                               "Distance/min": dist_min, "TopSpeed (km/h)": player_og_stats[2],
                               "AvgSpeed (km/h)": player_og_stats[3], "Sprints > 25,2km/h": player_og_stats[4],
                               "Distance Sprints (m)": player_og_stats[5], "Distance/min Sprints": dist_min_sprints,
                               "HighSpeedRuns 19,8-25,2km/h": player_og_stats[6],
                               "Distance HSR (m)": player_og_stats[7],
                               "Distance/min HSR": dist_min_hsruns, "Runnings 14,4-19,8kmh/": player_og_stats[-6],
                               "Running Distance (m)": player_og_stats[-5], "Running Distance/min": dist_min_runs,
                               "HighIntensityRuns > 14,4km/h": n_hiruns, "Distance HIR (m)": dist_hiruns,
                               "Distance/min HIR": dist_min_hiruns, "VeryHighIntensityRuns": n_vhiruns,
                               "Distance VHIR (m)": dist_vhiruns, "Distance/min VHIR": dist_min_vhiruns,
                               "Distance IBC": player_og_stats[-4], "Sprints IBC": player_og_stats[-3],
                               "SpeedRuns IBC": player_og_stats[-2], "AvgTime IBC": player_og_stats[-1]}, index=[0])

        # Add the player DF to the belonging team DF
        if team_id == str(18):
            players_data_bvb = pd.concat([players_data_bvb, player])
        else:
            players_data_oppo = pd.concat([players_data_oppo, player])

    return players_data_bvb, players_data_oppo

