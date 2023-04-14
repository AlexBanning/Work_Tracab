from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd


with open('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Script_Learning\\mls_schedule.xml') as fp:
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


# Get all matches
fixtures = data.find_all("Fixture")
# Define TimeSaving-Dates
dst_start = datetime.strptime('2023-03-26 02:00', '%Y-%m-%d %H:%M')
dst_end = datetime.strptime('2023-10-29 03:00', '%Y-%m-%d %H:%M')
# Define league
league = 'MLS'
# Create empty DF
season = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
# Get info for all matches and update DF
for i, match in enumerate(fixtures):
    date = match["PlannedKickoffTime"][0:10]
    time = match["PlannedKickoffTime"][11:16]
    kickoff = date + ' ' + time
    ko_date_object = datetime.strptime(kickoff, '%Y-%m-%d %H:%M')
    if dst_start < ko_date_object < dst_end:
        ko_date_object = ko_date_object + timedelta(hours=2)
    else:
        ko_date_object = ko_date_object + timedelta(hours=1)
    kickoff = ko_date_object.strftime('%Y-%m-%d %H:%M')
    home = match["HomeTeamName"]
    away = match["GuestTeamName"]
    match_id = match["DlProviderId"]
    matchday = match["MatchDay"]
    stadium = match["StadiumName"]

    match_info = {"Matchday": matchday, "MatchID": match_id, "KickOff": kickoff, "Home": home, "Away": away,
                  "League": league, "Stadium": stadium}

    season = season.append(pd.DataFrame([match_info]))