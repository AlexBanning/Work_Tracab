"""
Functions that use any data or data output and return or calculate values out of them.
"""
import os
import numpy as np
import pandas as pd
from xml.dom.minidom import parse
from TracabModules.Internal.gamelog_functions import get_player_name
import logging


class GatewayKPIs:

    def __init__(self, tf08_data, kpi_list_tf08):
        self.tf08_data = tf08_data
        self.kpi_list_tf08 = kpi_list_tf08

    def get_tf08_kpis(self):
        """
        Extracts specified KPIs (Key Performance Indicators) from TF08 data.

        Args:
            tf08_data (dict): TF08 data containing information about home team and away team.
            kpi_list (list): List of KPIs to extract. If None, all available KPIs will be returned.

        Returns:
            dict: Dictionary containing specified KPIs for home team and away team.
        """
        logging.basicConfig(level=logging.INFO)
        if self.kpi_list_tf08 is None:
            logging.info(f'No list of KPIs has been provided. Please return and provide a list!')

        kpis_mapping = {
            'Distance': self.extract_distance_kpi,
            'Possession': self.extract_possession_kpi,
            'TopSpeedPlayer': self.extract_topSpeedPlayer_kpi
            # Add more KPIs and their corresponding extraction functions here
        }

        home_team = self.tf08_data['Periods'][0]['HomeTeam']['TeamName']
        home_kpis = {}
        away_team = self.tf08_data['Periods'][0]['AwayTeam']['TeamName']
        away_kpis = {}

        for kpi in self.kpi_list_tf08:
            if kpi in kpis_mapping:
                home_kpis[kpi], away_kpis[kpi] = kpis_mapping[kpi](self.tf08_data)

        return {home_team: home_kpis, away_team: away_kpis}

    def extract_distance_kpi(self, tf08_data):
        home_dist = np.round(self.tf08_data['Periods'][0]['HomeTeam']['Distance'] / 1000, 2)
        away_dist = np.round(self.tf08_data['Periods'][0]['AwayTeam']['Distance'] / 1000, 2)
        return home_dist, away_dist

    def extract_possession_kpi(self, tf08_data):
        home_possession = self.tf08_data['Periods'][0]['HomeTeam']['PossessionData']['PossessionPercentage']
        away_possession = self.tf08_data['Periods'][0]['AwayTeam']['PossessionData']['PossessionPercentage']
        return home_possession, away_possession

    def extract_topSpeedPlayer_kpi(self, tf08_data):
        try:
            home_speeds = {f'{player['PlayerName']}':
                              player['TopSpeed'] for player in self.tf08_data['Periods'][0]['HomeTeam']['Players']
                           if len(player['PlayerName']) > 5}
        except Exception as e:
            home_speeds = {}
            (logging.info(f'Error {e} has occured when trying to fetch the HomeTeam TopSpeed'))
        try:
            away_speeds = {f'{player['PlayerName']}':
                           player['TopSpeed'] for player in tf08_data['Periods'][0]['AwayTeam']['Players']
                           if len(player['PlayerName']) > 5}
        except Exception as e:
            away_speeds = {}
            (logging.info(f'Error {e} has occured when trying to fetch the AwayTeam TopSpeed'))

        return home_speeds, away_speeds


def get_excel_kpis(main_folder, files, gamelog, ven, obs, match_info):
    """
    This function aims to fetch all KPIs of interest for the BVB validation from the PlayerID_resolution.xml-files and
    returns them for both BVB and their opponents.

    :param main_folder:
    :param ven: str
        String indicating whether DFL or EPL files should be fetched.
    :param gamelog: str
        String that is equal to the path of the gamelog that needs to be used to fetch the players' names.
    :param files: list of str
        List that contains the names of all PlayerID_resolution.xml files in the destined folder.
    :param match_info:
    :return:
        players_data_bvb: pd.DataFrame
        players_data_oppo: pd.DataFrame
            DataFrames that contain all KPI scores and player information for each player of the specific team.
    """

    # Create a DF for each team
    players_data_bvb = pd.DataFrame()
    players_data_oppo = pd.DataFrame()

    if obs is True:
        dpt = 'Observed'
    elif obs is False:
        dpt = 'Live'

    if ven == 'DFL':
        path = (os.getcwd() + r'\Observed_DFL\Webmonitor\Game_' +
                match_info['match_id'] + r'_3' + '\\' + dpt + r'\Team\Player')
    elif ven == 'EPL':
        path = (os.getcwd() + r'\Observed_EPL\Webmonitor\Game_' +
                match_info['match_id'] + r'_2' + '\\' + dpt + r'\Team\Player')

    # Loop through all PlayerID_Resolution.xml files to fetch KPI-scores for each player
    for i, file in enumerate(files):
        xml_doc = parse(path + '\\' + file)
        team_id = str(xml_doc.getElementsByTagName('PlayerData')[0].attributes['TeamID'].childNodes[0].data)
        player_id = str(xml_doc.getElementsByTagName('PlayerData')[0].attributes['PlayerID'].childNodes[0].data)
        player_nr = str(xml_doc.getElementsByTagName('PlayerData')[0].attributes['PlayerNumber'].childNodes[0].data)
        player_name = get_player_name(main_folder + '\\' + dpt + '_DFL' + '\\' + gamelog, team_id, player_id)
        stats_elements = xml_doc.getElementsByTagName('Stats')

        # Fetch those KPIs that are directly inside the PlayerID_Resolution.xml
        resolution_kpis = ['Distance', 'TopSpeed', 'AvgSpeed', 'Sprints', 'SprintDistance', 'SpeedRuns',
                           'SpeedRunsDistance', 'LowSpeedRuns', 'LowSpeedRunsDistance', 'DistanceIBC', 'SprintsIBC',
                           'SpeedRunsIBC', 'AvgTimeIBC']

        player_og_stats = []
        for j, kpi in enumerate(resolution_kpis):
            player_og_stats.append(float(stats_elements[-1].getElementsByTagName(kpi)[0].childNodes[0].data))

        # Do not add players who did not get any distances (total distance == 0)
        if player_og_stats[0] == float(0):
            continue

        # calculate those KPIs that are not directly inside the PlayerID_Resolution.xml
        tot_time = np.round(
            float(stats_elements[-1].getElementsByTagName('PlayTime')[0].childNodes[0].data) / 25 / 60,
            2)
        top_speed = max([float(x.getElementsByTagName('TopSpeed')[0].childNodes[0].data) for x in stats_elements])
        dist_min = np.round(np.divide(player_og_stats[0], tot_time), 2)
        dist_min_sprints = np.round(np.divide(player_og_stats[4], tot_time), 2)
        dist_min_hsruns = np.round(np.divide(player_og_stats[6], tot_time), 2)
        dist_min_runs = np.round(np.divide(player_og_stats[8], tot_time), 2)
        n_vhiruns = np.sum([player_og_stats[3], player_og_stats[5]])
        dist_vhiruns = np.round(np.sum([player_og_stats[4], player_og_stats[6]]), 2)
        dist_min_vhiruns = np.round(np.divide(dist_vhiruns, tot_time), 2)
        n_hiruns = np.sum([player_og_stats[-6], n_vhiruns])
        dist_hiruns = np.round(np.sum([player_og_stats[-5], dist_vhiruns]), 2)
        dist_min_hiruns = np.round(np.divide(dist_hiruns, tot_time), 2)

        # Add all KPIs to a player DF
        player = pd.DataFrame({"TeamID": team_id, "PlayerID": player_id, "PlayerNumber": player_nr,
                               "PlayerName": player_name, "PlayTime (min)": tot_time,
                               "Distance (m)": player_og_stats[0],
                               "Distance/min": dist_min, "TopSpeed (km/h)": top_speed,
                               "AvgSpeed (km/h)": player_og_stats[2], "Sprints > 25,2km/h": player_og_stats[3],
                               "Distance Sprints (m)": player_og_stats[4], "Distance/min Sprints": dist_min_sprints,
                               "HighSpeedRuns 19,8-25,2km/h": player_og_stats[5],
                               "Distance HSR (m)": player_og_stats[6],
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
