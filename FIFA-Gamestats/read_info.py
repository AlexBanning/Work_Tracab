import pandas as pd
import xml.etree.ElementTree as ET
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
corners = ET.SubElement(data, 'Freekicks')
freek = ET.SubElement(data, 'Freekicks')
offs = ET.SubElement(data, 'Offsides')
yell = ET.SubElement(data, 'YelloCards')
red = ET.SubElement(data, 'RedCards')
subs = ET.SubElement(data, 'Substitutions')

test = ET.tostring(data).decode('utf-8')

with open("test.xml", "wb") as f:
    f.write(ET.tostring(data))

a = ET.XML(test)