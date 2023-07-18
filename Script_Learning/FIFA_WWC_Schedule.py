import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import gspread
import ftputil
import os

# Import schedule.xml from FTP
server = "213.168.127.130"
user = "AlexTest"
password = "RobberyandLahm5%"
filename = '285026_schedule.xml'
f = open(filename, "w")
with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.chdir('FIFA/285026')
    ftp_host.open(filename)
    if ftp_host.path.isfile(filename):
        ftp_host.download(filename, filename)

# Create a schedule for FIFA WWC
# with open('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\women_schedule.xml') as fp:
#    data = BeautifulSoup(fp, 'xml')

directory = os.getcwd()
with open(
        directory + '\\285026_schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')

rounds = data.find_all('tournament-round')

# Create empty DF
season = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "League", "Stadium"])
# Get info for all matches and update DF
for j, round in enumerate(rounds):
    matchday = round["round-key"]
    fixtures = round.find_all("sports-event")
    for i, match in enumerate(fixtures):
        date = match.find("event-metadata")["start-date-time"][0:10]
        time = match.find("event-metadata")["start-date-time"][11:16]
        ko_date = (datetime.strptime(date + ' ' + time, "%Y-%m-%d %H:%M") + timedelta(hours=2)
                   ).strftime("%Y-%m-%d %H:%M")
        home = match.find_all("team")[0].find("team-metadata").find("name")["nickname"].encode("latin").decode("utf-8")
        away = match.find_all("team")[1].find("team-metadata").find("name")["nickname"].encode("latin").decode("utf-8")
        match_id = match.find("event-metadata")["event-key"]
        stadium = match.find("event-metadata").find("site").find("site-metadata").find("name")
        ["full"].encode("latin").decode("utf-8")

        match_info = {"Matchday": matchday, "MatchID": match_id, "KickOff": ko_date, "Home": home, "Away": away,
                      "League": "FIFA WWC", "Stadium": stadium}

        season = season.append(pd.DataFrame([match_info]))

# Push the schedule to the schedule sheet
gc = gspread.oauth(credentials_filename=
                   'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Script_Learning\\google_creds.json'
                   )

dispo_sheet = gc.open_by_key("14Dx1un2S9USaZX_5OyL2JALvxW4Fg18_OzJXaSuwYmc")
worksheet = dispo_sheet.worksheet("FIFA WWC")
worksheet.update([season.columns.values.tolist()] + season.values.tolist())