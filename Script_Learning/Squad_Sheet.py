import xml.etree.ElementTree as ET
import os
import gspread

import pandas as pd

# BL1
path = r'\\10.49.0.250\deltatre\MatchInfo\51\2023\team_players'

testfile = r'C:\Users\a.banning\Desktop\team_players_bl1\team_players_10.xml'
squads = pd.DataFrame(columns=['TeamID', 'TeamName', 'PlayerID', 'Jersey#', 'Playername', '# Name'])
for squad in os.listdir(path):
    print(squad)
    tree = ET.parse(path + '\\' + squad)
    root = tree.getroot()
    for player in root[1][1].findall('player'):
        name = player.find('player-metadata').find('name').attrib['nickname']
        nr_name = '#' + str(player.find('player-metadata').attrib['uniform-number']) + ' ' + str(name)
        jersey_nr = str(player.find('player-metadata').attrib['uniform-number'])
        player_id = str(player.find('player-metadata').attrib['player-key'])
        team_id = root[1][1].find('team-metadata').attrib['team-key']
        team_name = root[1][1].find('team-metadata').find('name').attrib['full']

        player_dict = {'TeamID': team_id, 'TeamName': team_name, 'PlayerID': player_id, 'Jersey#': jersey_nr,
                       'Playername': name, '# Name': nr_name}

        squads = pd.concat([squads, pd.DataFrame(player_dict, index=[0])], ignore_index=True)

# BL2
path = r'\\10.49.0.250\deltatre\MatchInfo\52\2023\team_players'

squads = pd.DataFrame(columns=['TeamID', 'TeamName', 'PlayerID', 'Jersey#', 'Playername', '# Name'])
for squad in os.listdir(path):
    tree = ET.parse(path + '\\' + squad)
    root = tree.getroot()
    for player in root[1][1].findall('player'):
        name = player.find('player-metadata').find('name').attrib['nickname']
        nr_name = '#' + str(player.find('player-metadata').attrib['uniform-number']) + ' ' + str(name)
        jersey_nr = str(player.find('player-metadata').attrib['uniform-number'])
        player_id = str(player.find('player-metadata').attrib['player-key'])
        team_id = root[1][1].find('team-metadata').attrib['team-key']
        team_name = root[1][1].find('team-metadata').find('name').attrib['full']

        player_dict = {'TeamID': team_id, 'TeamName': team_name, 'PlayerID': player_id, 'Jersey#': jersey_nr,
                       'Playername': name, '# Name': nr_name}

        squads = pd.concat([squads, pd.DataFrame(player_dict, index=[0])], ignore_index=True)

# MLS

path = r'\\10.49.0.250\d3_mls\MatchInfo'
squads = pd.DataFrame(columns=['TeamName', 'PlayerID', 'Jersey#', 'Playername', '# Name'])
for i, filename in enumerate(os.listdir(path)):
    if not filename.endswith('MLS-SEA-0001K8_player.xml'): continue
    tree = ET.parse(path + '\\' + filename)
    root = tree.getroot()
    players = root.find('Objects').findall('Object')
    for player in players:
        try:
            f_name = str(player.attrib['FirstName'][0]) + '.'
        except KeyError:
            f_name = 'N/A'
        try:
            l_name = str(player.attrib['LastName'])
        except KeyError:
            l_name = 'N/A'
        name = f_name + ' ' + l_name
        try:
            nr_name = '#' + str(player.attrib['ShirtNumber']) + ' ' + str(name)
        except KeyError:
            nr_name = 'N/A'
        try:
            jersey_nr = str(player.attrib['ShirtNumber'])
        except KeyError:
            jersey_nr = 'N/A'
        try:
            player_id = str(player.attrib['DlProviderId'])
        except KeyError:
            player_id = 'N/A'
        try:
            team_name = str(player.attrib['ClubName'])
        except KeyError:
            team_name = 'N/A'

        player_dict = {'TeamName': team_name, 'PlayerID': player_id, 'Jersey#': jersey_nr,
                       'Playername': name, '# Name': nr_name}

        squads = pd.concat([squads, pd.DataFrame(player_dict, index=[0])], ignore_index=True)

# Push squad to 23/24 Squads-Sheet
os.chdir("N:\\07_QC\\Scripts\\Schedule_script\\Season23-24")
gc = gspread.oauth(credentials_filename=
                   'schedule_push_authentification.json'
                   )

schedule_sheet = gc.open_by_key("1Og0bflU81tYhj-l-B7WhNGlOe6BLl7OWJVzH79K152o")
try:
    worksheet = schedule_sheet.worksheet('MLS')
except gspread.WorksheetNotFound:
    schedule_sheet.add_worksheet(title='MLS', rows=1000, cols=15)
worksheet = schedule_sheet.worksheet('MLS')
worksheet.update([squads.columns.values.tolist()] + squads.values.tolist())
