import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import gspread
from TracabModules import gamestatsFunctions as gf
import os
import ftputil

# Create a schedule DF
schedule = pd.read_excel(
    'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\schedule.xlsx')

new_schedule = schedule[['KickOffMoment', 'IfesMatchNumber', 'IfesMatchId', 'IfesMatchShortName']]

# Create a player database with information to all players of each team
players = pd.read_excel(
    'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\players.xlsx')
players = players[['Team', 'Shirt Nr', 'Last Name as in Passport', 'First Name as in Passport', 'IFES ID']]
# Create a referee database with information to all match officials
refs = pd.read_excel(
    'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\referees.xlsx')

# Create a team officials database with information to all officials of each team
t_officials = pd.read_excel(
    'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\teamOfficials.xlsx')

player_db = []
nations = players['Team'].unique().tolist()
# Remove the last values which are no nations
nations.pop()

# Create a list with all 3-Letter-Codes
tlc = ['ARG', 'BRA', 'COL', 'DOM', 'ECU', 'ENG', 'FIJ', 'FRA', 'GAM', 'GUA', 'HON', 'IRQ', 'ISR', 'ITA', 'JPN',
       'KOR', 'NZL', 'NGA', 'SEN', 'SVK', 'TUN', 'URU', 'USA', 'UZB']

# Create a dict with 3-letter codes and corresponding team names
nations_dict = {}
for i, nation in enumerate(nations):
    team_tlc = tlc[i]
    team_dict = {team_tlc: nation}
    nations_dict.update(team_dict)

# Fetch the teams that play against each other and create dataframes with their players
fixtures = [x for x in new_schedule['IfesMatchShortName']]

home = nations_dict[fixtures[0][0:3]]
away = nations_dict[fixtures[0][6:]]

home_team = players[players['Team']==home]
away_team = players[players['Team']==away]

# Testing to recreate our gamestats in the correct format and syntax
tree = ET.parse(
    'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\Gamestats.xml'
)
root = tree.getroot()
teams = tree.findall('Team')
home = teams[0]

home_players = home.find('Roster').findall('Player')

data = ET.Element('Hego')
data.set('iGameNumber', '12345')
data.set('dtGameBegin', '2023-06-01 15:30:00')
data.set('sRoundDescription', 'Round_1')
data.set('iRoundId', '1')
data.set('iCompetitionId', '54321')
data.set('iSpectators', '54076')
data.set('iSeasonId', '2023')
data.set('iVendorId', '4')
data.set('sStadium', 'Borussia Park')
data.set('iStadiumId', '1900')
data.set('iRefereeId', '31')
htt = ET.SubElement(data, 'Team')
hroster = ET.SubElement(htt, 'Roster')
for player in home_team.iterrows():
    print(player)
     i = ET.SubElement(hroster, 'Player')
     hroster.set('iJerseyNo', player['Shirt Nr'])
     hroster.set('iId', player['IFES ID'])
     hroster.set('iLastName', player['Last Name as in Passport'])
     hroster.set('iFirstName', player['First Name as in Passport'])
     hroster.set('iShortName', ' ')

hlineup = ET.SubElement(htt, 'Lineup')
att = ET.SubElement(data, 'Team')
aroster = ET.SubElement(att, 'Roster')
alineup = ET.SubElement(att, 'Lineup')
gstats = ET.SubElement(data, 'Gamestats')
ref = ET.SubElement(data, 'Team')
goals = ET.SubElement(data, 'Goals')
shots = ET.SubElement(data, 'Shots')
corners = ET.SubElement(data, 'Corners')
freek = ET.SubElement(data, 'Freekicks')
offs = ET.SubElement(data, 'Offsides')
yell = ET.SubElement(data, 'YellowCards')
red = ET.SubElement(data, 'RedCards')
subs = ET.SubElement(data, 'Substitutions')

test = ET.tostring(data).decode('utf-8')

with open("test.xml", "wb") as f:
    f.write(ET.tostring(data))

a = ET.XML(test)


# Tests for FIFA WWC


# Get schedule xml from FTP
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

# Create schedule for google sheet for FIFA WWC
# Path on home computer
with open('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\women_schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')

# Path on laptop
with open(
        'C:\\Users\\tracab.CHYRONHEGO\\Documents\\PythonFun\\285026_schedule.xml') as fp:
    data = BeautifulSoup(fp, 'xml')


# Get all rounds of tournament
rounds = data.find_all('tournament-round')

# Create empty DF
schedule = pd.DataFrame(columns=["Matchday", "MatchID", "KickOff", "Home", "Away", "hID", "aID", "League", "Stadium"])
# Get info for all matches and update DF
for j, round in enumerate(rounds):
    matchday = round['round-key']
    fixtures = round.find_all("sports-event")
    for i, match in enumerate(fixtures):
        date = match.find('event-metadata')["start-date-time"][0:10]
        time = match.find('event-metadata')["start-date-time"][11:16]
        # Adjust kickoff time from GMT to CET summer time
        ko_date = (datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M') + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')
        home = match.find_all('team')[0].find('team-metadata').find('name')["nickname"].encode("latin").decode("utf-8")
        home_id = match.find_all('team')[0].find('team-metadata')["team-key"]
        away = match.find_all('team')[1].find('team-metadata').find('name')["nickname"].encode("latin").decode("utf-8")
        away_id = match.find_all('team')[1].find('team-metadata')["team-key"]
        match_id = match.find('event-metadata')["event-key"]
        stadium = match.find('event-metadata').find('site').find('site-metadata').find('name')['full'].encode("latin").decode("utf-8")

        match_info = {"Matchday": matchday, "MatchID": match_id, "KickOff": ko_date, "Home": home, "Away": away,
                      "hID": home_id, "aID": away_id, "League": "FIFA WWC", "Stadium": stadium}

        schedule = schedule.append(pd.DataFrame([match_info]))

# Push the schedule to the schedule sheet
gc = gspread.oauth(credentials_filename=
                   'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Script_Learning\\google_creds.json'
                   )

dispo_sheet = gc.open_by_key("14Dx1un2S9USaZX_5OyL2JALvxW4Fg18_OzJXaSuwYmc")
worksheet = dispo_sheet.worksheet("FIFA WWC")
worksheet.update([schedule.columns.values.tolist()] + schedule.values.tolist())

# Create a DF with all players from all teams
players = pd.read_excel(
    'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\women_players.xlsx')
players = players[['Team', 'Shirt Nr', 'Last Name as in Passport', 'First Name as in Passport', 'IFES Player ID']]

# Create list of series with all players from a team
home_team = 'Argentina'
away_team = 'Germany'

hteam_players = [x[1] for x in players.iterrows() if x[1]['Team'] == home_team]
ateam_players = [x[1] for x in players.iterrows() if x[1]['Team'] == away_team]


# Function to write schedule DF, player DF and gamestats for all scheduled matches
league = 'FIFA WWC'
os.chdir('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA WWC')
schedule = gf.get_schedule(file=
                'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\women_schedule.xml',
                league='FIFA WWC')
players = gf.get_players(file=
               'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\FIFA-Gamestats\\tournamentInfo\\women_players.xlsx')
os.chdir('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\' + league)
gf.write_gamestats(schedule=schedule, players=players, comp_iD='285026', season_iD='2023', vendor_iD='15')

