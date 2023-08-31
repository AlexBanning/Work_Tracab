import requests
import pandas as pd
from IPython.display import display
from requests.structures import CaseInsensitiveDict
import TracabModules.apiFunctions as af


login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
lineups = af.get_both_lineups(token, 'M335374348')

test = pd.concat([lineups[0], lineups[1]], axis=1)
display(test.to_string())

# Tests with production environment

login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = "Bearer " + token

# Get general competition info
comp_info_url = 'https://data.voetbaldatacentre.nl/av/api/competitions'
comp_info = requests.get(comp_info_url, headers=headers).json()

# Get matchinfo for all matches of current matchday (or of a previous MD using the calendar week)
matchday_url = 'https://data.voetbaldatacentre.nl/av/api/matches/33'
md_info = requests.get(matchday_url, headers=headers).json()

# Get lineups for a single match by match number
lineup_url = 'https://data.voetbaldatacentre.nl/av/api/match/lineup/' + 'M335374348'
lineup_info = requests.get(lineup_url, headers=headers).json()

# Get all matches from a certain team
team_match_url = 'https://data.voetbaldatacentre.nl/av/api/matches/team/' + str(md_info[1]['awayTeam']['teamId'])
team_matches = requests.get(team_match_url, headers=headers).json()
lineup_url = 'https://data.voetbaldatacentre.nl/av/api/match/lineup/' + str(team_matches[0]['matchNumber'])
lineup_info = requests.get(lineup_url, headers=headers).json()

matchday_url = 'https://data.voetbaldatacentre.nl/av/api/matches/33'
md_info = requests.get(matchday_url, headers=headers).json()

lineup_url = ['https://data.voetbaldatacentre.nl/av/api/match/lineup/' + str(x['matchNumber']) for x in md_info]
lineup_info = [requests.get(x, headers=headers).json() for x in lineup_url]

test = pd.DataFrame()
for lineups in enumerate(lineup_info):
    home = pd.DataFrame([{'Player': x['firstName'] + ' ' + y['lastName'],
                          'jerseyNumber': int(z['matchShirtNumber'])} for x, y, z in
                         zip(lineups[1]['homeTeam']['players'], lineups[1]['homeTeam']['players'],
                             lineups[1]['homeTeam']['players'])])

    away = pd.DataFrame([{'Player': x['firstName'] + ' ' + y['lastName'],
                          'jerseyNumber': int(z['matchShirtNumber'])} for x, y, z in
                         zip(lineups[1]['awayTeam']['players'], lineups[1]['awayTeam']['players'],
                             lineups[1]['awayTeam']['players'])])

    test = pd.concat([test, home, away], ignore_index=True)


