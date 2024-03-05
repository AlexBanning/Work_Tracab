from IPython.display import display
from requests.structures import CaseInsensitiveDict
import TracabModules.apiFunctions as af
import requests
import string
import tkinter as tk
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
matches = pd.DataFrame([x['matchDescription'].translate(translation) for x in md_info], columns=['Match'])
# Run the match selector
root = tk.Tk()
app = af.DataFrameSelectorApp(root, matches)
root.mainloop()
# Save the selected row to get the match
if app.selected_index is not None:
    selected_match = matches.iloc[app.selected_index]['Match']
    print("Selected Match:")
    print(selected_match)
    # Use the selected_row in the remaining code

home_team = selected_match.split('-')[0].strip()
away_team = selected_match.split('-')[1].strip()

if home_team == 'AFC Ajax':
    home_team = 'Ajax'
elif home_team == 'Almere City':
    home_team = 'Almere City FC'
home, away = af.get_both_lineups_demo(token, md_info[app.selected_index]['matchNumber'], home_team=home_team)

# Adjust column names for the user
home[0] = home[0].rename(columns={'jerseyNumber': '# Home'})
home[1] = home[1].rename(columns={'jerseyNumber': '# Home'})
away[0] = away[0].rename(columns={'jerseyNumber': '# Away'})
away[1] = away[1].rename(columns={'jerseyNumber': '# Away'})


if not home[0].empty or not away[0].empty:
    # Create and run the DataFrameViewer
    app = af.DataFrameViewer(home[0], away[0], home_team, away_team)
    app.mainloop()
elif home[0].empty or away[0].empty:
    print('The API lineup information for this match are not available yet!')
    input('\n Press Enter to exit;')
