import os
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
from bs4 import BeautifulSoup
import ftputil
import subprocess
from datetime import date


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
                             if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                                 lineups['awayTeam']['players'], lineups['awayTeam']['players'])
                             if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        # Get Tracab matchID to download and open Tracab gamestats
        match_id_trac = get_tracabID(home_team)
        subprocess.call('C:\\Users\\a.banning\\Desktop\\App-CGN-conn.bat')
        # with open('A:\\' + str(match_id_trac) + 'Gamestats.xml') as fp:
        #     data = BeautifulSoup(fp, features='xml')
        with open(str(match_id_trac) + 'Gamestats.xml') as fp:
            data = BeautifulSoup(fp, features='xml')

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
    except:
        home = pd.DataFrame()
        home_gs = pd.DataFrame()
        away = pd.DataFrame()
        away_gs = pd.DataFrame()

    return [home, home_gs], [away, away_gs]


def get_api_lineups(token, match_id_ere):
    """
    A function, that fetches lineup information of the Eredivisie API for a single match and returns them in two
    pd.DataFrames.

    :param token:
    :param match_id_ere:
    :return:
    """

    lineups = api_lineups(token, match_id_ere)
    try:
        home = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
                                 lineups['homeTeam']['players'], lineups['homeTeam']['players'])
                             if y['playerStatus'] == 'BASE_PLAYER' or y['playerStatus'] == 'EXTRA_PLAYER']
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                                 lineups['awayTeam']['players'], lineups['awayTeam']['players'])
                             if y['playerStatus'] == 'BASE_PLAYER' or y['playerStatus'] == 'EXTRA_PLAYER']
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    except:
        home = pd.DataFrame()
        away = pd.DataFrame()

    return home, away


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
    # today = '2023-09-01'
    today = date.today().strftime('%Y-%m-%d')
    match_id = [x['uID'][1:] for x in matches_schedule if x.find('MatchInfo').find('Date').text[0:10] == today and
                str(x.find('TeamData')['TeamRef']) == tId][0]

    return match_id
