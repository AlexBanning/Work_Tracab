import requests
import pandas as pd
from pandasgui import show
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict
import TracabModules.apiFunctions as af


login_url = 'https://stagingdata.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'

line_up_url = 'https://stagingdata.voetbaldatacentre.nl/bv/api/match_lineup/161783'
token = af.get_token(login_url, creds)
lineups = af.get_both_lineups(token, '161783')



home = pd.DataFrame([{'Player': x['firstName'] + ' ' + y['lastName'],
      'jerseyNumber': int(z['matchShirtNumber'])} for x, y, z in
        zip(lineups['homeTeam']['players'],lineups['homeTeam']['players'], lineups['homeTeam']['players']) if
                     type(z['matchShirtNumber']) == int ]).sort_values(by=['jerseyNumber'],axis=0, ascending=True)

away = pd.DataFrame([{'Player': x['firstName'] + ' ' + y['lastName'],
      'jerseyNumber': int(z['matchShirtNumber'])} for x, y, z in
        zip(lineups['awayTeam']['players'],lineups['awayTeam']['players'], lineups['awayTeam']['players']) if
                     type(z['matchShirtNumber']) == int ]).sort_values(by=['jerseyNumber'],axis=0, ascending=True)

with open('2291800Gamestats.xml') as fp:
    data = BeautifulSoup(fp, features='xml')

home_gs = pd.DataFrame(
    [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode('latin').decode('utf-8'),
      'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
     zip(data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
         data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
         data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'))]
).sort_values(by=['jerseyNumber'],axis=0, ascending=True)

away_gs = pd.DataFrame(
    [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode('latin').decode('utf-8'),
      'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
     zip(data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
         data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
         data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'))]
).sort_values(by=['jerseyNumber'],axis=0, ascending=True)


