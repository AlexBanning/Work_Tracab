import pandas as pd
from IPython.display import display
from requests.structures import CaseInsensitiveDict
import TracabModules.External.apiFunctions as af
from bs4 import BeautifulSoup
import requests
import string
import ftputil

login_url = 'https://data.voetbaldatacentre.nl/api/login'
creds = '{"username": "chryonhego@archimedict.nl", "password": "34$h$kKs8y9Gqadp"}'
token = af.get_token(login_url, creds)
headers = CaseInsensitiveDict()
headers['accept'] = 'application/json'
headers['Authorization'] = "Bearer " + token
# Select the match of interest
matchday_url = 'https://data.voetbaldatacentre.nl/av/api/matches/33'
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
today = '2023-08-19'
match_id = [x['uID'][1:] for x in matches_schedule if x.find('MatchInfo').find('Date').text[0:10] == today and
            str(x.find('TeamData')['TeamRef']) == tId][0]

# date.today().strftime('%Y-%m-%d')

# Get lineup infos from eredivisie and from tracab gamestats
lineups = af.get_both_lineups(token, md_info[choice - 1]['matchNumber'], match_id)

home = pd.concat([lineups[0], lineups[1]], axis=1)
print('Home Team')
display(home.to_string())
away = pd.concat([lineups[2], lineups[3]], axis=1)
print(' \n \n Away Team')
display(home.to_string())
input('Press Enter to Exit;')