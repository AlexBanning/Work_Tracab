from IPython.display import display
from requests.structures import CaseInsensitiveDict
import TracabModules.apiFunctions as af
import requests
import string
import subprocess


# Version 1.2
# 2023/08/28: Updated that a message is shown when no lineups are available yet.
login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = "Bearer " + token
# Select the match of interest
matchday_url = 'https://data.voetbaldatacentre.nl/av/api/matches'
md_info = requests.get(matchday_url, headers=headers).json()
translation = str.maketrans('', '', string.digits)
matches = [x['matchDescription'].translate(translation) for x in md_info]

print('Please insert the number of the match you want to check:' + ' 1-' + str(len(matches)) + '\n'
                                                                                               '' + '\n'.join(
    matches) + '\n'
      )
choice = int(input())
match = matches[int(choice) - 1]

home_team = match.split('-')[0][0:-2]
home, away = af.get_api_lineups(token, md_info[choice - 1]['matchNumber'])

if home.empty or away.empty:
    print('The lineup information for this match are not available yet!')
    input('Press Enter to exit;')
else:
    print('Home Team')
    display(home.to_string())
    print(' \n \n Away Team')
    display(away.to_string())
    input('Press Enter to exit;')
