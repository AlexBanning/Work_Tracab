import os

import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
from bs4 import BeautifulSoup
import subprocess


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


def get_both_lineups(token, match_id_ere, match_id_trac):
    """
    A function, that fetches lineup information for a single match specified by match_id and our own gamestats to the
    match. Returns four pd.DataFrames containing gamestats information and official lineup information.

    :param token:
    :param match_id_ere:
    :param match_id_trac:
    :return:
    """

    lineups = api_lineups(token, match_id_ere)
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

    # subprocess.call('C:\\Users\\Tracab\\Desktop\\App-CGN-conn.bat')
    # with open('A:\\' + str(match_id_trac) + 'Gamestats.xml') as fp:
    #     data = BeautifulSoup(fp, features='xml')

    with open('testGamestats.xml') as fp:
        data = BeautifulSoup(fp, features='xml')
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

    return home, home_gs, away, away_gs


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
