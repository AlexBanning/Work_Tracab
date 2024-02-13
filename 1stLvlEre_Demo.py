from IPython.display import display
from requests.structures import CaseInsensitiveDict
import TracabModules.apiFunctions as af
import requests
import string
import tkinter as tk
from tkinter import ttk
import pandas as pd

# Version 1.2
# 2023/08/28: Updated that a message is shown when no lineups are available yet.
# 2023/08/31: Updated, that players with differences are directly displayed as well
# 2023/09/04: Updated, that players are not parsed based on their player status anymore. This information is only
#             available post KO. Now implementing players based on an existing jerseyNumber.
# 2023/10/11: Updated, wrong_player_function was extracted as a module and now only the function remains in line 39
#             to shorten the code.

login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = "Bearer " + token
# Select the match of interest
matchday_url = 'https://data.voetbaldatacentre.nl/av/api/matches/6'
md_info = requests.get(matchday_url, headers=headers).json()
translation = str.maketrans('', '', string.digits)
matches = [x['matchDescription'].translate(translation) for x in md_info]

print('Please insert the number of the match you want to check:' + ' 1-' + str(len(matches)) + '\n'
                                                                                               '' + '\n'.join(
    matches) + '\n'
      )
choice = int(input())
match = matches[int(choice) - 1]
home_team = match.split('-')[0].strip()
away_team = match.split('-')[1].strip()

if home_team == 'AFC Ajax':
    home_team = 'Ajax'
elif home_team == 'Almere City':
    home_team = 'Almere City FC'
home, away = af.get_both_lineups_demo(token, md_info[choice - 1]['matchNumber'], home_team=home_team)

home_wrong_player, away_wrong_player = af.get_wrong_players(home, away)

if not home[0].empty or not away[0].empty:
    # Create and run the DataFrameViewer
    app_home = af.DataFrameViewer(home[1], 'API - ' + home_team)
    app_away = af.DataFrameViewer(away[1], 'API - ' + away_team)
    app_home.mainloop()
    app_away.mainloop()
elif home[0].empty or away[0].empty:
    print('The API lineup information for this match are not available yet!')
input('\n Press Enter to exit;')