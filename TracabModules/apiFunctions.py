import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
from bs4 import BeautifulSoup

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

    line_up_url = 'https://stagingdata.voetbaldatacentre.nl/bv/api/match_lineup/' + str(match_id)
    headers = CaseInsensitiveDict()
    headers['accept'] = 'application/json'
    headers['Authorization'] = "Bearer " + token

    lineup = requests.get(line_up_url, headers=headers).json()

    return lineup


def get_both_lineups(token, match_id):
    """

    :param line_up_url:
    :param token:
    :param match_id:
    :return:
    """

    lineups = api_lineups(token, match_id)
    home = pd.DataFrame([{'Player': x['firstName'] + ' ' + y['lastName'],
                          'jerseyNumber': int(z['matchShirtNumber'])} for x, y, z in
                         zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
                             lineups['homeTeam']['players']) if
                         type(z['matchShirtNumber']) == int]).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

    away = pd.DataFrame([{'Player': x['firstName'] + ' ' + y['lastName'],
                          'jerseyNumber': int(z['matchShirtNumber'])} for x, y, z in
                         zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                             lineups['awayTeam']['players']) if
                         type(z['matchShirtNumber']) == int]).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

    with open('2291800Gamestats.xml') as fp:
        data = BeautifulSoup(fp, features='xml')

    home_gs = pd.DataFrame(
        [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode('latin').decode(
            'utf-8'),
          'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
         zip(data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
             data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
             data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'))]
    ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

    away_gs = pd.DataFrame(
        [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode('latin').decode(
            'utf-8'),
          'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
         zip(data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
             data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
             data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'))]
    ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

    return home, home_gs, away, away_gs