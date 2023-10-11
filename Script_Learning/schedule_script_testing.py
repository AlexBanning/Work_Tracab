from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from TracabModules.scheduleFunctions import get_schedule_xml as gs
import os
import ftputil

with open('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Script_Learning\\schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')

data = gs(filename="schedule.xml", ftp_dir="deltatre/MatchInfo/51/2023/schedule/")

with open('C:\\Users\\a.banning\\PycharmProjects\\Work_Tracab\\schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')

# Get division
league_name = data.find_all("sports-content-code")[1]["code-name"]
division = data.find("tournament-division-metadata")["division-key"]
league = division + "." + league_name
# Get all matchdays
rounds = data.find_all("tournament-round")

# Get round_id
round_id = rounds[0]["round-number"]

# Get all matches from a matchday
sports_event = rounds[0].contents[1::2]

# Get matchID
matchId = sports_event[0].contents[1]["event-key"]

# Get hometeam
home = sports_event[0].contents[3].contents[1].contents[1]["full"].encode("latin").decode("utf-8")

# Get awayteam
away = sports_event[0].contents[5].contents[1].contents[1]["full"].encode("latin").decode("utf-8")

# Get stadium
stadium = sports_event[0].contents[1].contents[1].contents[1].contents[1]["full"].encode("latin").decode("utf-8")

# Get date and KO time
# year = sports_event[0].contents[1]["start-date-time"][0:4]
# month = sports_event[0].contents[1]["start-date-time"][4:6]
# day = sports_event[0].contents[1]["start-date-time"][6:8]

date = sports_event[0].contents[1]["start-date-time"][0:4] + "-" + sports_event[0].contents[1]["start-date-time"][4:6] \
       + "-" + sports_event[0].contents[1]["start-date-time"][6:8]

# h = sports_event[0].contents[1]["start-date-time"][-11:-9]
# min = sports_event[0].contents[1]["start-date-time"][-9:-7]

ko = sports_event[0].contents[1]["start-date-time"][-11:-9] + ":" \
         + sports_event[0].contents[1]["start-date-time"][-9:-7]

KO_date = date + " " + ko

match = {"Matchday": round_id, "MatchID": matchId, "KickOff": KO_date, "Home": home, "Away": away,
         "League": league, "Stadium": stadium}



# Get division
league_name = data.find_all("sports-content-code")[1]["code-name"]
division = data.find("tournament-division-metadata")["division-key"]
league = division + "." + league_name

# Get all matchdays
rounds = data.find_all("tournament-round")

# Create a DF containing all matches of a complete season
season = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
# Iterate the whole season
for i, round in enumerate(rounds):
    round_id = i+1
    matchday = []
    # Get match specific information
    for j, match in enumerate(round.contents[1::2]):
        matchId = match.contents[1]["event-key"]
        home = match.contents[3].contents[1].contents[1]["full"].encode("latin").decode("utf-8")
        away = match.contents[5].contents[1].contents[1]["full"].encode("latin").decode("utf-8")
        stadium = match.contents[1].contents[1].contents[1].contents[1]["full"].encode("latin").decode("utf-8")
        date = match.contents[1]["start-date-time"][0:4] + "-" \
               + match.contents[1]["start-date-time"][4:6] + "-" \
               + match.contents[1]["start-date-time"][6:8]
        ko = match.contents[1]["start-date-time"][9:11] + ":" \
             + match.contents[1]["start-date-time"][11:13]
        ko_date = date + " " + ko
        match_info = {"Matchday": round_id, "MatchID": matchId, "KickOff": ko_date, "Home": home, "Away": away,
                      "League": league, "Stadium": stadium}
        matchday.append(match_info)
    md_df = pd.DataFrame(matchday)
    season = pd.concat([season, md_df])

# Test for Opta
comp_id = 9
season_id = 2023

# Check whether the files already exist and if yes, delete them beforehand
if os.path.isfile("srml-" + str(comp_id) + "-" + str(season_id) + "-results.xml"):
    os.remove("srml-" + str(comp_id) + "-" + str(season_id) + "-results.xml")
if os.path.isfile("srml-" + str(comp_id) + "-" + str(season_id) + "-squads.xml"):
    os.remove("srml-" + str(comp_id) + "-" + str(season_id) + "-squads.xml")

# Download schedule
gs(comp_id=9, season_id=2023, vendor='Opta')

# Open schedule
with open('C:\\Users\\a.banning\\PycharmProjects\\Work_Tracab\\srml-' + str(comp_id) + '-2023-results.xml',
          encoding='utf8') as fp_s:
    schedule_data = BeautifulSoup(fp, 'xml')

# Open team info
with open('C:\\Users\\a.banning\\PycharmProjects\\Work_Tracab\\srml-' + str(comp_id) + '-2023-squads.xml',
          encoding='utf8') as fp_t:
    team_data = BeautifulSoup(fp, 'xml')



# Create dictionary to link team_name and team_id
teams = team_data.find_all('Team')
team_names = [x.find('Name').text for x in teams]
team_ids = [x['uID'] for x in teams]
team_dict = dict(zip(team_ids, team_names))

# Create schedule
matches = schedule_data.find_all('MatchData')
md = [x.find('MatchInfo')['MatchDay'] for x in matches]
match_ids = [x['uID'][1:] for x in matches]
dates = [x.find('MatchInfo').find('Date').text for x in matches]
stadiums = [x.find('Stat').text for x in matches]
home_teams = [team_dict[x.find_all('TeamData')[0]['TeamRef']] for x in matches]
away_teams = [team_dict[x.find_all('TeamData')[1]['TeamRef']] for x in matches]
league = ['Eredivisie' for i in range(0,306)]

schedule = pd.DataFrame(list(zip(md, match_ids, dates, home_teams, away_teams, league, stadiums)))

# Test for Keytoq
ftp_dir = 'Keytoq/MatchInfo/'
filename= 'main.xml'
server = "213.168.127.130"
user = "Alex_Test"
password = "RobberyandLahm5%"
# filename = '../285026_schedule.xml'
f = open(filename, "w")
with ftputil.FTPHost(server, user, password) as ftp_host:
    # ftp_host.chdir('FIFA/285026')
    ftp_host.chdir(ftp_dir)
    ftp_host.open(filename)
    if ftp_host.path.isfile(filename):
        ftp_host.download(filename, filename)

with open('C:\\Users\\a.banning\\PycharmProjects\\Work_Tracab\\main.xml',
          encoding='utf8') as fp:
    schedule_data = BeautifulSoup(fp, 'xml')

matchdays = schedule_data.find_all('round')
matches = [x.find_all('match') for x in schedule_data.find_all('round').content()]

season = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
for i, md in enumerate(matches):
    ko_date = [x['date'] + '' + x['time'] for x in md]
    home = [x['team_a'] for x in md]
    away = [x['team_b'] for x in md]
    matchId = [x['id'] for x in md]
    league = ['Ekstraklasa' for x in md]
    round_id = [str((i+1)) for x in md]

    match_info = pd.DataFrame({"Matchday": round_id, "MatchID": matchId, "KickOff": ko_date, "Home": home, "Away": away,
                  "League": league})
    season = pd.concat([season, match_info])



gs(comp_id= 285026, season_id=2023, vendor='FIFA')

test = "Bayern München"

new = test.encode('latin').decode('latin')