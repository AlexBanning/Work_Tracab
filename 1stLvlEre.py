from IPython.display import display
from requests.structures import CaseInsensitiveDict
import TracabModules.apiFunctions as af
import requests
import string


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

if home_team == 'AFC Ajax':
    home_team = 'Ajax'
elif home_team == 'Almere City':
    home_team = 'Almere City FC'
home, away = af.get_both_lineups(token, md_info[choice - 1]['matchNumber'], home_team=home_team)

if not home[0].empty or not away[0].empty:
    home_wrong_player, away_wrong_player = af.get_wrong_players(home, away)
    if home_wrong_player.empty and away_wrong_player.empty:
        print('Home Team')
        display(home[0].to_string())
        print(' \n \nAway Team')
        display(away[0].to_string())
        print(' \n \n No differences in the lineup information could be detected.')
    elif not home_wrong_player.empty and away_wrong_player.empty:
        print('Home Team')
        display(home[0].to_string())
        print(' \n \nAway Team')
        display(away[0].to_string())
        print(' \n \n The following differences in the home team could be detected: \n' +
              home_wrong_player.to_string())
    elif home_wrong_player.empty and not away_wrong_player.empty:
        print('Home Team')
        display(home[0].to_string())
        print(' \n \nAway Team')
        display(away[0].to_string())
        print(' \n \n The following differences in the away team could be detected: \n' +
              away_wrong_player.to_string())
    elif not home_wrong_player.empty and not away_wrong_player.empty:
        print('Home Team')
        display(home[0].to_string())
        print(' \n \nAway Team')
        display(away[0].to_string())
        print(' \n \n The following differences in the home team could be detected: \n' +
              home_wrong_player.to_string())
        print(' \n \n The following differences in the away team could be detected: \n' +
              away_wrong_player.to_string())
elif home[0].empty or away[0].empty:
    print('The API lineup information for this match are not available yet!')
input('\n Press Enter to exit;')
