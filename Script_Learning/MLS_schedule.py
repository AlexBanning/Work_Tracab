from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


with open('C:\\Users\\tracab.CHYRONHEGO\\Documents\\PythonFun\\Script_Learning\\mls_schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')

# Get all matches
fixtures = data.find_all("Fixture")


date = fixtures[0]["PlannedKickoffTime"][0:10]
time = fixtures[0]["PlannedKickoffTime"][11:16]
kickoff = date + ' ' + time

test = datetime.strptime(kickoff, "%Y%m%d %H:%M")
date_object = datetime.strptime(date, '%Y-%m-%d').date()
time_object = datetime.strptime(time, "%H:%M").time()
home = fixtures[0]["HomeTeamName"]
away = fixtures[0]["GuestTeamName"]
match_id = fixtures[0]["DlProviderId"]
matchday = fixtures[0]["MatchDay"]
league = 'MLS'
stadium = fixtures[0]["StadiumName"]

league = 'MLS'
season = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
for i, match in enumerate(fixtures):
    date = match["PlannedKickoffTime"][0:10]
    time = match["PlannedKickoffTime"][11:16]
    kickoff = date + ' ' + time
    home = match["HomeTeamName"]
    away = match["GuestTeamName"]
    match_id = match["DlProviderId"]
    matchday = match["MatchDay"]
    stadium = match["StadiumName"]

    match_info = {"Matchday": matchday, "MatchID": match_id, "KickOff": kickoff, "Home": home, "Away": away,
                  "League": league, "Stadium": stadium}

    season = season.append(pd.DataFrame([match_info]))