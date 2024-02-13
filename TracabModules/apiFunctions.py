import os
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
from bs4 import BeautifulSoup
import ftputil
import subprocess
from datetime import date
import numpy as np
import tkinter as tk
from tkinter import ttk


def get_token(url, creds):
    """

    :param url: str with the API-address one wants to do a request from
    :param creds: dict
        containing the username and password need for authentication
    :return:
    """

    headers = CaseInsensitiveDict()
    headers['content-type'] = 'application/json'
    r = requests.post(url, headers=headers, data=creds)
    token = r.content.decode('utf-8')[10:-2]

    return token


def api_lineups(token, match_id):
    """

    :param token:
    :param match_id:
    :return:
    """

    line_up_url = 'https://data.voetbaldatacentre.nl/av/api/match/lineup/' + str(match_id)
    headers = CaseInsensitiveDict()
    headers['accept'] = 'application/json'
    headers['Authorization'] = "Bearer " + token
    # r =  requests.get(line_up_url, headers=headers)
    lineup = requests.get(line_up_url, headers=headers).json()

    return lineup


def get_both_lineups(token, match_id_ere, home_team):
    """
    A function, that fetches lineup information for a single match specified by match_id and our own gamestats to the
    match. Returns four pd.DataFrames containing gamestats information and official lineup information.

    :param token:
    :param match_id_ere:
    :param home_team:
    :return:
    """

    lineups = api_lineups(token, match_id_ere)
    try:
        # Changed to now check if a valid matchShirtNumber is available for the player before adding them to the pd.DF
        home = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
                                 lineups['homeTeam']['players'], lineups['homeTeam']['players'])
                             if z['playerStatus'] == 'EXTRA_PLAYER' or z['playerStatus'] == 'BASE_PLAYER']
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                                 lineups['awayTeam']['players'], lineups['awayTeam']['players'])
                             if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    except KeyError:  # normally one should spefically call the exception one expects to occure and not leave it open
        # to fetch all possible exceptions
        home = pd.DataFrame()
        away = pd.DataFrame()

    # Get Tracab matchID to download and open Tracab gamestats
    match_id_trac = get_tracabID(home_team)

    if match_id_trac is not None:
        # Add C:temp folder where all final gamestats are available as A network drive
        try:
            os.system(r'net use A: /delete /yes')
            os.system(r'net use A: \\10.49.0.10\temp /user:administrator Bismarck27 /persistent:no')
        except:
            print('The connection to APP-CGN could not be created!')
        with open('A:\\' + str(match_id_trac) + 'Gamestats.xml') as fp:
            data = BeautifulSoup(fp, features='xml')
        # with open(str(match_id_trac) + 'Gamestats.xml') as fp:
        #     data = BeautifulSoup(fp, features='xml')

        # Create two DFs containing the players available in Tracab gamestats
        home_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        # firstname  x['sFirstName'].encode('latin').decode('utf-8') + ' ' +
        away_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    else:
        home_gs = pd.DataFrame()
        away_gs = pd.DataFrame()

    return [home, home_gs], [away, away_gs]


def get_both_lineups_demo(token, match_id_ere, home_team):
    """
    A function, that fetches lineup information for a single match specified by match_id and our own gamestats to the
    match. Returns four pd.DataFrames containing gamestats information and official lineup information.

    :param token:
    :param match_id_ere:
    :param home_team:
    :return:
    """

    lineups = api_lineups(token, match_id_ere)
    try:
        # Changed to now check if a valid matchShirtNumber is available for the player before adding them to the pd.DF
        home = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
                                 lineups['homeTeam']['players'], lineups['homeTeam']['players'])
                             if z['playerStatus'] == 'EXTRA_PLAYER' or z['playerStatus'] == 'BASE_PLAYER']
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                                 lineups['awayTeam']['players'], lineups['awayTeam']['players'])
                             if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    except KeyError:  # normally one should spefically call the exception one expects to occure and not leave it open
        # to fetch all possible exceptions
        home = pd.DataFrame()
        away = pd.DataFrame()

    # Get Tracab matchID to download and open Tracab gamestats
    match_id_trac = get_tracabID_demo(home_team)

    if match_id_trac is not None:
        # Add C:temp folder where all final gamestats are available as A network drive
        try:
            os.system(r'net use A: /delete /yes')
            os.system(r'net use A: \\10.49.0.10\temp /user:administrator Bismarck27 /persistent:no')
        except:
            print('The connection to APP-CGN could not be created!')
        with open('A:\\' + str(match_id_trac) + 'Gamestats.xml') as fp:
            data = BeautifulSoup(fp, features='xml')
        # with open(str(match_id_trac) + 'Gamestats.xml') as fp:
        #     data = BeautifulSoup(fp, features='xml')

        # Create two DFs containing the players available in Tracab gamestats
        home_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        # firstname  x['sFirstName'].encode('latin').decode('utf-8') + ' ' +
        away_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    else:
        home_gs = pd.DataFrame()
        away_gs = pd.DataFrame()

    return [home, home_gs], [away, away_gs]


def get_tracabID(home_team):
    """

    :param home_team:
    :return:
    """
    # Create a function that can download the gamestats of a single match based on the home team's name
    # Download squad xml and schedule xml to be able to map team name and team ID and get the MatchID of their match
    server = "213.168.127.130"
    user = "Alex_Test"
    password = "RobberyandLahm5%"
    schedule_filename = 'srml-9-2023-results.xml'
    squads_filename = 'srml-9-2023-squads.xml'
    ftp_dir = 'Opta/MatchInfo'
    try:
        with ftputil.FTPHost(server, user, password) as ftp_host:
            ftp_host.chdir(ftp_dir)
            ftp_host.open(schedule_filename)
            if ftp_host.path.isfile(schedule_filename):
                ftp_host.download(schedule_filename, schedule_filename)
            ftp_host.open(squads_filename)
            if ftp_host.path.isfile(squads_filename):
                ftp_host.download(squads_filename, squads_filename)
    except:
        pass

    # Open xmls
    with open(schedule_filename,
              encoding='utf8') as fp:
        schedule_data = BeautifulSoup(fp, 'xml')

    # Open team info
    with open(squads_filename,
              encoding='utf8') as fp:
        team_data = BeautifulSoup(fp, 'xml')

    # Create dictionary to link team_name and team_id
    teams = team_data.find_all('Team')
    team_names = [x.find('Name').text for x in teams]
    team_ids = [x['uID'] for x in teams]
    team_dict = dict(zip(team_ids, team_names))
    # Get teamID based on name of home team
    tId = [x for x, y in team_dict.items() if home_team in y][0]
    # MatchIds of all matches of the home_team
    matches_schedule = schedule_data.find_all('MatchData')
    today = date.today().strftime('%Y-%m-%d')

    try:
        match_id = [x['uID'][1:] for x in matches_schedule if x.find('MatchInfo').find('Date').text[0:10] == today and
                    str(x.find('TeamData')['TeamRef']) == tId][0]
        return match_id
    except IndexError:
        print('Could not receive a Tracab-ID')


def get_tracabID_demo(home_team):
    """

    :param home_team:
    :return:
    """
    # Create a function that can download the gamestats of a single match based on the home team's name
    # Download squad xml and schedule xml to be able to map team name and team ID and get the MatchID of their match
    server = "213.168.127.130"
    user = "Alex_Test"
    password = "RobberyandLahm5%"
    schedule_filename = 'srml-9-2023-results.xml'
    squads_filename = 'srml-9-2023-squads.xml'
    ftp_dir = 'Opta/MatchInfo'
    try:
        with ftputil.FTPHost(server, user, password) as ftp_host:
            ftp_host.chdir(ftp_dir)
            ftp_host.open(schedule_filename)
            if ftp_host.path.isfile(schedule_filename):
                ftp_host.download(schedule_filename, schedule_filename)
            ftp_host.open(squads_filename)
            if ftp_host.path.isfile(squads_filename):
                ftp_host.download(squads_filename, squads_filename)
    except:
        pass

    # Open xmls
    with open(schedule_filename,
              encoding='utf8') as fp:
        schedule_data = BeautifulSoup(fp, 'xml')

    # Open team info
    with open(squads_filename,
              encoding='utf8') as fp:
        team_data = BeautifulSoup(fp, 'xml')

    # Create dictionary to link team_name and team_id
    teams = team_data.find_all('Team')
    team_names = [x.find('Name').text for x in teams]
    team_ids = [x['uID'] for x in teams]
    team_dict = dict(zip(team_ids, team_names))
    # Get teamID based on name of home team
    tId = [x for x, y in team_dict.items() if home_team in y][0]
    # MatchIds of all matches of the home_team
    matches_schedule = schedule_data.find_all('MatchData')
    today = '2024-02-10'

    try:
        match_id = [x['uID'][1:] for x in matches_schedule if x.find('MatchInfo').find('Date').text[0:10] == today and
                    str(x.find('TeamData')['TeamRef']) == tId][0]
        return match_id
    except IndexError:
        print('Could not receive a Tracab-ID')


def get_wrong_players(home, away):
    """
    :param home:
    :param away:
    :return:
    """

    home_check = pd.merge(home[0], home[1], on=['jerseyNumber'], how='left', indicator='exists')
    away_check = pd.merge(away[0], away[1], on=['jerseyNumber'], how='left', indicator='exists')
    # add column to show if each row in first DataFrame exists in second
    home_check['exists'] = np.where(home_check.exists != 'both', True, False)
    away_check['exists'] = np.where(away_check.exists != 'both', True, False)

    home_wrong = np.where(home_check['exists'] == True)
    home_wrong_player = home_check.iloc[home_wrong[0]].rename(columns={'Player_x': 'Player',
                                                                       'jerseyNumber': 'Nr. EreInfo'
                                                                       }
                                                              ).sort_values(by=['Player'], axis=0)
    away_wrong = np.where(away_check['exists'] == True)
    away_wrong_player = away_check.iloc[away_wrong[0]].rename(columns={'Player_x': 'Player',
                                                                       'jerseyNumber': 'Nr. EreInfo'
                                                                       }
                                                              ).sort_values(by=['Player'], axis=0)

    home_wrong_player = home_wrong_player.drop(['Player_y', 'exists'], axis=1)
    away_wrong_player = away_wrong_player.drop(['Player_y', 'exists'], axis=1)

    return home_wrong_player, away_wrong_player


class DataFrameViewer(tk.Tk):
    def __init__(self, df, team):
        tk.Tk.__init__(self)
        self.title(str(team))

        # Adjust the default window size
        self.geometry('300x500')

        # Create a Treeview widget
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        # Add columns to the Treeview
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=20, anchor=tk.CENTER)  # Adjust the width as needed

        # Insert data into the Treeview
        for i, row in df.iterrows():
            self.tree.insert("", i, values=list(row))

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
